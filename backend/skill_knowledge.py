# backend/skill_knowledge.py

"""
Global skill knowledge base.
This file is resume-independent and job-independent.
It grows slowly over time.
"""

# Exact / Alias relationships
# Concept → concrete skills
SKILL_ALIASES = {
    "api development": ["fastapi", "flask", "rest api"],
    "backend development": ["fastapi", "django", "flask"],
    "databases": ["mongodb", "postgresql", "firebase"],
    "frontend development": ["react", "next.js", "tailwind"],
}

# Conceptual / partial relationships
# Job concept → related resume skills
RELATED_SKILLS = {
    "rag": ["langchain", "faiss"],
    "vector search": ["faiss", "pinecone", "chromadb"],
    "llm systems": ["langchain"],
}
