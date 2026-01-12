from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="mistral")

JOB_SKILL_PROMPT = """
Extract a list of technical skills from the job description below.

Rules:
- Return ONLY a comma-separated list of skills
- Do NOT add explanations
- Do NOT include soft skills unless technical
- Normalize skill names (e.g., Python, Machine Learning, Docker)

Job Description:
{job_description}
"""

def extract_job_skills(job_description: str) -> list[str]:
    """
    Extracts technical skills from a job description.
    """

    response = llm.invoke(
        JOB_SKILL_PROMPT.format(job_description=job_description)
    )

    skills = [
        skill.strip()
        for skill in response.split(",")
        if skill.strip()
    ]

    return list(set(skills))
