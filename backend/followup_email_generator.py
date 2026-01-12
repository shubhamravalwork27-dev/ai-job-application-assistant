from langchain_ollama import OllamaLLM

# Initialize LLM (same model as main email generator)
llm = OllamaLLM(model="mistral")

FOLLOWUP_EMAIL_PROMPT = """
You are an AI assistant that writes ONLY a short follow-up email body for a job application.

The purpose of this email is ONLY to politely follow up on a previously submitted application.

Context:
- The candidate applied {days} days ago
- Company: {company}
- Role: {role}

STRICT RULES:
- DO NOT mention resume details, education, skills, or past experience
- DO NOT repeat qualifications or achievements
- DO NOT include a subject line
- DO NOT include any greeting (e.g., "Dear Hiring Manager")
- DO NOT include any closing lines (e.g., "Thank you", "Best regards")
- DO NOT include a name or signature
- Keep the email to 2 short paragraphs maximum

Tone:
- Professional
- Polite
- Non-pushy

Return ONLY the follow-up email body text. Nothing else.


"""
def generate_followup_email(
    job: dict,
    days_since_application: int,
    tone: str = "professional"
) -> str:
    """
    Generates a clean follow-up email body (no subject, greeting, closing, or signature).
    """

    prompt = FOLLOWUP_EMAIL_PROMPT.format(
        days=days_since_application,
        company=job["company"],
        role=job["role"]
    )

    # 1️⃣ Call LLM FIRST
    email_body = llm.invoke(prompt).strip()

    # 2️⃣ Defensive cleanup SECOND
    lines = email_body.splitlines()
    clean_lines = []

    for line in lines:
        lower = line.lower().strip()

        # Remove subject lines
        if lower.startswith("subject:"):
            continue

        # Remove greetings
        if lower.startswith("dear"):
            continue

        # Stop at closing lines
        if lower in [
            "best regards,",
            "best regards",
            "kind regards,",
            "kind regards",
            "sincerely,",
            "sincerely",
            "regards,",
            "regards"
        ]:
            break

        # Remove placeholders
        if "[your name]" in lower:
            continue

        clean_lines.append(line.strip())

    # 3️⃣ Return clean body
    return "\n".join(clean_lines).strip()
