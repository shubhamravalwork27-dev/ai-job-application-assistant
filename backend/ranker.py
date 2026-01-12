import json
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="mistral")

RANKING_PROMPT = """
You are an AI job matching evaluator.

Given a resume profile and a job description, evaluate how well the job matches the resume.

Return ONLY valid JSON. No explanation text outside JSON.

JSON format:
{{
  "match_score": number between 0 and 100,
  "reason": "short explanation (1 sentence)"
}}

Resume Profile:
{resume_profile}

Job Description:
{job_description}
"""



def rank_job(resume_profile: dict, job: dict) -> dict:
    job_text = f"""
Role: {job['role']}
Skills: {job['skills']}
Description: {job['description']}
"""

    prompt = RANKING_PROMPT.format(
        resume_profile=json.dumps(resume_profile),
        job_description=job_text
    )

    response = llm.invoke(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {
            "match_score": 0,
            "reason": "Could not evaluate match"
        }


if __name__ == "__main__":
    # Temporary manual test
    sample_resume = {
        "skills": ["Python", "Machine Learning", "FastAPI"],
        "experience_level": "Intern",
        "preferred_field": "AI"
    }

    sample_job = {
        "role": "AI Intern",
        "skills": "Python,Machine Learning,RAG",
        "description": "Work on AI models and RAG-based systems."
    }

    result = rank_job(sample_resume, sample_job)
    print("📊 Ranking Result:")
    print(result)
