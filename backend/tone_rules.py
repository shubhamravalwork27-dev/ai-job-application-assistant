# backend/tone_rules.py

"""
Rule-based email tone intelligence.
"""

ENTERPRISE_COMPANIES = [
    "google", "microsoft", "amazon", "meta", "ibm", "oracle"
]

STARTUP_KEYWORDS = [
    "startup", "early", "seed", "series a", "fast-growing"
]

JUNIOR_KEYWORDS = [
    "intern", "junior", "entry", "fresher", "trainee"
]


def recommend_tone(job: dict) -> tuple[str, str]:
    """
    Returns (tone, reason)
    """

    company = job.get("company", "").lower()
    role = job.get("role", "").lower()
    description = job.get("description", "").lower()

    # Rule 1 — Enterprise companies
    if company in ENTERPRISE_COMPANIES:
        return (
            "formal",
            "This is a large enterprise company, so a professional tone is recommended."
        )

    # Rule 2 — Junior roles
    for word in JUNIOR_KEYWORDS:
        if word in role:
            return (
                "enthusiastic",
                "This role is junior-level, so an enthusiastic tone works best."
            )

    # Rule 3 — Startup language
    for word in STARTUP_KEYWORDS:
        if word in description:
            return (
                "enthusiastic",
                "The job description suggests a startup environment."
            )

    # Default
    return (
        "concise",
        "A concise and professional tone is suitable for this role."
    )
