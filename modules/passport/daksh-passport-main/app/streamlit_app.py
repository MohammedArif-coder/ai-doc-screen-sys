import os
from pathlib import Path

import requests
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DAKSH Passport Screening",
    page_icon="🛂",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 36px;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .info-box {
        padding: 18px;
        border-radius: 12px;
        background-color: #f8fafc;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }

    .mrz-box {
        font-family: monospace;
        font-size: 15px;
        word-break: break-all;
        background-color: #f3f4f6;
        padding: 14px;
        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_name(value):
    return str(value).replace("_", " ").title()


def show_status_badge(status):
    if status == "manual_review":
        st.warning("🟡 MANUAL REVIEW REQUIRED")

    elif status == "no_consistency_issue_detected":
        st.success("🟢 NO CONSISTENCY ISSUE DETECTED")

    else:
        st.info(
            f"Status: {str(status).replace('_', ' ').upper()}"
        )


def show_consistency_status(status):
    if status == "MATCH":
        st.success("MATCH")

    elif status == "MISMATCH":
        st.error("MISMATCH")

    elif status == "PARTIAL":
        st.warning("PARTIAL")

    else:
        st.info(status)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🛂 DAKSH Passport Screening System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-assisted identity and document screening'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Configuration")

    api_url = st.text_input(
        "FastAPI URL",
        value="http://127.0.0.1:8000"
    )

    st.divider()

    st.subheader("Pipeline")

    st.write("✅ Image preprocessing")
    st.write("✅ Full-page OCR")
    st.write("✅ Visual field extraction")
    st.write("✅ Dynamic MRZ detection")
    st.write("✅ MRZ parsing")
    st.write("✅ MRZ validation")
    st.write("✅ Visual ↔ MRZ consistency")
    st.write("✅ Image quality")
    st.write("✅ Metadata")
    st.write("✅ ELA analysis")


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-title">📄 Upload Passport</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Upload a passport image",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear passport image for screening."
)


if uploaded_file is not None:

    preview_col, info_col = st.columns(
        [1.3, 1]
    )

    with preview_col:

        st.image(
            uploaded_file,
            caption="Uploaded Passport",
            use_container_width=True
        )

    with info_col:

        st.markdown(
            '<div class="info-box">',
            unsafe_allow_html=True
        )

        st.write(
            f"**File:** {uploaded_file.name}"
        )

        st.write(
            f"**Type:** {uploaded_file.type}"
        )

        st.write(
            f"**Size:** "
            f"{uploaded_file.size / 1024:.1f} KB"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button(
    "🔍 Analyze Passport",
    type="primary",
    use_container_width=True
)


if analyze:

    if uploaded_file is None:

        st.warning(
            "Please upload a passport image first."
        )

    else:

        endpoint = (
            api_url.rstrip("/")
            + "/api/passport/screen"
        )

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        }

        with st.spinner(
            "Analyzing passport... "
            "OCR and forensic analysis may take some time."
        ):

            try:

                response = requests.post(
                    endpoint,
                    files=files,
                    timeout=300
                )

                if response.status_code != 200:

                    try:
                        error_data = response.json()

                    except Exception:
                        error_data = response.text

                    st.error(
                        f"Backend error: {error_data}"
                    )

                    st.stop()

                data = response.json()

                st.session_state[
                    "screening_result"
                ] = data

                st.session_state[
                    "uploaded_filename"
                ] = uploaded_file.name

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI. "
                    "Make sure Uvicorn is running on port 8000."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The screening request timed out. "
                    "OCR or forensic analysis may still be processing."
                )

            except Exception as exc:

                st.error(
                    f"Unexpected error: {exc}"
                )


# ============================================================
# RESULTS
# ============================================================

