
import streamlit as st
import tempfile
import os
import urllib.parse

from backend.tone_llm import recommend_tone_llm
from backend.job_skill_extractor import extract_job_skills
from backend.skill_matcher import compare_skills
from backend.resume_analyzer import analyze_resume
from backend.retriever import retrieve_jobs
from backend.ranker import rank_job
from backend.email_generator import generate_email_draft
from backend.followup_email_generator import generate_followup_email
from backend.user_profiles import save_profile
from backend.user_profiles import (
    list_profiles,
    load_profile,
    create_profile
)
from datetime import datetime, timedelta
# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Job Application Assistant",
    layout="centered"
)


def add_application_to_profile(profile_data: dict, job: dict, tone: str):
    # Ensure applications list exists
    if "applications" not in profile_data:
        profile_data["applications"] = []

    application = {
        "company": job["company"],
        "role": job["role"],
        "location": job.get("location", ""),
        "applied_on": datetime.now().strftime("%Y-%m-%d"),
        "email_tone": tone,
        "status": "Applied",
        "follow_up_due": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    }

    profile_data["applications"].append(application)
    save_profile(profile_data)

    return profile_data

if "active_profile" not in st.session_state:
    st.session_state.active_profile = None

if "profile_data" not in st.session_state:
    st.session_state.profile_data = None
if "followup_emails" not in st.session_state:
    st.session_state["followup_emails"] = {}

if "user_info" not in st.session_state:
    st.session_state["user_info"] = {}
if "tone_recommendations" not in st.session_state:
    st.session_state.tone_recommendations = {}
# ---------------- Session State Initialization ----------------
if "ranked_jobs" not in st.session_state:
    st.session_state.ranked_jobs = []

if "resume_profile" not in st.session_state:
    st.session_state.resume_profile = None

if "selected_jobs" not in st.session_state:
    st.session_state.selected_jobs = []


st.subheader("Select Profile")

profiles = list_profiles()

profile_options = profiles + ["➕ Create New Profile"]

selected_profile = st.radio(
    "Choose a profile:",
    profile_options,
    key="profile_selector"
)

# ---- Create new profile ----
if selected_profile == "➕ Create New Profile":
    new_profile_name = st.text_input("Enter new profile name")
    

    if st.button("Create Profile"):
        if not new_profile_name.strip():
            st.error("Profile name cannot be empty.")
        else:
            try:
                profile_data = create_profile(new_profile_name)
                st.session_state.active_profile = profile_data["profile_id"]
                st.session_state.profile_data = profile_data
                st.session_state.current_step = "job_selection"
                st.session_state.selected_jobs = []
                st.session_state.ranked_jobs = []

                st.success(f"Profile '{new_profile_name}' created and selected.")
                st.rerun()

            except ValueError:
                st.error("Profile already exists.")

# ---- Load existing profile ----
else:
    if st.button("Use Selected Profile"):
        profile_data = load_profile(selected_profile)

# 🔥 RESET APP FLOW FOR SWITCHED PROFILE
        st.session_state.active_profile = selected_profile
        st.session_state.profile_data = profile_data
        st.session_state.current_step = "job_selection"
        st.session_state.selected_jobs = []
        st.session_state.ranked_jobs = []

        st.success(f"Active profile: {profile_data['profile_name']}")
        st.rerun()


if not st.session_state.active_profile:
    st.info("Please select or create a profile to continue.")
    st.stop()
st.title("AI Job Application Assistant")

st.markdown(
    """
    Upload your resume, review matched jobs, select one,
    and generate a professional job application email.
    """
)

# ================= RESUME UPLOAD =================
st.subheader("Resume Upload")

uploaded_file = st.file_uploader(
    "Upload your resume (PDF only)",
    type=["pdf"]
)

# ================= JOB PREFERENCES =================
st.subheader("Job Preferences")



preferred_field = st.selectbox(
    "Preferred Job Field",
    ["AI", "Data Science", "Web", "Cybersecurity", "Software", "Cloud", "IT"]
)

