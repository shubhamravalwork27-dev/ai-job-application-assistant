from langchain_ollama import OllamaLLM

# Initialize LLM
llm = OllamaLLM(model="mistral")

# Prompt for generating ONLY the email body
EMAIL_PROMPT = """
You are an AI assistant that writes job application emails.

Write a {tone} job application email using the details below.
Keep it professional and concise.

IMPORTANT RULES:
- Write ONLY the main email body.
- STOP writing before any closing lines.
- DO NOT write "Best regards", "Sincerely","Regards","Best Wishes" or any sign-off.
- DO NOT include names, placeholders, or contact details.



Job Details:
Company: {company}
Role: {role}
Location: {location}

Candidate Profile:
Skills: {skills}
Experience Level: {experience_level}

Return ONLY the email body text.
"""

def build_signature(user_info: dict) -> str:
    """
    Builds a professional email signature.
    Only includes fields that the user actually provided.
    """
    lines = []

    if user_info.get("full_name"):
        lines.append(user_info["full_name"])

    if user_info.get("phone"):
        lines.append(f"Phone: {user_info['phone']}")

    if user_info.get("portfolio"):
        lines.append(f"Portfolio: {user_info['portfolio']}")

    if user_info.get("linkedin"):
        lines.append(f"LinkedIn: {user_info['linkedin']}")

    if user_info.get("github"):
        lines.append(f"GitHub: {user_info['github']}")

    if not lines:
        return ""

    return "\n".join(lines)


def generate_email_draft(
    resume_profile: dict,
    job: dict,
    tone: str,
    user_info: dict
) -> str:
    """
    Generates a complete job application email with a clean signature.
    """
    prompt = EMAIL_PROMPT.format(
        tone=tone,
        company=job["company"],
        role=job["role"],
        location=job["location"],
        skills=", ".join(resume_profile["skills"]),
        experience_level=resume_profile["experience_level"]
    )

    # Generate email body from LLM
    email_body = llm.invoke(prompt).strip()
    # ---- Safety: remove any accidental sign-offs from LLM ----
    for bad_phrase in ["Best regards", "Sincerely", "Kind regards", "[Your Name]"]:
        if bad_phrase in email_body:
            email_body = email_body.split(bad_phrase)[0].strip()


    # Build deterministic signature
    signature = build_signature(user_info)

    # Assemble final email
    if signature:
        return f"{email_body}\n\nBest regards,\n{signature}"
    else:
        return f"{email_body}\n\nBest regards,"
