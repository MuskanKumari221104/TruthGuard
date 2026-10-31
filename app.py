import tempfile
import html
from pathlib import Path

import streamlit as st

from src.pipeline import run_pipeline


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="TruthGuard AI | Intelligent Verification",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# CUSTOM DESIGN / CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background:
            radial-gradient(ellipse at 15% 10%, rgba(75, 35, 130, 0.25), transparent 40%),
            radial-gradient(ellipse at 85% 20%, rgba(0, 100, 160, 0.18), transparent 38%),
            radial-gradient(ellipse at 50% 100%, rgba(100, 20, 120, 0.18), transparent 45%),
            #070817;
        color: #f4efff;
    }

    /* Subtle star-like background */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        opacity: 0.28;
        background-image:
            radial-gradient(1px 1px at 10% 20%, #ffffff 99%, transparent),
            radial-gradient(1px 1px at 25% 70%, #c9a5ff 99%, transparent),
            radial-gradient(2px 2px at 55% 30%, #ffffff 99%, transparent),
            radial-gradient(1px 1px at 80% 60%, #d6baff 99%, transparent),
            radial-gradient(1px 1px at 90% 15%, #ffffff 99%, transparent);
        background-size: 220px 220px;
    }

    /* Main content width */
    .block-container {
        max-width: 1600px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111329 0%, #090b1b 100%);
        border-right: 1px solid rgba(177, 100, 255, 0.3);
    }

    section[data-testid="stSidebar"] * {
        color: #e9e2ff;
    }

    /* Sidebar brand */
    .sidebar-brand {
        color: #df75ff;
        font-size: 13px;
        font-weight: 900;
        letter-spacing: 5px;
        margin-top: 12px;
        margin-bottom: 35px;
    }

    .sidebar-heading {
        font-size: 21px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .sidebar-description {
        color: #a7a5c7;
        font-size: 14px;
        line-height: 1.7;
        margin-bottom: 25px;
    }

    .sidebar-divider {
        height: 1px;
        background: rgba(190, 150, 255, 0.2);
        margin: 25px 0;
    }

    /* Main heading */
    .eyebrow {
        color: #d96cff;
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 5px;
        margin-bottom: 12px;
    }

    .main-title {
        color: #ffffff;
        font-size: clamp(30px, 4vw, 48px);
        font-weight: 900;
        letter-spacing: -1.5px;
        margin: 0;
        text-shadow: 0 0 25px rgba(183, 80, 255, 0.2);
    }

    .main-subtitle {
        color: #aaa9c9;
        font-size: 16px;
        margin-top: 12px;
        margin-bottom: 28px;
    }

    /* Neon cards */
    .neon-card {
        position: relative;
        background: linear-gradient(
            145deg,
            rgba(30, 25, 65, 0.96),
            rgba(13, 17, 43, 0.96)
        );
        border: 1px solid rgba(176, 90, 255, 0.48);
        border-radius: 15px;
        padding: 23px;
        min-height: 175px;
        box-shadow:
            0 0 15px rgba(151, 61, 255, 0.08),
            inset 0 0 20px rgba(135, 70, 255, 0.035);
        transition: all 0.25s ease;
        overflow: hidden;
    }

    .neon-card:hover {
        border-color: #df75ff;
        box-shadow:
            0 0 12px rgba(212, 90, 255, 0.25),
            0 0 30px rgba(139, 70, 255, 0.12);
        transform: translateY(-3px);
    }

    .neon-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 12%;
        width: 76%;
        height: 2px;
        background: linear-gradient(
            90deg,
            transparent,
            #e46aff,
            #8b5cff,
            transparent
        );
        box-shadow: 0 0 12px #c85cff;
    }

    .card-label {
        color: #c2b5e6;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .card-value {
        color: #ffffff;
        font-size: 34px;
        font-weight: 900;
        margin-top: 13px;
    }

    .card-description {
        color: #9997bd;
        font-size: 13px;
        margin-top: 5px;
    }

    .panel-title {
        color: #f5eaff;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 17px;
    }

    /* Feature panels */
    .feature-panel {
        background: linear-gradient(
            145deg,
            rgba(27, 25, 61, 0.95),
            rgba(12, 16, 39, 0.98)
        );
        border: 1px solid rgba(155, 105, 255, 0.42);
        border-radius: 15px;
        padding: 21px;
        min-height: 275px;
        box-shadow: 0 0 20px rgba(118, 65, 220, 0.07);
    }

    .feature-heading {
        color: #f4eaff;
        font-size: 17px;
        font-weight: 800;
        margin-bottom: 17px;
    }

    .muted-text {
        color: #aaa8c8;
        font-size: 13px;
        line-height: 1.7;
    }

    .document-row {
        background: rgba(120, 85, 180, 0.12);
        border: 1px solid rgba(180, 120, 255, 0.2);
        padding: 10px 12px;
        border-radius: 8px;
        margin-bottom: 9px;
        color: #e9e0ff;
        font-size: 13px;
        overflow-wrap: anywhere;
    }

    .neon-line {
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(215, 100, 255, 0.65),
            rgba(80, 200, 255, 0.5),
            transparent
        );
        margin: 30px 0;
    }

    /* Answer panel */
    .answer-panel {
        background: linear-gradient(
            120deg,
            rgba(47, 23, 83, 0.75),
            rgba(15, 24, 57, 0.95)
        );
        border: 1px solid #d65cff;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 0 22px rgba(194, 75, 255, 0.12);
    }

    .answer-label {
        color: #d87aff;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }

    .answer-text {
        color: #ffffff;
        font-size: 21px;
        line-height: 1.6;
        font-weight: 800;
    }

    /* Status labels */
    .status-pill {
        display: inline-block;
        padding: 7px 15px;
        border-radius: 30px;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: 1px;
        margin-bottom: 20px;
        background: rgba(193, 82, 255, 0.15);
        color: #e39aff;
        border: 1px solid rgba(215, 105, 255, 0.6);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #a43cff, #e14dce);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 9px;
        font-weight: 800;
        min-height: 45px;
        box-shadow: 0 0 15px rgba(187, 68, 255, 0.25);
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #ffffff;
        box-shadow: 0 0 22px rgba(210, 85, 255, 0.5);
        transform: translateY(-2px);
    }

    /* Inputs */
    .stTextArea textarea,
    .stTextInput input {
        background: #11162e !important;
        color: #ffffff !important;
        border: 1px solid rgba(177, 110, 255, 0.4) !important;
        border-radius: 9px !important;
    }

    [data-testid="stFileUploader"] {
        background: rgba(15, 18, 42, 0.8);
        border: 1px dashed rgba(194, 105, 255, 0.55);
        border-radius: 10px;
        padding: 12px;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(28, 26, 62, 0.8);
        border: 1px solid rgba(164, 103, 255, 0.35);
        border-radius: 8px;
    }

    /* Hide Streamlit branding */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def safe_text(value):
    """Escape dynamic text before placing it inside HTML."""
    return html.escape(str(value if value is not None else ""))


def render_metric(label, value, description):
    st.markdown(
        f"""
        <div class="neon-card">
            <div class="card-label">{safe_text(label)}</div>
            <div class="card-value">{safe_text(value)}</div>
            <div class="card-description">{safe_text(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(title):
    st.markdown(
        f'<div class="panel-title">{title}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">TRUTHGUARD AI</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-heading">🛡️ Control Center</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-description">'
        'Intelligent document analysis and verification'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown("### 📁 Document Import")

    st.caption("Upload your policy documents")

    uploaded_files = st.file_uploader(
        "Upload PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        help="Upload the documents you want TruthGuard to analyze.",
        label_visibility="collapsed",
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} document(s) selected")

        with st.expander("View uploaded documents"):
            for file in uploaded_files:
                st.write(f"📄 {file.name}")

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown("### 💬 Ask TruthGuard")

    question = st.text_area(
        "Your question",
        placeholder=(
            "Example: How many days do employees "
            "have to submit a claim?"
        ),
        height=130,
        label_visibility="collapsed",
    )

    with st.expander("⚙️ Advanced Settings"):
        st.caption(
            "Choose the date used by the verification pipeline "
            "when evaluating document policies."
        )

        question_date = st.date_input(
            "Policy evaluation date",
        )

    verify_clicked = st.button(
        "⚡ Verify Answer",
        type="primary",
        use_container_width=True,
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown("### SYSTEM MODULES")

    st.markdown(
        """
        <div class="muted-text">
        ◈ Document Processing<br><br>
        ◈ Semantic Retrieval<br><br>
        ◈ Contradiction Detection<br><br>
        ◈ Evidence Resolution<br><br>
        ◈ Source Citation
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# RUN VERIFICATION
# ---------------------------------------------------------

if verify_clicked:

    if not uploaded_files:
        st.sidebar.error("Please upload at least one PDF or TXT document.")

    elif not question.strip():
        st.sidebar.error("Please enter a question.")

    else:
        try:
            with st.spinner("TruthGuard is analyzing your documents..."):

                with tempfile.TemporaryDirectory() as temp_dir:

                    file_paths = []

                    for index, uploaded_file in enumerate(uploaded_files):

                        safe_name = Path(uploaded_file.name).name

                        destination = (
                            Path(temp_dir) / f"{index}_{safe_name}"
                        )

                        destination.write_bytes(uploaded_file.getvalue())

                        file_paths.append(destination)

                    result = run_pipeline(
                        file_paths=file_paths,
                        question=question.strip(),
                        question_date=question_date.isoformat(),
                    )

                    st.session_state["truthguard_result"] = result
                    st.session_state["truthguard_question"] = question.strip()
                    st.session_state["truthguard_document_names"] = [
                        file.name for file in uploaded_files
                    ]

            st.sidebar.success("Verification completed!")

        except Exception as exc:
            st.sidebar.error("Verification failed.")
            st.exception(exc)


# ---------------------------------------------------------
# MAIN DASHBOARD HEADER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="eyebrow">✦ INTELLIGENT DOCUMENT VERIFICATION</div>
    <h1 class="main-title">TruthGuard Dashboard</h1>
    <div class="main-subtitle">
        Analyze documents. Detect contradictions.
        Verify answers with evidence.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# LOAD RESULT FROM SESSION
# ---------------------------------------------------------

result = st.session_state.get("truthguard_result")

document_names = st.session_state.get(
    "truthguard_document_names", []
)

if result:

    status = result.get("status", "unknown")

    if status == "answered":
        status_text = "RESOLUTION PRODUCED"
    elif status == "unresolved":
        status_text = "CONFLICT UNRESOLVED"
    elif status == "insufficient_evidence":
        status_text = "INSUFFICIENT EVIDENCE"
    else:
        status_text = "REVIEW REQUIRED"

    evidence = result.get("evidence", [])
    contradictions = result.get("contradictions", [])
    citations = result.get("citations", [])

else:

    status = "waiting"
    status_text = "AWAITING DOCUMENTS"
    evidence = []
    contradictions = []
    citations = []


# ---------------------------------------------------------
# STATUS + METRICS
# ---------------------------------------------------------

st.markdown(
    f'<div class="status-pill">● {safe_text(status_text)}</div>',
    unsafe_allow_html=True,
)

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    render_metric(
        "Documents",
        len(document_names),
        "Uploaded for analysis",
    )

with metric2:
    render_metric(
        "Evidence Retrieved",
        len(evidence),
        "Relevant evidence chunks",
    )

with metric3:
    render_metric(
        "Conflicts Detected",
        len(contradictions),
        "Potential contradictions",
    )

with metric4:
    status_value = "Resolved" if status == "answered" else (
        "Pending" if status == "waiting" else "Review"
    )

    render_metric(
        "Verification Status",
        status_value,
        "Current verification state",
    )


st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# THREE MAIN DASHBOARD PANELS
# ---------------------------------------------------------

col1, col2, col3 = st.columns(3, gap="medium")


# DOCUMENT REVIEW PANEL

with col1:

    st.markdown(
        """
        <div class="feature-panel">
            <div class="feature-heading">
                📑 DOCUMENT REVIEW
            </div>
            <div class="muted-text">
                Uploaded documents and source information.
            </div>
            <br>
        """,
        unsafe_allow_html=True,
    )

    if document_names:

        for name in document_names:

            st.markdown(
                f"""
                <div class="document-row">
                    📄 {safe_text(name)}
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.markdown(
            '<div class="muted-text">'
            'No documents uploaded yet. Use the left panel to import PDF or TXT files.'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# VERIFICATION TRACKER PANEL

with col2:

    st.markdown(
        """
        <div class="feature-panel">
            <div class="feature-heading">
                🧠 VERIFICATION TRACKER
            </div>
            <div class="muted-text">
                Monitor the document verification pipeline.
            </div>
            <br>
        """,
        unsafe_allow_html=True,
    )

    modules = [
        ("Document Processing", bool(document_names)),
        ("Semantic Retrieval", bool(evidence)),
        ("Contradiction Detection", bool(result)),
        ("Evidence Resolution", status == "answered"),
    ]

    for module, completed in modules:

        indicator = "🟣" if completed else "⚪"
        label = "Completed" if completed else "Waiting"

        st.markdown(
            f"""
            <div class="document-row">
                {indicator} <b>{safe_text(module)}</b>
                <span style="float:right;color:#c8a5ff;">
                    {label}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# DOCUMENT COMPARISON PANEL

with col3:

    st.markdown(
        """
        <div class="feature-panel">
            <div class="feature-heading">
                ⚖️ DOCUMENT COMPARISON
            </div>
            <div class="muted-text">
                Compare conflicting information across sources.
            </div>
            <br>
        """,
        unsafe_allow_html=True,
    )

    if contradictions:

        st.markdown(
            f"""
            <div class="document-row">
                <span style="color:#e77cff;font-weight:800;">
                    {len(contradictions)}
                </span>
                potential conflict(s) detected.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="muted-text">'
            'Scroll to the Contradiction Analysis section below '
            'to inspect each conflicting claim.'
            '</div>',
            unsafe_allow_html=True,
        )

    elif result:

        st.markdown(
            """
            <div class="document-row">
                🟣 No contradictions detected by the current rules.
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="muted-text">
                Upload documents and run verification to compare
                claims across different sources.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# VERIFICATION RESULTS
# ---------------------------------------------------------

if result:

    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="panel-title">✦ VERIFICATION ANALYSIS</div>',
        unsafe_allow_html=True,
    )

    question_text = st.session_state.get(
        "truthguard_question", ""
    )

    left, right = st.columns([1.6, 1], gap="large")

    with left:

        st.markdown(
            f"""
            <div class="answer-panel">
                <div class="answer-label">YOUR QUESTION</div>
                <div style="color:#eee8ff;font-size:16px;">
                    {safe_text(question_text)}
                </div>
                <br>
                <div class="answer-label">TRUTHGUARD ANSWER</div>
                <div class="answer-text">
                    {safe_text(
                        result.get("answer")
                        or "No verified answer available."
                    )}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if result.get("reason"):

            st.markdown(
                f"""
                <div class="muted-text" style="margin-top:15px;">
                    <b>Resolution explanation:</b>
                    {safe_text(result["reason"])}
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:

        st.markdown(
            """
            <div class="feature-panel">
                <div class="feature-heading">
                    📊 ANALYSIS SUMMARY
                </div>
            """,
            unsafe_allow_html=True,
        )

        st.metric("Documents Analyzed", len(document_names))
        st.metric("Evidence Chunks Retrieved", len(evidence))
        st.metric("Potential Contradictions", len(contradictions))

        st.markdown("</div>", unsafe_allow_html=True)


    # -----------------------------------------------------
    # CONTRADICTION ANALYSIS
    # -----------------------------------------------------

    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="panel-title">⚡ CONTRADICTION ANALYSIS</div>',
        unsafe_allow_html=True,
    )

    if contradictions:

        for number, conflict in enumerate(contradictions, start=1):

            claim1, claim2 = st.columns(2, gap="medium")

            with claim1:

                st.markdown(
                    f"""
                    <div class="feature-panel">
                        <div class="answer-label">
                            CLAIM {number} — SOURCE 1
                        </div>
                        <div style="color:#f4eaff;line-height:1.7;">
                            {safe_text(conflict.get("claim_1", ""))}
                        </div>
                        <br>
                        <div class="muted-text">
                            DOCUMENT: {safe_text(conflict.get("source_1", "Unknown"))}
                            <br>
                            PAGE: {safe_text(conflict.get("page_1", "Unknown"))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with claim2:

                st.markdown(
                    f"""
                    <div class="feature-panel">
                        <div class="answer-label">
                            CONFLICTING CLAIM — SOURCE 2
                        </div>
                        <div style="color:#f4eaff;line-height:1.7;">
                            {safe_text(conflict.get("claim_2", ""))}
                        </div>
                        <br>
                        <div class="muted-text">
                            DOCUMENT: {safe_text(conflict.get("source_2", "Unknown"))}
                            <br>
                            PAGE: {safe_text(conflict.get("page_2", "Unknown"))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.write("")

    else:

        st.info(
            "No contradictions were detected by the current verification rules."
        )


    # -----------------------------------------------------
    # EVIDENCE NETWORK
    # -----------------------------------------------------

    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="panel-title">✧ EVIDENCE NETWORK</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="feature-panel" style="text-align:center;">
            <div class="answer-label">CENTRAL VERIFICATION ENGINE</div>
            <div style="
                display:inline-block;
                margin:15px;
                padding:14px 28px;
                border-radius:30px;
                color:white;
                font-weight:900;
                background:linear-gradient(90deg,#983eff,#dc4bd7,#20c8e8);
                box-shadow:0 0 25px rgba(196,76,255,0.45);
            ">
                TRUTHGUARD AI
            </div>
            <div style="color:#d36cff;font-size:24px;">↕</div>
            <div class="answer-label">CONNECTED EVIDENCE SOURCES</div>
        """,
        unsafe_allow_html=True,
    )

    if evidence:

        evidence_columns = st.columns(min(len(evidence), 4))

        for index, item in enumerate(evidence):

            with evidence_columns[index % len(evidence_columns)]:

                source = safe_text(item.get("source", "Unknown source"))
                page = safe_text(item.get("page_number", "Unknown"))

                st.markdown(
                    f"""
                    <div class="document-row" style="text-align:center;">
                        📄 {source}<br>
                        <span style="color:#a9a0c9;">Page {page}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:

        st.markdown(
            '<div class="muted-text">No evidence sources available.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


    # -----------------------------------------------------
    # RETRIEVED EVIDENCE
    # -----------------------------------------------------

    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="panel-title">📚 RETRIEVED EVIDENCE</div>',
        unsafe_allow_html=True,
    )

    if evidence:

        for number, item in enumerate(evidence, start=1):

            source = item.get("source", "Unknown source")
            page = item.get("page_number", "Unknown")

            with st.expander(
                f"Evidence {number}  |  {source}  |  Page {page}"
            ):

                st.write("**Source:**", source)
                st.write("**Page:**", page)

                if "similarity_score" in item:

                    st.write(
                        "**Similarity score:**",
                        round(item["similarity_score"], 3),
                    )

                st.write(item.get("text", ""))

    else:

        st.info("No retrieved evidence is available.")


    # -----------------------------------------------------
    # SOURCE CITATIONS
    # -----------------------------------------------------

    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="panel-title">🔗 SOURCE CITATIONS</div>',
        unsafe_allow_html=True,
    )

    if citations:

        for citation in citations:

            source = safe_text(
                citation.get("source", "Unknown source")
            )

            page = safe_text(
                citation.get("page_number", "Unknown")
            )

            st.markdown(
                f"""
                <div class="document-row">
                    📄 <b>{source}</b>
                    <span style="color:#aaa0c7;"> — Page {page}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.info("No citations are available.")


# ---------------------------------------------------------
# INITIAL / EMPTY DASHBOARD
# ---------------------------------------------------------

else:

    st.markdown(
        """
        <div class="answer-panel">
            <div class="feature-heading">
                ✦ WELCOME TO TRUTHGUARD AI
            </div>

            <div style="
                color:#d4cce9;
                font-size:16px;
                line-height:1.8;
            ">
                Your intelligent document verification workspace is ready.
                Upload your policy documents, enter a question in the
                left panel, and start your first verification.
            </div>

            <br>

            <div style="display:flex;flex-wrap:wrap;gap:10px;">
                <span class="document-row">📄 Document Processing</span>
                <span class="document-row">🔍 Semantic Retrieval</span>
                <span class="document-row">⚡ Contradiction Detection</span>
                <span class="document-row">🧠 Evidence Resolution</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="
        text-align:center;
        color:#777493;
        font-size:12px;
        padding:15px;
    ">
        TRUTHGUARD AI · INTELLIGENT DOCUMENT VERIFICATION
        <br><br>
        Rule-based contradiction detection · Evidence-backed answers · Source citations
    </div>
    """,
    unsafe_allow_html=True,
)