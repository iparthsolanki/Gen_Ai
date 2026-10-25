import tempfile
from pathlib import Path

import streamlit as st

from main import (
    llm,
    load_resume_node,
    analyze_resume_node,
    recommend_roles_node,
    generate_questions_node,
    AnswerEvaluation,
)

st.set_page_config(
    page_title="AI Resume Analyzer & Interview Assistant",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 AI Resume Analyzer & Personalized Interview Assistant")
st.caption("LangGraph + Groq | Resume-based role recommendations and a personalized 5-question interview")

DEFAULTS = {
    "resume_path": None,
    "resume_text": "",
    "resume_analysis": None,
    "role_recommendations": [],
    "selected_role": None,
    "interview_questions": [],
    "current_question": 0,
    "answers": [],
    "evaluations": [],
    "interview_complete": False,
    "final_report": "",
    "show_feedback": False,
    "uploaded_signature": None,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_session():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


def evaluate_answer(question_data, answer):
    evaluator = llm.with_structured_output(AnswerEvaluation)
    prompt = f"""
You are a fair technical interviewer evaluating an answer for the role
{st.session_state.selected_role['role']}.
Score from 0 to 10 based on correctness, relevance, clarity, and depth.
Be constructive. If the answer is blank or skipped, score 0.
Do not invent candidate experience or assume details not provided.

Candidate resume analysis:
{st.session_state.resume_analysis}

Question:
{question_data['question']}
Focus area:
{question_data.get('focus_area', 'General')}
Candidate answer:
{answer if answer.strip() else 'No answer provided.'}

Return a technically sound concise sample answer and specific feedback.
"""
    return evaluator.invoke(prompt).model_dump()


with st.sidebar:
    st.header("Project workflow")
    st.markdown(
        "1. Upload resume PDF\n2. Analyze resume\n3. Review suggested roles\n"
        "4. Select a role\n5. Answer 5 questions\n6. View report"
    )
    if st.button("🔄 Start over", use_container_width=True):
        reset_session()
        st.rerun()

st.subheader("1. Upload your resume")
uploaded_file = st.file_uploader("Choose a text-based PDF resume", type=["pdf"])

if uploaded_file is not None:
    signature = (uploaded_file.name, uploaded_file.size)
    if st.session_state.uploaded_signature != signature:
        # Clean up the previous temporary PDF, if one exists.
        old_path = st.session_state.resume_path
        if old_path:
            try:
                Path(old_path).unlink(missing_ok=True)
            except OSError:
                pass
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            st.session_state.resume_path = tmp.name
        st.session_state.uploaded_signature = signature
        # Reset all downstream results for the new file.
        for key in ["resume_text", "resume_analysis", "role_recommendations", "selected_role",
                    "interview_questions", "current_question", "answers", "evaluations",
                    "interview_complete", "final_report", "show_feedback"]:
            st.session_state[key] = DEFAULTS[key]

    st.success(f"Uploaded: {uploaded_file.name}")
    if st.button("Analyze resume", type="primary"):
        try:
            with st.spinner("Reading resume and analyzing skills, education, experience, and projects..."):
                loaded = load_resume_node({"resume_path": st.session_state.resume_path})
                st.session_state.resume_text = loaded["resume_text"]
                analysis_result = analyze_resume_node({"resume_text": st.session_state.resume_text})
                st.session_state.resume_analysis = analysis_result["resume_analysis"]
                roles_result = recommend_roles_node({
                    "resume_text": st.session_state.resume_text,
                    "resume_analysis": st.session_state.resume_analysis,
                })
                st.session_state.role_recommendations = roles_result["role_recommendations"]
            st.success("Resume analysis complete!")
        except Exception as exc:
            st.error(f"Could not analyze resume: {type(exc).__name__}: {exc}")
            st.info("Check GROQ_API_KEY, model access, internet connection, and whether the PDF contains selectable text.")

if st.session_state.resume_analysis:
    analysis = st.session_state.resume_analysis
    st.divider()
    st.subheader("2. Resume analysis")
    st.write(analysis.get("summary", ""))
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Skills**")
        st.write(", ".join(analysis.get("skills", [])) or "No skills found in the resume.")
        st.markdown("**Education**")
        st.markdown("\n".join(f"- {x}" for x in analysis.get("education", [])) or "No education details found.")
    with col2:
        st.markdown("**Experience**")
        st.markdown("\n".join(f"- {x}" for x in analysis.get("experience", [])) or "No experience details found.")
        st.markdown("**Projects**")
        st.markdown("\n".join(f"- {x}" for x in analysis.get("projects", [])) or "No projects found.")

    st.divider()
    st.subheader("3. Recommended job roles")
    roles = st.session_state.role_recommendations
    for idx, role in enumerate(roles, start=1):
        with st.expander(f"{idx}. {role['role']} — estimated resume match {role['match_percentage']}%"):
            st.markdown("**Why this role may fit**")
            st.markdown("\n".join(f"- {x}" for x in role.get("reasons", [])) or "No supporting reasons returned.")
            st.markdown("**Skills to consider building**")
            st.write(", ".join(role.get("missing_skills", [])) or "No additional skills identified.")
            st.markdown("**Relevant projects**")
            st.markdown("\n".join(f"- {x}" for x in role.get("relevant_projects", [])) or "No directly relevant project identified.")

    role_names = [r["role"] for r in roles]
    if roles and st.session_state.selected_role is None:
        chosen_role_name = st.selectbox("Choose the role you want to practise for", role_names)
        if st.button("Start personalized interview", type="primary"):
            selected = next(r for r in roles if r["role"] == chosen_role_name)
            try:
                with st.spinner(f"Creating five questions for {chosen_role_name} using your resume and projects..."):
                    q_result = generate_questions_node({
                        "selected_role": selected,
                        "resume_analysis": analysis,
                        "resume_text": st.session_state.resume_text,
                    })
                st.session_state.selected_role = selected
                st.session_state.interview_questions = q_result["interview_questions"]
                st.session_state.current_question = 0
                st.session_state.answers = [""] * 5
                st.session_state.evaluations = []
                st.session_state.interview_complete = False
                st.session_state.show_feedback = False
                st.rerun()
            except Exception as exc:
                st.error(f"Could not create interview questions: {type(exc).__name__}: {exc}")

if st.session_state.selected_role and st.session_state.interview_questions and not st.session_state.interview_complete:
    st.divider()
    st.subheader(f"4. Personalized interview — {st.session_state.selected_role['role']}")
    q_index = st.session_state.current_question
    questions = st.session_state.interview_questions
    q = questions[q_index]
    st.progress((q_index + 1) / 5)
    st.markdown(f"**Question {q_index + 1} of 5**")
    st.caption(f"{q.get('difficulty', 'Mixed')} difficulty · Focus: {q.get('focus_area', 'General')}")
    if q.get("project_reference"):
        st.caption(f"Resume reference: {q['project_reference']}")
    st.markdown(f"### {q['question']}")

    answer = st.text_area(
        "Your answer",
        key=f"answer_{q_index}",
        height=160,
        placeholder="Type your answer here. Explain your approach, reasoning, and examples.",
    )
    if st.button("Submit answer & get feedback", type="primary", key=f"submit_{q_index}"):
        try:
            with st.spinner("Evaluating your answer..."):
                evaluation = evaluate_answer(q, answer)
            evaluation["question"] = q["question"]
            evaluation["focus_area"] = q.get("focus_area", "General")
            evaluation["candidate_answer"] = answer if answer.strip() else "No answer provided."
            if len(st.session_state.evaluations) == q_index:
                st.session_state.evaluations.append(evaluation)
            else:
                st.session_state.evaluations[q_index] = evaluation
            st.session_state.answers[q_index] = answer
            st.session_state.show_feedback = True
            st.rerun()
        except Exception as exc:
            st.error(f"Could not evaluate answer: {type(exc).__name__}: {exc}")

    if st.session_state.show_feedback and len(st.session_state.evaluations) > q_index:
        ev = st.session_state.evaluations[q_index]
        st.metric("Score", f"{ev['score']}/10")
        st.write(ev.get("correctness", ""))
        with st.expander("What you did well", expanded=True):
            st.markdown("\n".join(f"- {x}" for x in ev.get("strengths", [])) or "No strengths listed.")
        with st.expander("How to improve", expanded=True):
            st.markdown("\n".join(f"- {x}" for x in ev.get("improvements", [])) or "No improvements listed.")
        with st.expander("Example stronger answer"):
            st.write(ev.get("sample_answer", ""))

        if q_index < 4:
            if st.button("Next question →", type="primary", key=f"next_{q_index}"):
                st.session_state.current_question += 1
                st.session_state.show_feedback = False
                st.rerun()
        else:
            if st.button("Finish interview & generate report", type="primary"):
                results = st.session_state.evaluations
                total = sum(item["score"] for item in results)
                average = total / len(results) if results else 0
                strengths = [x for item in results for x in item.get("strengths", [])]
                improvements = [x for item in results for x in item.get("improvements", [])]
                report_lines = [
                    "AI RESUME ANALYZER — FINAL INTERVIEW REPORT",
                    "=" * 48,
                    f"Target role: {st.session_state.selected_role['role']}",
                    f"Estimated resume match: {st.session_state.selected_role['match_percentage']}%",
                    f"Interview score: {total}/50 ({average:.1f}/10 average)",
                    "", "QUESTION-WISE RESULTS:",
                ]
                for i, item in enumerate(results, 1):
                    report_lines.extend([
                        f"\n{i}. {item['question']}",
                        f"Score: {item['score']}/10",
                        f"Evaluation: {item.get('correctness', '')}",
                        f"Your answer: {item.get('candidate_answer', '')}",
                        f"Example stronger answer: {item.get('sample_answer', '')}",
                    ])
                report_lines.extend(["\nSTRENGTHS:"] + [f"- {x}" for x in strengths])
                report_lines.extend(["\nAREAS TO IMPROVE:"] + [f"- {x}" for x in improvements])
                report_lines.append("\nNote: AI-generated practice feedback, not a hiring decision.")
                st.session_state.final_report = "\n".join(report_lines)
                Path("interview_report.txt").write_text(st.session_state.final_report, encoding="utf-8")
                st.session_state.interview_complete = True
                st.rerun()

if st.session_state.interview_complete:
    st.divider()
    st.subheader("5. Final interview report")
    total = sum(item["score"] for item in st.session_state.evaluations)
    average = total / len(st.session_state.evaluations) if st.session_state.evaluations else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Total score", f"{total}/50")
    c2.metric("Average", f"{average:.1f}/10")
    c3.metric("Target role", st.session_state.selected_role["role"])
    st.text_area("Report", st.session_state.final_report, height=400)
    st.download_button(
        "⬇️ Download interview report",
        data=st.session_state.final_report,
        file_name="interview_report.txt",
        mime="text/plain",
    )

st.caption("Resume-role match percentages are AI estimates, not hiring probabilities. Avoid uploading sensitive information you do not want processed.")
