import os
import io
import streamlit as st
from fastapi import UploadFile
from web.service import process_pipeline
from prop.schema import Opportunity
from prop.scoring_bid import evaluate_opportunity

st.set_page_config(page_title="Proposal Bot", page_icon="📄", layout="wide")

st.title("📄 Proposal Bot – Streamlit Edition")
st.write("Upload a PWS/SoW (pdf/docx/md/txt) and optional RFP YAML to parse requirements, draft outlines, build a compliance matrix, and generate a branded DOCX.")

with st.sidebar:
    st.header("Settings")
    brand = st.text_input("Brand Name", os.getenv("ORAN_BRAND_NAME", "Oran Inc."))
    tagline = st.text_input("Header Tagline", os.getenv("ORAN_HEADER_RIGHT", "IT Services"))
    logo_file = st.file_uploader("Logo (PNG optional)", type=["png","jpg","jpeg"], key="logo")
    apply_brand = st.button("Apply Branding")
    if apply_brand:
        os.environ["ORAN_BRAND_NAME"] = brand
        os.environ["ORAN_HEADER_RIGHT"] = tagline
        if logo_file:
            tmp_logo = os.path.join("web","static","oran_logo.png")
            os.makedirs(os.path.dirname(tmp_logo), exist_ok=True)
            with open(tmp_logo, "wb") as f:
                f.write(logo_file.read())
        st.success("Brand settings applied for this session.")

col1, col2 = st.columns(2)
with col1:
    pws_upload = st.file_uploader("PWS / SoW Document", type=["pdf","docx","md","txt"], accept_multiple_files=False)
with col2:
    rfp_upload = st.file_uploader("RFP YAML (optional)", type=["yaml","yml"], accept_multiple_files=False)

run_btn = st.button("Run Pipeline", type="primary", use_container_width=True)

@st.cache_data(show_spinner=False)
def _cached_pipeline(pws_bytes: bytes, pws_name: str, rfp_bytes: bytes | None, rfp_name: str | None, brand_name: str, tagline: str):
    """Wrap process_pipeline for caching identical inputs within session."""
    # Materialize temp UploadFile-like objects
    class _Upload(UploadFile):
        def __init__(self, name: str, data: bytes):
            self.filename = name
            self.file = io.BytesIO(data)
    pws_u = _Upload(pws_name, pws_bytes)
    rfp_u = _Upload(rfp_name, rfp_bytes) if (rfp_bytes and rfp_name) else None
    # Apply branding env (transient for build)
    orig_brand = os.environ.get("ORAN_BRAND_NAME")
    orig_tag = os.environ.get("ORAN_HEADER_RIGHT")
    os.environ["ORAN_BRAND_NAME"] = brand_name
    os.environ["ORAN_HEADER_RIGHT"] = tagline
    try:
        return st.run(process_pipeline(pws_u, rfp_u))  # type: ignore
    finally:
        if orig_brand is None:
            os.environ.pop("ORAN_BRAND_NAME", None)
        else:
            os.environ["ORAN_BRAND_NAME"] = orig_brand
        if orig_tag is None:
            os.environ.pop("ORAN_HEADER_RIGHT", None)
        else:
            os.environ["ORAN_HEADER_RIGHT"] = orig_tag

if run_btn:
    if not pws_upload:
        st.error("Please upload a PWS/SoW file.")
    else:
        with st.spinner("Processing pipeline..."):
            pws_bytes = pws_upload.read()
            rfp_bytes = rfp_upload.read() if rfp_upload else None
            result = _cached_pipeline(pws_bytes, pws_upload.name, rfp_bytes, rfp_upload.name if rfp_upload else None, brand, tagline)
        st.success("Pipeline complete.")
        st.subheader("Outputs")
        outputs = result.get("outputs", {})
        dl_cols = st.columns(5)
        keys = ["requirements","outlines","flowchart","gantt","docx"]
        for idx,k in enumerate(keys):
            path = outputs.get(k)
            if path and os.path.exists(path):
                with open(path, "rb") as f:
                    label = k.upper()
                    dl_cols[idx].download_button(label=label, data=f.read(), file_name=os.path.basename(path))
        st.json(result.get("section6_coverage"))

        # Quick scoring placeholder (user can expand later)
        st.subheader("Opportunity Scoring (Manual Draft)")
        opp = Opportunity()
        score_out = evaluate_opportunity(opp)
        st.write(score_out.get("decision"))
        st.write("Total Score:", score_out.get("total"))

st.markdown("---")
st.caption("Session-based build. For production, deploy FastAPI separately and call via HTTP from Streamlit for scalability.")