preferred_state = st.selectbox(
    "Preferred State / Location (optional)",
    ["All India", "Gujarat", "Maharashtra", "Karnataka", "Delhi", "Remote"]
)

# ================= CONTACT DETAILS =================


st.subheader("Contact & Profile Links (Optional)"
)
full_name = st.text_input("Full Name (optional)")

phone = st.text_input("Mobile Number (10 digits)")
if phone:
    if not phone.isdigit():
        st.warning("Mobile number should contain only digits.")
    elif len(phone) != 10:
        st.warning("Mobile number should be exactly 10 digits.")

portfolio = st.text_input("Portfolio URL")
github = st.text_input("GitHub Profile URL")
linkedin = st.text_input("LinkedIn Profile URL")

# ---- Build user info ONCE (global, safe) ----
user_info = {
    "full_name": full_name.strip() if full_name else None,
    "phone": phone if phone.isdigit() and len(phone) == 10 else None,
    "portfolio": portfolio.strip() if portfolio else None,
    "github": github.strip() if github else None,
    "linkedin": linkedin.strip() if linkedin else None
}
st.session_state["user_info"] = user_info


# ================= STEP 1: GENERATE JOB MATCHES =================
if uploaded_file and st.button("Step 1: Generate Job Matches"):

    with st.spinner("Analyzing resume and finding best matches..."):

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            resume_path = tmp.name

        resume_profile = analyze_resume(resume_path)
        resume_profile.setdefault("skills", [])
        resume_profile.setdefault("experience_level", "Fresher")

        query_parts = resume_profile["skills"] + [preferred_field]
        if preferred_state != "All India":
            query_parts.append(preferred_state)

        query = " ".join(query_parts)

        jobs = retrieve_jobs(query, top_k=3)

        ranked_jobs = []
        for job in jobs:
            ranking = rank_job(resume_profile, job)
            ranked_jobs.append((job, ranking))

        ranked_jobs.sort(key=lambda x: x[1]["match_score"], reverse=True)

        st.session_state["ranked_jobs"] = ranked_jobs
        st.session_state["resume_profile"] = resume_profile
        os.remove(resume_path)
applications = st.session_state.profile_data.get("applications", [])
# ================= STEP 2: SHOW MATCHED JOBS =================
# ================= STEP 2: SHOW MATCHED JOBS =================
if "ranked_jobs" in st.session_state:

    st.subheader("Step 2: Matched Jobs")

    selected_jobs = []

    for idx, (job, ranking) in enumerate(st.session_state["ranked_jobs"]):

        label = f"{job['company']} | {job['role']} | Match: {ranking['match_score']}%"

        is_selected = st.checkbox(label, key=f"job_select_{idx}")

        st.caption(f"Why matched: {ranking['reason']}")

        if is_selected:
            selected_jobs.append(job)

    # ---- Validation (AFTER loop) ----
    if not selected_jobs:
        st.warning("Please select at least one job to continue.")

    # ---- Continue button (AFTER loop) ----
    if selected_jobs and st.button("Continue with selected jobs",key="continue_jobs"):
        st.session_state.selected_jobs = selected_jobs
        st.success(f"{len(selected_jobs)} job(s) selected.")
        st.rerun() 
table_data = []
for app in applications:
    table_data.append({
        "Company": app["company"],
        "Role": app["role"],
        "Status": app["status"],
        "Applied On": app["applied_on"],
        "Email Tone": app["email_tone"]
    })
     
    
    # ================= STEP 4: EXPLAINABLE SKILL MATCH =================
st.subheader("Explainable Skill Match")

for job in st.session_state.selected_jobs:
    st.markdown("---")
    st.markdown(f"### {job['company']} — {job['role']}")

    job_skills = extract_job_skills(job.get("description", ""))
    resume_skills = st.session_state["resume_profile"]["skills"]

    result = compare_skills(resume_skills, job_skills)

    st.markdown("**Matched Skills**")
    if result["matched"]:
        st.write(", ".join(result["matched"]))
    else:
        st.caption("None")

    st.markdown("**Related Skills**")
    if result["related"]:
        for r, j in result["related"]:
            st.write(f"{r} → {j}")
    else:
        st.caption("None")

    st.markdown("**Missing Skills**")
    if result["missing"]:
        st.write(", ".join(result["missing"]))
    else:
        st.caption("None")

        # ================= STEP 3.3: LLM TONE RECOMMENDATION =================
