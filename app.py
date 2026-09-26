import os, tempfile
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from document_processor import extract_text
from qna_generator import generate_qna_multilingual
from excel_writer import create_qna_workbook

load_dotenv()
st.set_page_config(page_title="LinguaQ AI", page_icon="🌐", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:2rem}
.hero{padding:1.7rem 2rem;border:1px solid rgba(128,128,128,.25);border-radius:22px;background:linear-gradient(135deg,rgba(99,102,241,.13),rgba(14,165,233,.08));margin-bottom:1.2rem}
.hero h1{margin:0;font-size:2.35rem}.hero p{margin:.5rem 0 0;opacity:.8}
.q-card{border:1px solid rgba(128,128,128,.22);border-radius:14px;padding:1rem;margin-bottom:.8rem}
.q-label{font-size:.78rem;font-weight:700;opacity:.65}.q-text{font-size:1.02rem;font-weight:650;margin:.25rem 0 .55rem}.a-text{line-height:1.55;opacity:.9}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🌐 LinguaQ AI</h1><p>Upload. Understand. Generate. Translate.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Generation Settings")
    api_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY",""), type="password")
    model = st.selectbox("AI Model", ["gemini-3.5-flash-lite","gemini-3.5-flash"])
    qna_count = st.slider("Q&A pairs", 5, 20, 5, step=5)
    difficulty = st.selectbox("Difficulty", ["Mixed","Easy","Medium","Advanced"])
    question_type = st.selectbox("Question type", ["Mixed","Conceptual","Definition","Short Answer"])
    st.divider()
    st.caption("Output languages")
    st.write("🇬🇧 English")
    st.write("🇮🇳 Hindi")
    st.write("🇮🇳 Marathi")

st.subheader("① Upload your document")
uploaded = st.file_uploader("Supported formats: PDF, DOCX, TXT", type=["pdf","docx","txt"])

if uploaded:
    suffix = Path(uploaded.name).suffix.lower()
    temp_input = Path(tempfile.gettempdir()) / f"linguaq_input{suffix}"
    temp_input.write_bytes(uploaded.getvalue())

    try:
        text = extract_text(str(temp_input))
    except Exception as exc:
        st.error(f"Could not read the document: {exc}")
        st.stop()

    if not text.strip():
        st.error("No readable text was found in the document.")
        st.stop()

    c1,c2,c3 = st.columns(3)
    c1.metric("Document", uploaded.name)
    c2.metric("Characters", f"{len(text):,}")
    c3.metric("Estimated words", f"{len(text.split()):,}")

    with st.expander("👀 Preview extracted text"):
        st.text_area("Extracted text", text[:5000], height=180)

    st.subheader("② Configure generation")
    st.info(f"Up to **{qna_count} Q&A pairs** • Difficulty: **{difficulty}** • Type: **{question_type}**")

    st.subheader("③ Generate multilingual Q&A")
    if st.button("✨ Generate Q&A", type="primary", use_container_width=True):
        if not api_key.strip():
            st.error("Enter your Gemini API key in the sidebar.")
            st.stop()

        progress = st.progress(0)
        status = st.empty()

        def update_progress(value, message):
            progress.progress(max(0,min(100,value)))
            status.write(message)

        try:
            result = generate_qna_multilingual(
                text=text, api_key=api_key.strip(), model=model,
                qna_per_chunk=qna_count, max_chars=10000,
                progress_callback=update_progress
            )
            final_data = {k: result.get(k,[])[:qna_count] for k in ["English","Hindi","Marathi"]}
            if not final_data["English"]:
                raise ValueError("No English Q&A was generated.")
            if not final_data["Hindi"] or not final_data["Marathi"]:
                raise ValueError(f"Multilingual generation incomplete: English={len(final_data['English'])}, Hindi={len(final_data['Hindi'])}, Marathi={len(final_data['Marathi'])}.")

            output_path = Path(tempfile.gettempdir()) / "LinguaQ_QnA.xlsx"
            create_qna_workbook(final_data, str(output_path))
            st.session_state["result"] = final_data
            st.session_state["excel"] = output_path.read_bytes()
            progress.progress(100)
            status.success("✓ Generated, translated, validated and exported.")
        except Exception as exc:
            st.error(f"Generation failed: {exc}")

if "result" in st.session_state:
    data = st.session_state["result"]
    st.subheader("④ Review results")
    a,b,c = st.columns(3)
    a.metric("🇬🇧 English",len(data["English"]))
    b.metric("🇮🇳 Hindi",len(data["Hindi"]))
    c.metric("🇮🇳 Marathi",len(data["Marathi"]))

    if len(data["English"]) == len(data["Hindi"]) == len(data["Marathi"]):
        st.success("✓ All three language sets are aligned.")

    tabs = st.tabs(["🇬🇧 English","🇮🇳 Hindi","🇮🇳 Marathi"])
    for tab, lang in zip(tabs, ["English","Hindi","Marathi"]):
        with tab:
            for i,item in enumerate(data[lang],1):
                st.markdown(f'<div class="q-card"><div class="q-label">QUESTION {i}</div><div class="q-text">{item["question"]}</div><div class="q-label">ANSWER</div><div class="a-text">{item["answer"]}</div></div>', unsafe_allow_html=True)

    st.subheader("⑤ Download")
    st.download_button("📥 Download Excel Workbook", data=st.session_state["excel"], file_name="LinguaQ_QnA.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

st.divider()
st.caption("LinguaQ AI • Python • Gemini AI • Streamlit • OpenPyXL • English • Hindi • Marathi")
