import html
import tempfile
from pathlib import Path

import streamlit as st

from document_processor import extract_text
from qna_generator import generate_qna_multilingual
from excel_writer import create_qna_workbook


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="QnAForge",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="auto",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --qf-blue: #2563eb;
    --qf-purple: #7c3aed;
    --qf-cyan: #0ea5e9;
    --qf-border: rgba(128,128,128,0.20);
    --qf-soft: rgba(128,128,128,0.07);
}

/* Main width */
.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    border-right: 1px solid var(--qf-border);
}

section[data-testid="stSidebar"] > div {
    padding-top: 2rem;
}

/* Hero */
.qf-hero {
    padding: 2.4rem 2.5rem;
    margin-bottom: 2rem;
    border-radius: 26px;
    border: 1px solid rgba(37,99,235,0.22);
    background:
        radial-gradient(
            circle at 85% 20%,
            rgba(124,58,237,0.22),
            transparent 35%
        ),
        radial-gradient(
            circle at 10% 90%,
            rgba(37,99,235,0.18),
            transparent 35%
        ),
        var(--secondary-background-color);
    box-shadow: 0 15px 45px rgba(0,0,0,0.08);
}

.qf-hero-icon {
    font-size: 2.7rem;
    line-height: 1;
    margin-bottom: 0.5rem;
}

.qf-hero-title {
    font-size: 2.7rem;
    font-weight: 850;
    letter-spacing: -1.5px;
    line-height: 1.1;
}

.qf-hero-title span {
    background: linear-gradient(
        90deg,
        var(--qf-blue),
        var(--qf-purple)
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.qf-hero-subtitle {
    margin-top: 0.8rem;
    font-size: 1.05rem;
    opacity: 0.75;
    max-width: 720px;
}

.qf-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin-top: 1.2rem;
}

.qf-badge {
    display: inline-block;
    padding: 0.42rem 0.8rem;
    border-radius: 999px;
    border: 1px solid var(--qf-border);
    background: var(--qf-soft);
    font-size: 0.82rem;
}

/* Section headings */
.qf-section-title {
    font-size: 1.45rem;
    font-weight: 800;
    margin-top: 0.4rem;
}

.qf-section-subtitle {
    margin-top: 0.25rem;
    margin-bottom: 1.2rem;
    opacity: 0.68;
}

/* Upload card */
.qf-upload-card {
    padding: 1.4rem;
    border-radius: 20px;
    border: 1px solid var(--qf-border);
    background: var(--secondary-background-color);
    margin-bottom: 1.5rem;
}

/* Configuration */
.qf-config {
    padding: 1.1rem 1.25rem;
    border-radius: 18px;
    border: 1px solid var(--qf-border);
    background: var(--qf-soft);
    margin: 1rem 0 1.2rem 0;
}

/* Q&A card */
.qf-qcard {
    padding: 1.25rem 1.35rem;
    margin: 0 0 1rem 0;
    border-radius: 18px;
    border: 1px solid var(--qf-border);
    background: var(--secondary-background-color);
    box-shadow: 0 5px 18px rgba(0,0,0,0.045);
}

.qf-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: linear-gradient(
        135deg,
        var(--qf-blue),
        var(--qf-purple)
    );
    color: white;
    font-weight: 800;
    margin-bottom: 0.8rem;
}

.qf-label {
    font-size: 0.76rem;
    font-weight: 750;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.55;
    margin-top: 0.55rem;
}

.qf-question {
    font-size: 1rem;
    font-weight: 700;
    line-height: 1.55;
    margin-top: 0.25rem;
}

.qf-answer {
    font-size: 0.94rem;
    line-height: 1.65;
    opacity: 0.88;
    margin-top: 0.25rem;
}

/* Footer */
.qf-footer {
    text-align: center;
    opacity: 0.55;
    padding: 2rem 0 1rem 0;
    font-size: 0.82rem;
}

/* Buttons */
.stButton > button {
    border-radius: 12px;
    font-weight: 700;
}

