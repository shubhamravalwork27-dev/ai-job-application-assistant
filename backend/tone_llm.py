# backend/tone_llm.py

from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="mistral")

PROMPT = """
You are an AI assistant helping to write job application emails.

Given the job details below, recommend the BEST email tone.

Choose ONLY ONE tone from:
- formal
- concise
- enthusiastic

Also give a short reason.

Job Details:
Company: {company}
Role: {role}
Description: {description}

Respond strictly in JSON format:
{{
  "tone": "<formal|concise|enthusiastic>",
  "reason": "<short explanation>"
}}
"""

def recommend_tone_llm(job: dict) -> dict:
    response = llm.invoke(
        PROMPT.format(
            company=job.get("company", ""),
            role=job.get("role", ""),
            description=job.get("description", "")
        )
    )

    try:
        import json
        return json.loads(response)
    except Exception:
        # Safe fallback
        return {
            "tone": "concise",
            "reason": "Defaulted due to parsing issue."
        }
