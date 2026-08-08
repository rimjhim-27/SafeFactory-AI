import os
import streamlit as st
from ultralytics import YOLO
from PIL import Image


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SafeFactory AI",
    page_icon="🏭",
    layout="wide"
)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

# The trained PPE model should be placed at:
# models/best.pt
#
# The .pt file is intentionally not committed to GitHub.
# See models/README.md for model setup information.

MODEL_PATH = os.path.join("models", "best.pt")


# General YOLO model for person detection.
# Ultralytics automatically downloads yolo11n.pt if required.
person_model = YOLO("yolo11n.pt")


# Load trained PPE model only if it exists locally.
if os.path.exists(MODEL_PATH):
    ppe_model = YOLO(MODEL_PATH)
    model_available = True
else:
    ppe_model = None
    model_available = False


# ============================================================
# HEADER
# ============================================================

st.title("🏭 SafeFactory AI")

st.subheader(
    "Neuro-Symbolic Industrial Safety Monitoring"
)

st.caption(
    "From Seeing Hazards to Reasoning About Safety."
)


# ============================================================
# MODEL STATUS
# ============================================================

if model_available:
    st.success("🟢 Trained PPE model loaded successfully.")
else:
    st.warning(
        "⚠️ Trained PPE model not found. "
        "Place the trained 'best.pt' file inside the "
        "'models' folder to enable PPE detection."
    )


# ============================================================
# IMAGE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📷 Upload a factory image",
    type=["jpg", "jpeg", "png"]
)


# ============================================================
# MAIN APPLICATION
# ============================================================

if uploaded_file:

    image = Image.open(uploaded_file)

    st.divider()

    # --------------------------------------------------------
    # PERSON DETECTION
    # --------------------------------------------------------

    person_results = person_model(image)

    person_count = 0

    for result in person_results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            # COCO class 0 = person
            if class_id == 0 and confidence >= 0.40:
                person_count += 1


    # --------------------------------------------------------
    # PPE MODEL CHECK
    # --------------------------------------------------------

    if ppe_model is None:

        st.error(
            "🚨 PPE model unavailable. "
            "Please place 'best.pt' inside the models/ folder."
        )

        st.stop()


    # --------------------------------------------------------
    # PPE DETECTION
    # --------------------------------------------------------

    ppe_results = ppe_model(image)

    detected_items = []


    for result in ppe_results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            class_name = ppe_model.names[class_id]

            if confidence >= 0.40:
                detected_items.append(class_name)


    # --------------------------------------------------------
    # PPE STATUS
    # --------------------------------------------------------

    helmet_detected = "helmet" in detected_items

    vest_detected = "vest" in detected_items

    mask_detected = "mask" in detected_items


    # ========================================================
    # AI DETECTION RESULT
    # ========================================================

    st.subheader("🔍 AI Detection Results")

    annotated = ppe_results[0].plot()

    st.image(
        annotated,
        caption="YOLO11n PPE Detection",
        use_container_width=True
    )


    st.divider()


    # ========================================================
    # SAFETY CONTEXT
    # ========================================================

    st.subheader("🏭 Safety Context")

    col_context1, col_context2 = st.columns(2)


    with col_context1:

        machine_active = st.checkbox(
            "🏭 Machine is ACTIVE",
            value=True
        )


    with col_context2:

        hazard_zone = st.checkbox(
            "⚠️ Worker is inside HAZARD ZONE",
            value=True
        )


    st.divider()


    # ========================================================
    # DETECTION METRICS
    # ========================================================

    st.subheader("📊 Detection Summary")

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "👷 Workers",
            person_count
        )


    with col2:

        st.metric(
            "🪖 Helmet",
            "Detected" if helmet_detected else "Missing"
        )


    with col3:

        st.metric(
            "🦺 Vest",
            "Detected" if vest_detected else "Missing"
        )


    with col4:

        st.metric(
            "😷 Mask",
            "Detected" if mask_detected else "Missing"
        )


    st.divider()


    # ========================================================
    # SYMBOLIC RULE ENGINE
    # ========================================================

    st.subheader("🧠 Symbolic Safety Reasoning")


    # --------------------------------------------------------
    # RULE-001
    # Critical violation: missing helmet
    # --------------------------------------------------------

    if (
        person_count > 0
        and machine_active
        and hazard_zone
        and not helmet_detected
    ):

        st.error(
            "🚨 CRITICAL SAFETY VIOLATION"
        )

        st.markdown(
            """
            ### RULE-001 Triggered

            **Reasoning:**

            - 👷 Worker detected
            - 🏭 Machine is ACTIVE
            - ⚠️ Worker is inside hazardous zone
            - 🪖 Required helmet was **NOT detected**

            ### Recommended Action

            **Stop the machine or remove the worker
            from the hazardous zone immediately.**
            """
        )


    # --------------------------------------------------------
    # RULE-002
    # High risk: missing vest
    # --------------------------------------------------------

    elif (
        person_count > 0
        and machine_active
        and hazard_zone
        and not vest_detected
    ):

        st.warning(
            "⚠️ HIGH SAFETY RISK"
        )

        st.markdown(
            """
            ### RULE-002 Triggered

            Worker detected inside an active hazardous
            zone without the required safety vest.

            ### Reasoning

            - 👷 Worker detected
            - 🏭 Machine is ACTIVE
            - ⚠️ Hazard Zone is ACTIVE
            - 🦺 Required safety vest was **NOT detected**

            ### Recommended Action

            **Remove the worker from the hazardous zone.**
            """
        )


    # --------------------------------------------------------
    # SAFE / NO CRITICAL VIOLATION
    # --------------------------------------------------------

    elif person_count > 0:

        st.success(
            "✅ NO CRITICAL SAFETY VIOLATION"
        )

        st.markdown(
            """
            ### Safety Assessment

            Worker detected, but none of the currently
            implemented critical safety rules were triggered.

            **Current conditions appear compliant with
            the implemented rule set.**
            """
        )


    # --------------------------------------------------------
    # NO WORKER
    # --------------------------------------------------------

    else:

        st.success(
            "✅ SAFE"
        )

        st.write(
            "No worker detected in the uploaded image."
        )


    # ========================================================
    # NEURO-SYMBOLIC EXPLANATION
    # ========================================================

    st.divider()

    st.subheader("🔬 Neuro-Symbolic Decision Flow")

    st.markdown(
        """
        **Neural Perception**

        YOLO11n identifies what is visually present.

        ↓

        **Structured Safety Facts**

        Worker + PPE + Machine State + Hazard Zone

        ↓

        **Symbolic Reasoning**

        Explicit safety rules evaluate the combination
        of conditions.

        ↓

        **Explainable Decision**

        The system reports the triggered rule,
        risk level, reason and recommended action.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "SafeFactory AI • Explainable Neuro-Symbolic AI "
    "for Industrial Safety Monitoring"
)

st.caption(
    "Prototype for research and demonstration purposes. "
    "Not intended for autonomous industrial machinery control."
)