/* Mobile */
@media (max-width: 768px) {

    .block-container {
        padding-left: 0.9rem;
        padding-right: 0.9rem;
        padding-top: 1rem;
    }

    .qf-hero {
        padding: 1.5rem 1.15rem;
        border-radius: 20px;
    }

    .qf-hero-icon {
        font-size: 2.2rem;
    }

    .qf-hero-title {
        font-size: 2rem;
    }

    .qf-hero-subtitle {
        font-size: 0.9rem;
    }

    .qf-badge {
        font-size: 0.72rem;
        padding: 0.32rem 0.62rem;
    }

    .qf-section-title {
        font-size: 1.2rem;
    }

    .qf-qcard {
        padding: 1rem;
        border-radius: 15px;
    }

    .qf-question {
        font-size: 0.94rem;
    }

    .qf-answer {
        font-size: 0.88rem;
    }
}

@media (max-width: 430px) {

    .qf-hero {
        padding: 1.15rem 0.95rem;
    }

    .qf-hero-title {
        font-size: 1.7rem;
    }

    .qf-qcard {
        padding: 0.85rem;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# API KEY
# ============================================================

try:
    api_key = st.secrets["GEMINI_API_KEY"]

except Exception:
    st.error("⚠️ Gemini API key is not configured.")
    st.info(
        "Add GEMINI_API_KEY to .streamlit/secrets.toml "
        "for local use."
    )
    st.stop()


# ============================================================
# HERO
# ============================================================

st.html(
    """
<div class="qf-hero">
    <div class="qf-hero-icon">🌐</div>
    <div class="qf-hero-title">
        <span>QnAForge</span>
    </div>
    <div class="qf-hero-subtitle">
        AI-powered multilingual Question-Answer generation
        from your documents.
    </div>
    <div class="qf-badges">
        <span class="qf-badge">✨ AI Powered</span>
        <span class="qf-badge">🇬🇧 English</span>
        <span class="qf-badge">🇮🇳 Hindi</span>
        <span class="qf-badge">🇮🇳 Marathi</span>
    </div>
</div>
"""
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Generation Settings")
    st.caption("Customize your Q&A generation.")

    model = st.selectbox(
        "AI Model",
        [
            "gemini-3.5-flash-lite",
            "gemini-3.5-flash",
        ],
        index=0,
    )

    qna_count = st.slider(
        "Q&A pairs",
        min_value=5,
        max_value=20,
        value=5,
        step=5,
    )

    difficulty = st.selectbox(
        "Difficulty",
        [
            "Mixed",
            "Easy",
            "Medium",
            "Advanced",
        ],
    )

    question_type = st.selectbox(
        "Question type",
        [
            "Mixed",
            "Conceptual",
            "Definition",
            "Short Answer",
        ],
    )

    st.divider()

    st.caption("🌍 Output languages")

    st.write("🇬🇧 English")
    st.write("🇮🇳 Hindi")
    st.write("🇮🇳 Marathi")

    st.divider()

    st.caption("🔐 API key secured through Streamlit Secrets")


# ============================================================
# UPLOAD SECTION
# ============================================================

st.html(
    """
<div class="qf-section-title">
    📄 Upload your document
</div>

<div class="qf-section-subtitle">
    Upload a PDF, DOCX or TXT file and QnAForge will create
    meaningful, context-aware questions and answers.
</div>
"""
)

st.html(
    """
<div class="qf-upload-card">
    <strong>Supported formats:</strong>
    PDF, DOCX, TXT
</div>
"""
)

uploaded_file = st.file_uploader(
    "Upload",
    type=["pdf", "docx", "txt"],
    label_visibility="collapsed",
)


# ============================================================
# DOCUMENT PROCESSING
# ============================================================

if uploaded_file is not None:

    suffix = Path(uploaded_file.name).suffix.lower()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as tmp:

        tmp.write(uploaded_file.getbuffer())
        temp_path = tmp.name

    try:

        text = extract_text(temp_path)

    except Exception as exc:

        st.error(f"Could not read the document: {exc}")
        st.stop()

    finally:

        try:
            Path(temp_path).unlink()
        except Exception:
            pass

    if not text.strip():

        st.warning(
            "The uploaded document does not contain readable text."
        )
        st.stop()

    word_count = len(text.split())
    character_count = len(text)

    st.html(
        f"""
<div class="qf-config">
    <strong>📄 {html.escape(uploaded_file.name)}</strong><br>
    <span style="opacity:0.7;">
        {word_count:,} words · {character_count:,} characters
    </span>
</div>
"""
    )

    # Preview
    with st.expander("👀 Preview extracted text"):

        preview = text[:5000]

        st.text_area(
            "Extracted text",
            preview,
            height=220,
            label_visibility="collapsed",
        )

    # Generation settings summary
    st.html(
        f"""
<div class="qf-config">
    <strong>Generation configuration</strong><br>
    Model: {html.escape(model)}
    &nbsp;·&nbsp;
    Q&A pairs: {qna_count}
    &nbsp;·&nbsp;
    Difficulty: {html.escape(difficulty)}
    &nbsp;·&nbsp;
    Type: {html.escape(question_type)}
    <br>
    Languages: English · Hindi · Marathi
</div>
"""
    )

    # ========================================================
    # GENERATE
    # ========================================================

    generate_clicked = st.button(
        "✨ Generate Multilingual Q&A",
        type="primary",
        use_container_width=True,
    )

    if generate_clicked:

        progress = st.progress(0)
        status = st.empty()

        def update_progress(value, message):

            progress.progress(
                max(0, min(100, int(value)))
            )

            status.info(message)

        try:

            result = generate_qna_multilingual(
                text=text,
                api_key=api_key,
                model=model,
                qna_per_chunk=qna_count,
                max_chars=10000,
                progress_callback=update_progress,
            )

            st.session_state["result"] = result

            progress.progress(100)
            status.success(
                "✓ Q&A generation completed successfully."
            )

        except Exception as exc:

            progress.empty()
            status.empty()

            st.error(
                f"Generation failed: {exc}"
            )


# ============================================================
# RESULTS
# ============================================================

if "result" in st.session_state:

    data = st.session_state["result"]

    st.divider()

    st.html(
        """
<div class="qf-section-title">
    📚 Review your results
</div>

<div class="qf-section-subtitle">
    Review the generated Q&A in each language before downloading.
</div>
"""
    )

    # --------------------------------------------------------
    # LANGUAGE COUNTS
    # --------------------------------------------------------

    english_count = len(data.get("English", []))
    hindi_count = len(data.get("Hindi", []))
    marathi_count = len(data.get("Marathi", []))

    a, b, c = st.columns(3)

    a.metric(
        "🇬🇧 English",
        english_count,
    )

    b.metric(
        "🇮🇳 Hindi",
        hindi_count,
    )

    c.metric(
        "🇮🇳 Marathi",
        marathi_count,
    )

    if (
        english_count
        == hindi_count
        == marathi_count
    ):

        st.success(
            "✓ All three language sets are aligned."
        )

    # ========================================================
    # LANGUAGE TABS
    # ========================================================

    tabs = st.tabs(
        [
            "🇬🇧 English",
            "🇮🇳 Hindi",
            "🇮🇳 Marathi",
        ]
    )

    for tab, language in zip(
        tabs,
        [
            "English",
            "Hindi",
            "Marathi",
        ],
    ):

        with tab:

            items = data.get(language, [])

            if not items:

                st.info(
                    f"No {language} Q&A was generated."
                )
                continue

            for i, item in enumerate(
                items,
                1,
            ):

                question = html.escape(
                    str(
                        item.get(
                            "question",
                            "",
                        )
                    ).strip()
                )

                answer = html.escape(
                    str(
                        item.get(
                            "answer",
                            "",
                        )
                    ).strip()
                )

                st.html(
                    f"""
<div class="qf-qcard">
    <div class="qf-number">{i}</div>

    <div class="qf-label">
        Question
    </div>

    <div class="qf-question">
        {question}
    </div>

    <div class="qf-label">
        Answer
    </div>

    <div class="qf-answer">
        {answer}
    </div>
</div>
"""
                )

    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.divider()

    st.html(
        """
<div class="qf-section-title">
    📥 Download your Q&A
</div>

<div class="qf-section-subtitle">
    Download the complete multilingual workbook in Excel format.
</div>
"""
    )

    try:

        output_path = Path("QnAForge_QnA.xlsx")

        create_qna_workbook(
            data,
            str(output_path),
        )

        with open(
            output_path,
            "rb",
        ) as file:

            st.download_button(
                label="📥 Download QnAForge_QnA.xlsx",
                data=file,
                file_name="QnAForge_QnA.xlsx",
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),
                use_container_width=True,
            )

    except Exception as exc:

        st.error(
            f"Could not create Excel workbook: {exc}"
        )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
<div class="qf-footer">
    🌐 <strong>QnAForge</strong>
    · Multilingual AI Question-Answer Generation
    <br>
    English · Hindi · Marathi
</div>
"""
)