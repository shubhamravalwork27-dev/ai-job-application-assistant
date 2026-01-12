from backend.resume_analyzer import analyze_resume
from backend.retriever import retrieve_jobs
from backend.ranker import rank_job

def run_pipeline(resume_path: str):
    print("🔍 Analyzing resume...")
    resume_profile = analyze_resume(resume_path)

    print("📄 Resume Profile:")
    print(resume_profile)

    # Build search query from resume
    query = " ".join(resume_profile["skills"]) + " " + resume_profile["preferred_field"]

    print("\n🔎 Retrieving relevant jobs...")
    retrieved_jobs = retrieve_jobs(query, top_k=5)

    print("\n📊 Ranking jobs...")
    ranked_results = []

    for job in retrieved_jobs:
        ranking = rank_job(resume_profile, job)
        ranked_results.append({
            "company": job["company"],
            "role": job["role"],
            "location": job["location"],
            "match_score": ranking["match_score"],
            "reason": ranking["reason"]
        })

    # Sort by score descending
    ranked_results.sort(key=lambda x: x["match_score"], reverse=True)

    print("\n✅ Final Ranked Jobs:")
    for job in ranked_results:
        print(
            f"- {job['company']} | {job['role']} | {job['location']} "
            f"| Match: {job['match_score']}% | {job['reason']}"
        )

    return ranked_results


if __name__ == "__main__":
    run_pipeline("data/resumes/Shubham_Raval_Resume.pdf")
