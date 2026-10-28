# AI Resume Analyzer & Personalized Interview Assistant

![Resume Upload](screenshots/resume-analyzer-01-upload.png)

![Resume Analysis](screenshots/resume-analyzer-02-analysis.png)

![Recommended Job Roles](screenshots/resume-analyzer-03-recommended-roles.png)

![Personalized Interview](screenshots/resume-analyzer-04-interview.png)

<p align="center">
  <strong>LangGraph | Groq | Python | Pydantic | Streamlit | Generative AI</strong>
</p>

<p align="center">
  An AI-powered career preparation application that analyzes resumes, recommends suitable job roles, and conducts personalized technical interviews.
</p>

---

## Project Overview

**AI Resume Analyzer & Personalized Interview Assistant** is an AI-powered application built to help candidates understand their professional profiles, discover suitable job roles, identify skill gaps, and practise technical interviews using their own resumes.

The application accepts a text-based PDF resume and uses a language model to extract candidate information, including skills, education, experience, and projects. Based on this analysis, it recommends relevant job roles and estimates how closely the resume aligns with each role.

After selecting a role, the candidate receives five personalized interview questions. Each answer is evaluated by the AI interviewer, which provides a score, technical feedback, strengths, improvement suggestions, and an example of a stronger answer.

The application combines **LangGraph workflow orchestration, Groq LLM inference, Pydantic structured outputs, and Streamlit** to deliver an interactive interview preparation experience.

## Key Features

- **PDF Resume Upload:** Upload a text-based PDF resume directly through the interface.
- **AI Resume Analysis:** Extract skills, education, experience, projects, and a professional summary.
- **Job Role Recommendations:** Generate relevant job roles based on the candidate's resume.
- **Resume Match Estimation:** Display an estimated match percentage for each recommended role.
- **Role Suitability Explanation:** Understand why a role may fit the candidate's profile.
- **Skill Gap Identification:** Discover additional skills worth building for a target role.
- **Project-Based Recommendations:** Identify projects relevant to recommended positions.
- **Personalized Interview:** Generate five interview questions for the selected role.
- **Adaptive Interview Context:** Use resume information and project references to personalize questions.
- **AI Answer Evaluation:** Evaluate answers for correctness, relevance, clarity, and depth.
- **Constructive Feedback:** Show strengths, improvement areas, and example answers.
- **Interview Progress Tracking:** Track question progress through a visual progress bar.
- **Performance Report:** Calculate total and average interview scores.
- **Report Download:** Download the final interview report as a text file.
- **Session Management:** Start a fresh workflow using the Start Over option.

## Problem Statement

Candidates frequently prepare for technical interviews using generic question lists that do not reflect their own projects, technical skills, or professional background.

They may also struggle to determine which job roles suit their current profile and which skills they should improve before applying.

This project addresses these challenges by connecting resume analysis, role recommendations, skill-gap identification, and personalized interview practice in a single application.

## Project Objectives

- Extract meaningful information from PDF resumes.
- Generate a structured overview of the candidate's background.
- Recommend suitable job roles based on resume evidence.
- Explain the reasoning behind role recommendations.
- Identify skills that candidates could develop further.
- Generate five personalized interview questions for a selected role.
- Evaluate candidate answers and provide actionable feedback.
- Calculate interview performance scores.
- Generate a downloadable interview report.

## Application Screenshots

### 1. Resume Upload

The candidate uploads a text-based PDF resume and starts the analysis process.

![Resume Upload Interface](screenshots/resume-analyzer-01-upload.png)

### 2. Resume Analysis

The application displays the candidate summary, skills, education, experience, and projects extracted from the resume.

![Resume Analysis Results](screenshots/resume-analyzer-02-analysis.png)

### 3. Recommended Job Roles

The application displays recommended positions with estimated resume-match percentages, supporting reasons, skills to consider building, and relevant projects.

![Recommended Job Roles](screenshots/resume-analyzer-03-recommended-roles.png)

### 4. Personalized Interview

The candidate answers five role-specific questions and receives AI-generated evaluation and feedback after submitting each answer.

![Personalized Interview](screenshots/resume-analyzer-04-interview.png)

---

## End-to-End Workflow

```text
                 PDF Resume
                     |
                     v
              Upload Resume
                     |
                     v
              Load Resume PDF
                     |
                     v
             Extract Resume Text
                     |
                     v
              Analyze Resume
                     |
                     v
            Recommend Job Roles
                     |
                     v
            Select Target Role
                     |
                     v
          Generate Five Questions
                     |
                     v
            Answer Each Question
                     |
                     v
             Evaluate Answers
                     |
                     v
            Calculate Scores
                     |
                     v
           Generate Final Report
                     |
                     v
           Download Interview Report
