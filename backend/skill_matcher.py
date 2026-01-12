# backend/skill_matcher.py

from backend.skill_knowledge import SKILL_ALIASES, RELATED_SKILLS


def normalize(skill: str) -> str:
    """Normalize skill text for comparison."""
    return skill.lower().strip()


def expand_resume_skills(resume_skills):
    """
    Expands resume skills using alias knowledge.
    Example: FastAPI → API Development
    """
    expanded = set()

    for skill in resume_skills:
        norm = normalize(skill)
        expanded.add(norm)

        for parent, children in SKILL_ALIASES.items():
            if norm in children:
                expanded.add(parent)

    return expanded

def normalize_job_skill(skill: str) -> str:
    s = normalize(skill)

    if "rag" in s:
        return "rag"
    if "vector" in s:
        return "vector search"

    return s

def find_related(resume_set, job_set):
    """
    Finds related / partial skill matches.
    Example: LangChain ↔ RAG
    """
    related = []

    for job_skill in job_set:
        for concept, related_list in RELATED_SKILLS.items():
            if job_skill == concept:
                for resume_skill in related_list:
                    if resume_skill in resume_set:
                        related.append((resume_skill, job_skill))

    return related


def normalize_job_skill(skill: str) -> str:
    s = normalize(skill)

    if "rag" in s or "retrieval augmented" in s:
        return "rag"
    if "vector" in s:
        return "vector search"

    return s


def compare_skills(resume_skills, job_skills):
    resume_set = expand_resume_skills(resume_skills)

    # ✅ Normalize job skills into known concepts
    job_set = {normalize_job_skill(skill) for skill in job_skills}

    matched = sorted(job_set & resume_set)

    related = find_related(resume_set, job_set)
    related_job_skills = {job for _, job in related}

    missing = sorted(job_set - set(matched) - related_job_skills)

    return {
        "matched": matched,
        "related": related,
        "missing": missing,
    }