if "screening_result" in st.session_state:

    data = st.session_state["screening_result"]

    st.divider()

    # ========================================================
    # OVERALL STATUS
    # ========================================================

    st.markdown(
        '<div class="section-title">🎯 Screening Status</div>',
        unsafe_allow_html=True
    )

    show_status_badge(
        data.get(
            "status",
            "unknown"
        )
    )

    if data.get("reason"):

        st.info(
            data["reason"]
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    summary = data.get(
        "summary",
        {}
    )

    st.markdown(
        '<div class="section-title">📊 Screening Summary</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "MRZ Validation Failures",
            summary.get(
                "mrz_validation_failures",
                0
            )
        )

    with c2:

        st.metric(
            "Field Mismatches",
            summary.get(
                "field_mismatches",
                0
            )
        )

    with c3:

        st.metric(
            "Partial Matches",
            summary.get(
                "partial_matches",
                0
            )
        )


    # ========================================================
    # VISUAL PASSPORT FIELDS
    # ========================================================

    st.markdown(
        '<div class="section-title">📋 Extracted Passport Details</div>',
        unsafe_allow_html=True
    )

    visual_fields = data.get(
        "visual_fields",
        {}
    )

    field_items = list(
        visual_fields.items()
    )

    left_col, right_col = st.columns(2)

    for index, (key, value) in enumerate(
        field_items
    ):

        target_col = (
            left_col
            if index % 2 == 0
            else right_col
        )

        with target_col:

            st.markdown(
                f"**{format_name(key)}**"
            )

            if value:

                st.code(
                    str(value),
                    language=None
                )

            else:

                st.write(
                    "Not detected"
                )


    # ========================================================
    # MRZ INFORMATION
    # ========================================================

    st.markdown(
        '<div class="section-title">🔤 MRZ Information</div>',
        unsafe_allow_html=True
    )

    mrz = data.get(
        "mrz"
    )

    if mrz:

        st.write("**MRZ Line 1**")

        st.code(
            mrz.get(
                "line1",
                ""
            ),
            language=None
        )

        st.write("**MRZ Line 2**")

        st.code(
            mrz.get(
                "line2",
                ""
            ),
            language=None
        )

        with st.expander(
            "View Parsed MRZ"
        ):

            st.json(
                mrz.get(
                    "parsed",
                    {}
                )
            )

    else:

        st.warning(
            "MRZ was not available."
        )


    # ========================================================
    # MRZ VALIDATION
    # ========================================================

    st.markdown(
        '<div class="section-title">✅ MRZ Validation</div>',
        unsafe_allow_html=True
    )

    validation = data.get(
        "mrz_validation",
        {}
    )

    checks = validation.get(
        "checks",
        {}
    )

    if checks:

        for field, check in checks.items():

            if check.get("valid"):

                st.success(
                    f"✅ {format_name(field)} — PASS"
                )

            else:

                st.error(
                    f"❌ {format_name(field)} — FAIL "
                    f"| Expected: {check.get('expected')} "
                    f"| Calculated: {check.get('calculated')}"
                )

    else:

        st.info(
            "No MRZ validation checks available."
        )


    # ========================================================
    # VISUAL ↔ MRZ CONSISTENCY
    # ========================================================

    st.markdown(
        '<div class="section-title">🔎 Visual ↔ MRZ Consistency</div>',
        unsafe_allow_html=True
    )

    consistency = data.get(
        "consistency",
        []
    )

    if consistency:

        for item in consistency:

            field = format_name(
                item.get(
                    "field",
                    ""
                )
            )

            status_value = item.get(
                "status",
                "UNKNOWN"
            )

            visual_value = item.get(
                "visual",
                "-"
            )

            mrz_value = item.get(
                "mrz",
                "-"
            )

            with st.container():

                col1, col2, col3 = st.columns(
                    [2, 1.5, 3]
                )

                with col1:

                    st.write(
                        f"**{field}**"
                    )

                with col2:

                    show_consistency_status(
                        status_value
                    )

                with col3:

                    st.write(
                        f"Visual: `{visual_value}`"
                    )

                    st.write(
                        f"MRZ: `{mrz_value}`"
                    )

    else:

        st.info(
            "No consistency results available."
        )


    # ========================================================
    # FORENSIC ANALYSIS
    # ========================================================

    st.markdown(
        '<div class="section-title">🧪 Forensic Analysis</div>',
        unsafe_allow_html=True
    )

    forensics = data.get(
        "forensics",
        {}
    )

    quality = forensics.get(
        "image_quality",
        {}
    )

    metadata = forensics.get(
        "metadata",
        {}
    )

    ela = forensics.get(
        "ela",
        {}
    )


    # --------------------------------------------------------
    # IMAGE QUALITY
    # --------------------------------------------------------

    st.subheader(
        "📷 Image Quality"
    )

    q1, q2, q3, q4 = st.columns(4)

    with q1:

        st.metric(
            "Resolution",
            (
                f"{quality.get('width', '-')}"
                f" × "
                f"{quality.get('height', '-')}"
            )
        )

    with q2:

        st.metric(
            "Sharpness",
            quality.get(
                "sharpness",
                "-"
            )
        )

    with q3:

        st.metric(
            "Brightness",
            quality.get(
                "brightness",
                "-"
            )
        )

    with q4:

        st.metric(
            "Overall",
            quality.get(
                "overall",
                "-"
            )
        )

    if quality.get("warnings"):

        for warning in quality[
            "warnings"
        ]:

            st.warning(
                f"⚠ {warning}"
            )

    else:

        st.success(
            "No image-quality warnings."
        )


    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    st.subheader(
        "🧾 Metadata"
    )

    m1, m2, m3 = st.columns(3)

    with m1:

        st.write(
            f"**Format:** "
            f"{metadata.get('format', '-')}"
        )

    with m2:

        exif_status = (
            "Present"
            if metadata.get(
                "exif_present",
                False
            )
            else "Not present"
        )

        st.write(
            f"**EXIF:** {exif_status}"
        )

    with m3:

        st.write(
            f"**Software:** "
            f"{metadata.get('software') or 'None'}"
        )

    with st.expander(
        "View Complete Metadata"
    ):

        st.json(
            metadata
        )


    # --------------------------------------------------------
    # ELA
    # --------------------------------------------------------

    st.subheader(
        "🔬 Error Level Analysis"
    )

    e1, e2, e3 = st.columns(3)

    with e1:

        st.metric(
            "Mean ELA",
            ela.get(
                "mean",
                "-"
            )
        )

    with e2:

        st.metric(
            "99th Percentile",
            ela.get(
                "percentile_99",
                "-"
            )
        )

    with e3:

        st.metric(
            "Anomaly Level",
            ela.get(
                "anomaly_level",
                "-"
            )
        )


           # --------------------------------------------------------
    # ELA VISUALIZATION
    # --------------------------------------------------------

    st.subheader("🔬 ELA Visualization")

    suspicious_regions = ela.get(
        "suspicious_regions",
        []
    )

    if suspicious_regions:

        annotated_original_path = ela.get(
            "annotated_original_path"
        )

        annotated_heatmap_path = ela.get(
            "annotated_heatmap_path"
        )

        if annotated_original_path:

            original_path = Path(
                annotated_original_path
            )

            if not original_path.is_absolute():
                original_path = (
                    Path.cwd() / original_path
                )

            if original_path.exists():

                st.image(
                    str(original_path),
                    caption="Passport with ELA Regions",
                    use_container_width=True
                )

        if annotated_heatmap_path:

            heatmap_path = Path(
                annotated_heatmap_path
            )

            if not heatmap_path.is_absolute():
                heatmap_path = (
                    Path.cwd() / heatmap_path
                )

            if heatmap_path.exists():

                with st.expander(
                    "View Annotated ELA Heatmap"
                ):

                    st.image(
                        str(heatmap_path),
                        caption="ELA Heatmap",
                        use_container_width=True
                    )

        st.subheader("📍 Suspicious Regions")

        st.write(
            f"Detected regions: "
            f"{len(suspicious_regions)}"
        )

        for index, region in enumerate(
            suspicious_regions,
            start=1
        ):

            st.write(
                f"**Region {index}** — "
                f"x={region.get('x')}, "
                f"y={region.get('y')}, "
                f"width={region.get('width')}, "
                f"height={region.get('height')}, "
                f"area={region.get('area')}"
            )

    else:

        st.info(
            "No localized ELA regions detected. "
            "No suspicious-region image is displayed."
        )
    # --------------------------------------------------------
    # SUSPICIOUS REGIONS
    # --------------------------------------------------------

    suspicious_regions = ela.get(
        "suspicious_regions",
        []
    )

    st.subheader(
        "📍 Suspicious Regions"
    )

    if suspicious_regions:

        st.write(
            f"Detected regions: "
            f"{len(suspicious_regions)}"
        )

        for index, region in enumerate(
            suspicious_regions,
            start=1
        ):

            st.write(
                f"**Region {index}** — "
                f"x={region.get('x')}, "
                f"y={region.get('y')}, "
                f"width={region.get('width')}, "
                f"height={region.get('height')}, "
                f"area={region.get('area')}"
            )

    else:

        st.info(
            "No localized ELA regions detected."
        )


    # ========================================================
    # FAILED / MISMATCH DETAILS
    # ========================================================

    st.markdown(
        '<div class="section-title">⚠️ Review Details</div>',
        unsafe_allow_html=True
    )

    failed_fields = summary.get(
        "failed_mrz_fields",
        []
    )

    mismatched_fields = summary.get(
        "mismatched_fields",
        []
    )

    partial_fields = summary.get(
        "partial_fields",
        []
    )

    if failed_fields:

        st.write(
            "**MRZ validation failures:**"
        )

        for field in failed_fields:

            st.write(
                f"• {format_name(field)}"
            )

    if mismatched_fields:

        st.write(
            "**Visual ↔ MRZ mismatches:**"
        )

        for field in mismatched_fields:

            st.write(
                f"• {format_name(field)}"
            )

    if partial_fields:

        st.write(
            "**Partial matches:**"
        )

        for field in partial_fields:

            st.write(
                f"• {format_name(field)}"
            )

    if not (
        failed_fields
        or mismatched_fields
        or partial_fields
    ):

        st.success(
            "No review issues were reported."
        )

    # ========================================================
    # FINAL EVIDENCE OVERVIEW
    # ========================================================

    st.markdown(
        '<div class="section-title">🧾 Evidence Overview</div>',
        unsafe_allow_html=True
    )

    quality_status = quality.get(
        "overall",
        "UNKNOWN"
    )

    mrz_status = (
        "PASS"
        if summary.get(
            "mrz_validation_failures",
            0
        ) == 0
        else "ISSUES DETECTED"
    )

    consistency_status = (
        "PASS"
        if summary.get(
            "field_mismatches",
            0
        ) == 0
        else "ISSUES DETECTED"
    )

    ela_status = ela.get(
        "anomaly_level",
        "UNKNOWN"
    )

    evidence1, evidence2, evidence3, evidence4 = st.columns(4)

    with evidence1:
        st.metric(
            "Image Quality",
            quality_status
        )

    with evidence2:
        st.metric(
            "MRZ Validation",
            mrz_status
        )

    with evidence3:
        st.metric(
            "Field Consistency",
            consistency_status
        )

    with evidence4:
        st.metric(
            "ELA",
            ela_status
        )

    st.info(
        "These results are screening evidence. "
        "Forensic indicators such as ELA and missing EXIF "
        "should be interpreted together with OCR, MRZ, "
        "and consistency results."
    )


    # ========================================================
    # COMPLETE JSON
    # ========================================================

    with st.expander(
        "🧾 View Complete Screening JSON"
    ):

        st.json(
            data
        )