# ================= STEP 3: CHOOSE EMAIL STYLE (PER JOB) =================
if "selected_jobs" in st.session_state and st.session_state.selected_jobs:

    st.subheader("Step 3: Choose Email Style (Per Job)")

    # Initialize storage once
    if "final_tones" not in st.session_state:
        st.session_state.final_tones = {}

    for idx, job in enumerate(st.session_state.selected_jobs):

        job_key = f"{job['company']}|{job['role']}"

        # ---------- AI RECOMMENDATION ----------
        if job_key not in st.session_state.tone_recommendations:
            with st.spinner(f"Analyzing best email tone for {job['company']}..."):
                st.session_state.tone_recommendations[job_key] = recommend_tone_llm(job)

        rec = st.session_state.tone_recommendations[job_key]

        st.markdown(f"### {job['company']} — {job['role']}")
        st.markdown(f"**AI Recommended Tone:** `{rec['tone'].title()}`")
        st.caption(rec["reason"])

        # ---------- USER SELECTION ----------
        if job_key not in st.session_state.final_tones:
            st.session_state.final_tones[job_key] = rec["tone"]

        selected_tone = st.radio(
            "Choose email tone:",
            ["formal", "concise", "enthusiastic"],
            index=["formal", "concise", "enthusiastic"].index(
                st.session_state.final_tones[job_key]
            ),
            key=f"tone_select_{job_key}"
        )

        st.session_state.final_tones[job_key] = selected_tone

        st.divider()

    # ---------- SAVE & CONTINUE ----------
    if st.button("Save Email Preferences"):
        job_email_configs = []

        for job in st.session_state.selected_jobs:
            job_key = f"{job['company']}|{job['role']}"
            job_email_configs.append({
                "job": job,
                "tone": st.session_state.final_tones[job_key]
            })

        st.session_state.job_email_configs = job_email_configs
        st.session_state.tone_confirmed = True

        st.success("Email preferences saved. Proceed to Step 4.")


    # ================= STEP 4: GENERATE EMAIL =================
    # ================= STEP 4: GENERATE EMAILS =================
if "job_email_configs" in st.session_state:

    st.subheader("Step 4: Generate Emails")

    if st.button("Generate Email Drafts"):

        generated_emails = []

        with st.spinner("Generating emails..."):

            for item in st.session_state["job_email_configs"]:

                job = item["job"]
                tone = item["tone"]

                email_text = generate_email_draft(
                    resume_profile=st.session_state["resume_profile"],
                    job=job,
                    tone=tone,
                    user_info=st.session_state["user_info"]
                )

                generated_emails.append({
                    "job": job,
                    "tone": tone,
                    "email": email_text
                })

        st.session_state["generated_emails"] = generated_emails
        st.success("Email drafts generated successfully.")
        st.divider()

