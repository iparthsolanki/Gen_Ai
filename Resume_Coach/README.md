# AI Resume Analyzer & Personalized Interview Assistant

![Resume Upload](screenshots/01-resume-upload.png)

![Resume Analysis](screenshots/02-resume-analysis.png)

![Recommended Job Roles](screenshots/03-recommended-roles.png)

![Personalized Interview](screenshots/04-personalized-interview.png)

<p align="center">
  <strong>LangGraph | Groq | Python | Pydantic | Streamlit | Generative AI</strong>
</p>

---

## Overview

AI Resume Analyzer & Personalized Interview Assistant is an AI-powered career preparation application that analyzes a candidate's resume, recommends suitable job roles, and conducts a personalized technical interview based on the selected role.

The application uses LangGraph to organize the workflow and Groq-hosted LLM inference to extract resume information, identify relevant job opportunities, generate interview questions, and evaluate candidate answers.

The goal is to make interview preparation more personalized by connecting resume skills, projects, experience, and job requirements in a single workflow.

## Key Features

- PDF resume upload and text extraction
- AI-powered resume analysis
- Structured extraction of skills, education, experience, and projects
- Resume-based job role recommendations
- Estimated resume match percentage for recommended roles
- Explanation of role suitability
- Identification of potential skill gaps
- Project-specific interview questions
- Five personalized interview questions per selected role
- Answer evaluation with scores from 0 to 10
- Feedback on technical correctness, strengths, and improvements
- Sample answers for learning and practice
- Final interview report with total and average scores
- Automatic saving of the report to `interview_report.txt`

## Problem Statement

Candidates often prepare for interviews using generic questions that may not reflect their actual skills, projects, or target roles.

They may also struggle to identify suitable job opportunities and understand which skills they should improve before applying.

This project addresses these challenges by combining resume analysis, role recommendations, skill-gap identification, and personalized interview practice.

## Project Objectives

- Extract structured information from PDF resumes.
- Understand a candidate's technical skills and experience.
- Recommend relevant entry-level or experienced job roles.
- Explain why each recommended role may fit the candidate.
- Identify common role skills that are not evident in the resume.
- Generate interview questions tailored to the selected role.
- Evaluate answers using AI-generated feedback.
- Provide sample answers to support learning.
- Generate a consolidated interview performance report.

## Application Workflow

```text
        PDF Resume
            |
            v
    Load Resume with PyPDFLoader
            |
            v
     Analyze Resume with LLM
            |
            v
   Recommend Relevant Job Roles
            |
            v
     Candidate Selects a Role
            |
            v
 Generate Five Interview Questions
            |
            v
    Candidate Answers Questions
            |
            v
     Evaluate Each Answer
            |
            v
  Calculate Interview Performance
            |
            v
    Generate Final Report
            |
            v
    Save interview_report.txt
