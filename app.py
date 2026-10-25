
import textwrap

import pandas as pd
import plotly.express as px
import streamlit as st

from job_matcher import (
    label,
    load_roles,
    role_from_job_description,
    score_roles,
)
from report import build_report
from resume_insights import detect_sections, resume_tips
from resume_parser import ResumeParseError, extract_text
from roadmap_generator import build_roadmap, roadmap_dataframe
from skill_extractor import extract_skills, group_by_category
from text_cleaner import clean_text


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ResumeIQ",
    page_icon="📄",
    layout="wide",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            ellipse at top left,
            rgba(124, 58, 237, 0.13),
            transparent 45%
        ),
        #0B0B12;
}

.block-container {
    max-width: 1450px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: #10101A;
    border-right: 1px solid #302943;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #191927, #12121C);
    border: 1px solid #302943;
    padding: 22px;
    border-radius: 16px;
}

[data-testid="stMetricLabel"] {
    color: #B8B4CC;
}

[data-testid="stMetricValue"] {
    color: #C4B5FD;
    font-weight: 800;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 10px;
    border: 1px solid #8B5CF6;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: #C4B5FD;
    color: #DDD6FE;
}

div[data-testid="stFileUploader"] {
    border: 1px dashed #65518F;
    border-radius: 14px;
    padding: 12px;
}

[data-testid="stDataFrame"] {
    border: 1px solid #302943;
    border-radius: 12px;
}

h1 {
    font-weight: 800 !important;
    letter-spacing: -1px;
}

/* Sidebar navigation spacing */

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    border-radius: 9px;
    padding-top: 7px;
    padding-bottom: 7px;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #211B32;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# MAIN HEADER
# Fixed HTML indentation using textwrap.dedent
# --------------------------------------------------

header_html = textwrap.dedent("""
    <div style="margin-bottom:28px; padding-top:8px;">
        <div style="
            color:#A78BFA;
            font-size:12px;
            font-weight:700;
            letter-spacing:2px;
            margin-bottom:12px;">
            AI-POWERED CAREER INTELLIGENCE
        </div>

        <h1 style="margin:0; line-height:1.2;">
            Your next career move<br>
            <span style="color:#A78BFA;">
                starts with your resume.
            </span>
        </h1>
    </div>
""").strip()

st.html(header_html)


# --------------------------------------------------
# LOAD ROLES
# --------------------------------------------------

roles = list(load_roles())


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    

    # WORKSPACE NAVIGATION

    workspace_html = textwrap.dedent("""
        <div style="
            color:#A78BFA;
            font-size:11px;
            font-weight:700;
            letter-spacing:1.5px;
            padding:4px 0 10px 0;">
            WORKSPACE
        </div>
    """).strip()

    st.html(workspace_html)

    selected_tab = st.radio(
        "Navigation",
        [
            "Overview",
            "Skills",
            "Role matches",
            "Skill gap & roadmap",
            "Resume tips",
            "Report",
        ],
        key="main_navigation",
        label_visibility="collapsed",
    )

    st.divider()

    # RESUME UPLOAD

    st.subheader("Upload resume")

    uploaded = st.file_uploader(
        "Choose a resume",
        type=["pdf", "docx", "txt"],
        help="Maximum file size: 5 MB.",
    )

    st.divider()

    # TARGET ROLE

    st.subheader("Target role")

    jd_text = st.text_area(
        "Job description (optional)",
        height=120,
    )

    if jd_text.strip():
        custom_role = role_from_job_description(jd_text)

        roles = [custom_role] + [
            role for role in roles
            if role.name != custom_role.name
        ]

    target_name = st.selectbox(
        "Choose role",
        [role.name for role in roles],
    )


# --------------------------------------------------
# WAIT FOR RESUME UPLOAD
# --------------------------------------------------

if not uploaded:
    st.stop()


# --------------------------------------------------
# ANALYZE RESUME
# --------------------------------------------------

try:
    raw = extract_text(
        uploaded.name,
        uploaded.getvalue(),
    )

except ResumeParseError as exc:
    st.error(str(exc))
    st.stop()

cleaned = clean_text(raw)

skills = extract_skills(cleaned)
by_cat = group_by_category(skills)

matches = score_roles(
    cleaned,
    skills,
    roles,
)

target = next(
    (
        match for match in matches
        if match["role"] == target_name
    ),
    None,
)

if target is None:
    st.error("The selected role could not be matched.")
    st.stop()

roadmap = build_roadmap(
    target["missing_required"],
    target["missing_nice"],
)

tips = resume_tips(raw, skills)

