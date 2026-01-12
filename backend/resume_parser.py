import pdfplumber

def parse_resume(pdf_path: str) -> str:
    """
    Extract text from a PDF resume.
    Returns clean combined text from all pages.
    """
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text.strip()


# Simple manual test
if __name__ == "__main__":
    sample_path = "data/resumes/Shubham_Raval_Resume.pdf"
    extracted_text = parse_resume(sample_path)
    print("------ RESUME TEXT ------")
    print(extracted_text)
