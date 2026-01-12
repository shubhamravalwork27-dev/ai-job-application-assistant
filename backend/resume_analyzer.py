import json
from langchain_ollama import OllamaLLM

from backend.resume_parser import parse_resume
llm = OllamaLLM(model="mistral")


RESUME_ANALYSIS_PROMPT = """
You are an AI resume analyzer.

Extract the following information from the resume text below.
Return ONLY valid JSON. No explanation. No markdown.

Fields required:
- skills: list of technical skills
- experience_level: one of [Intern, Fresher, Junior, Mid]
- preferred_field: one of [AI, Data Science, Web, Cybersecurity, Software, Cloud, IT]

Resume text:
{resume_text}
"""

def analyze_resume(pdf_path: str) -> dict:
    resume_text = parse_resume(pdf_path)

    prompt = RESUME_ANALYSIS_PROMPT.format(resume_text=resume_text)

    response = llm.invoke(prompt)


    try:
        return json.loads(response)
    except json.JSONDecodeError:
        raise ValueError("LLM did not return valid JSON")


if __name__ == "__main__":
    result = analyze_resume("data/resumes/Shubham_Raval_Resume.pdf")
    print("------ STRUCTURED RESUME PROFILE ------")
    print(json.dumps(result, indent=2))
