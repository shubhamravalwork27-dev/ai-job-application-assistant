# backend/test_skill_pipeline.py

from backend.job_skill_extractor import extract_job_skills
from backend.skill_matcher import compare_skills

# ---- Fake resume skills (simulate extracted resume) ----
resume_skills = [
    "Python",
    "Docker",
    "LangChain",
    "FAISS"
]

# ---- Fake job description ----
job_description = """
We are looking for an AI Engineer with experience in Python,
RAG systems, vector search, and Kubernetes.
"""

# ---- Extract job skills ----
job_skills = extract_job_skills(job_description)

print("Job skills extracted:")
print(job_skills)

# ---- Compare ----
result = compare_skills(resume_skills, job_skills)

print("\nSkill Match Result:")
print(result)