# Responsible AI notice (shown on every tab)
st.info(
    "**For guidance only.** Match scores are automated estimates, not recruiter "
    "decisions, and this tool must not be used to hire or reject anyone. "
    "A missing keyword does not mean missing ability. Only job-related skills, "
    "education, projects and experience are evaluated; gender, age, religion, "
    "nationality, photo, marital status and disability are never scored. "
    "Your resume is processed in memory and is not stored.",
    icon="ℹ️",
)


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

if selected_tab == "Overview":

    c1, c2, c3 = st.columns(3)

    c1.metric(
        f"Match: {target_name}",
        f"{target['score']}%",
        label(target["score"]),
    )

    c2.metric(
        "Skill coverage",
        f"{target['skill_coverage']}%",
    )

    c3.metric(
        "Text similarity",
        f"{target['text_similarity']}%",
    )

    st.divider()

    st.subheader("Top recommended roles")

    for i, match in enumerate(matches[:3], 1):

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(
                    f"**{i}. {match['role']}**"
                )
                st.caption(label(match["score"]))

            with col2:
                st.metric(
                    "Match",
                    f"{match['score']}%",
                )


# --------------------------------------------------
# SKILLS
# --------------------------------------------------

elif selected_tab == "Skills":

    if by_cat:

        cols = st.columns(2)

        for i, (category, items) in enumerate(
            sorted(by_cat.items())
        ):

            with cols[i % 2]:

                with st.container(border=True):
                    st.markdown(f"**{category}**")
                    st.write(" · ".join(items))

    else:
        st.warning("No known skills detected.")

    with st.expander("Detected resume sections"):

        sections = detect_sections(raw)

        st.write({
            name: ("Found" if found else "Not found")
            for name, found in sections.items()
        })


# --------------------------------------------------
# ROLE MATCHES
# --------------------------------------------------

elif selected_tab == "Role matches":

    df = pd.DataFrame(matches)[
        [
            "role",
            "score",
            "skill_coverage",
            "text_similarity",
        ]
    ]

    df = df.sort_values(
        "score",
        ascending=True,
    )

    fig = px.bar(
        df,
        x="score",
        y="role",
        orientation="h",
        range_x=[0, 100],
        text="score",
        labels={
            "score": "Match score (%)",
            "role": "",
        },
        color="score",
        color_continuous_scale=[
            "#312E81",
            "#7C3AED",
            "#C4B5FD",
        ],
    )

    fig.update_traces(
        texttemplate="%{text}%",
        textposition="outside",
        marker_line_width=0,
        cliponaxis=False,
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#EDE9FE",
            family="Inter",
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#292638",
            range=[0, 110],
            title="Match score (%)",
        ),
        yaxis=dict(
            showgrid=False,
            title="",
        ),
        coloraxis_showscale=False,
        margin=dict(
            l=10,
            r=35,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    st.subheader("Detailed comparison")

    st.dataframe(
        df.sort_values(
            "score",
            ascending=False,
        ),
        hide_index=True,
        width="stretch",
    )


# --------------------------------------------------
# SKILL GAP & ROADMAP
# --------------------------------------------------

elif selected_tab == "Skill gap & roadmap":

    a, b = st.columns(2)

    with a:

        with st.container(border=True):

            st.subheader("Matched skills")

            matched = (
                target["matched_required"]
                + target["matched_nice"]
            )

            st.write(
                ", ".join(matched) or "None"
            )

    with b:

        with st.container(border=True):

            st.subheader("Missing skills")

            st.write(
                "**Required:** "
                + (
                    ", ".join(target["missing_required"])
                    or "None"
                )
            )

            st.write(
                "**Nice to have:** "
                + (
                    ", ".join(target["missing_nice"])
                    or "None"
                )
            )

    st.divider()

    st.subheader("Learning roadmap")

    if roadmap:

        st.dataframe(
            roadmap_dataframe(roadmap),
            hide_index=True,
            width="stretch",
        )

    else:
        st.success("No skill gaps found.")


# --------------------------------------------------
# RESUME TIPS
# --------------------------------------------------

elif selected_tab == "Resume tips":

    for i, tip in enumerate(tips, 1):

        with st.container(border=True):
            st.markdown(f"**{i}.** {tip}")


# --------------------------------------------------
# REPORT
# --------------------------------------------------

elif selected_tab == "Report":

    md = build_report(
        uploaded.name,
        by_cat,
        matches,
        target,
        roadmap,
        tips,
    )

    st.download_button(
        "Download report",
        md,
        file_name="resume_analysis_report.md",
        mime="text/markdown",
        width="stretch",
    )

    with st.expander("Preview report"):
        st.markdown(md)