# ================= STEP 5: EMAIL PREVIEWS =================
if "generated_emails" in st.session_state:

    st.divider()
    st.subheader("Step 5: Email Previews")

    for idx, item in enumerate(st.session_state["generated_emails"]):

        job = item["job"]
        tone = item["tone"]
        email_text = item["email"]
        job_key = f"{job['company']}|{job['role']}"
        
        
        st.markdown(
            f"### 📌 {job['company']} — {job['role']}  \n"
            f"**Email Style:** {tone.capitalize()}"
        )
       
        show_copy_view = st.checkbox(
        "Show copy-friendly view",
        key=f"toggle_copy_view_{idx}"
        )
        if show_copy_view:
            st.code(email_text, language="text")
            st.caption("⧉ Use the copy icon to copy this email")
        else:
            st.text_area(
            label="Email Preview",
            value=email_text,
            height=350,
            key=f"email_preview_{idx}"
            )
        subject = f"Application for {job['role']} at {job['company']}"
        encoded_subject = urllib.parse.quote(subject)
        encoded_body = urllib.parse.quote(email_text)

        gmail_url = ("https://mail.google.com/mail/?view=cm&fs=1"
            f"&su={encoded_subject}"
            f"&body={encoded_body}"
        )

        st.markdown(
        f"""
        <a href="{gmail_url}" target="_blank">
        <button style="
            background-color:#EA4335;
            color:white;
            padding:10px 16px;
            border:none;
            border-radius:6px;
            cursor:pointer;
            font-size:14px;
        ">
            📧 Open in Gmail
        </button>
        </a>
        """,unsafe_allow_html=True
        )  
        st.markdown("#### 🔁 Follow-up Email")

        days = st.radio(
            "How many days since you applied?",
            [5, 7, 10, 14],
            horizontal=True,
            key=f"followup_days_{idx}"
        )
        

        if st.button("Generate Follow-up Email", key=f"gen_followup_{idx}"):

            followup_text = generate_followup_email(
            job=job,
            days_since_application=days
        )

            st.session_state["followup_emails"][job_key] = followup_text



        if job_key in st.session_state["followup_emails"]:

            clean_followup = "\n".join(
                    line.strip()
                    for line in st.session_state["followup_emails"][job_key].splitlines()
                    if line.strip()
                )

            st.text_area(   
                "Follow-up Preview",
                clean_followup,
                height=220,
                key=f"followup_preview_{job_key}"
                )
            # ---- Open Follow-up in Gmail ----
            subject = f"Follow-up: {job['role']} at {job['company']}"

            encoded_subject = urllib.parse.quote(subject)
            encoded_body = urllib.parse.quote(clean_followup)

            gmail_url = ("https://mail.google.com/mail/?view=cm&fs=1"
                f"&su={encoded_subject}&body={encoded_body}"
            )

            st.markdown(
                f"""
                <a href="{gmail_url}" target="_blank">
                <button style="
                background-color:#EA4335;
                color:white;
                padding:8px 16px;
                border:none;
                border-radius:6px;
                cursor:pointer;
                margin-top:8px;
                ">
                📧 Open Follow-up in Gmail
                </button>
                </a>
                """,
                unsafe_allow_html=True
                )


        st.caption("Tip: Click inside → Ctrl + A → Ctrl + C to copy")
# ================= CONFIRM APPLICATION =================
    st.divider()
    st.subheader("Confirm Application")

if st.button("Mark as Applied"):

    if not st.session_state.get("generated_emails"):
        st.error("No generated emails found.")
        st.stop()

    for item in st.session_state["generated_emails"]:
        st.session_state.profile_data = add_application_to_profile(
            profile_data=st.session_state.profile_data,
            job=item["job"],
            tone=item["tone"]
        )

    st.success("✅ Applications saved to your profile.")
    st.write("Saved applications:")

    # Optional: show saved data
    st.json(st.session_state.profile_data["applications"])

    # Force UI refresh
# ================= STEP 5: APPLICATION TRACKER =================
st.divider()
st.subheader("Step 5: Application Tracker")
if not applications:
    st.info("No applications tracked yet.")
else:
    table_data = []
    for app in applications:
        table_data.append({
            "Company": app["company"],
            "Role": app["role"],
            "Status": app["status"],
            "Applied On": app["applied_on"],
            "Email Tone": app["email_tone"]
        })

    st.table(table_data)
  
st.divider()
st.subheader("Step 6: Update Application Status")
for idx, app in enumerate(applications):
    st.markdown(f"### {app['company']} — {app['role']}")
    new_status = st.selectbox(
        "Update status:",
        ["Applied", "Replied", "Interview", "Rejected", "Offer"],
        index=["Applied", "Replied", "Interview", "Rejected", "Offer"].index(app["status"]),
        key=f"status_select_{idx}"
    )
    if st.button("Save Status", key=f"save_status_{idx}"):
        st.session_state.profile_data["applications"][idx]["status"] = new_status

        save_profile(st.session_state.profile_data)

        st.success("Status updated successfully.")
        st.rerun()
