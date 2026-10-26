import io
from datetime import datetime

import cv2
import numpy as np
import pandas as pd
import streamlit as st

from utils.pose_utils import (BANDS, annotate_image, classify, compute_shoulder_angle,
                              detect_pose_landmarks, to_png_bytes)

st.set_page_config(page_title="Frozen Shoulder Angle", page_icon="🦾", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1200px; padding-top: 2rem;}
h1 {text-align: center; font-weight: 700;}
.card {background:#fff; border-radius:14px; padding:1rem 1.2rem;
       box-shadow:0 2px 10px rgba(0,0,0,.08); text-align:center;}
.card .big {font-size:2.2rem; font-weight:700;}
.pill {display:inline-block; padding:.15rem .7rem; border-radius:999px;
       color:#fff; font-weight:600; font-size:.9rem;}
</style>""", unsafe_allow_html=True)

st.session_state.setdefault("history", [])
st.session_state.setdefault("annotated", None)
st.session_state.setdefault("last_key", None)

st.title("🦾 Frozen Shoulder Angle Detector")
st.caption("AI-assisted shoulder elevation angle from a single photo (MediaPipe Pose). "
           "Educational tool - not a medical diagnosis.")

tab_an, tab_dash, tab_ayu, tab_about = st.tabs(
    ["📷 Analyze", "📊 Dashboard", "🌿 Ayurveda info", "ℹ️ About"])


def card(title, angle):
    label, colour = classify(angle)
    val = "N/A" if angle is None else f"{angle:.1f}°"
    st.markdown(f"<div class='card'><div>{title}</div><div class='big'>{val}</div>"
                f"<span class='pill' style='background:{colour}'>{label}</span></div>",
                unsafe_allow_html=True)


# ------------------------------------------------------------------ Analyze
with tab_an:
    left, right = st.columns([3, 2])
    with left:
        up = st.file_uploader("Upload a frontal image (JPG/PNG)", type=["jpg", "jpeg", "png"])
        c1, c2 = st.columns(2)
        pid = c1.text_input("Patient / session label", value="Patient 1")
        pose_name = c2.selectbox("Movement", ["Abduction (arm out to the side)",
                                              "Flexion (arm forward)", "Other"])

    if up is None:
        st.session_state.annotated = None          # fixes stale download button
        st.session_state.last_key = None
        st.info("Tip: full torso visible, arm raised, plain background, good light.")
    else:
        data = up.getvalue()
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            st.error("Unable to read the image. Try another file.")
        else:
            h, w = img.shape[:2]
            results = detect_pose_landmarks(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            ms, notes = [], []
            for side in ("left", "right"):
                ang, pos, why = compute_shoulder_angle(results, w, h, side)
                ms.append((side, ang, pos))
                if why:
                    notes.append(f"{side.title()}: {why}")
            out = annotate_image(img, ms)
            st.session_state.annotated = to_png_bytes(out)

            with left:
                st.image(out, caption="Annotated image (L = left, R = right shoulder)",
                         use_column_width=True)
            with right:
                st.subheader("Result")
                card("Left shoulder", ms[0][1])
                st.write("")
                card("Right shoulder", ms[1][1])
                for n in notes:
                    st.warning(n + ". Upload a clearer frontal image.")
                st.download_button("⬇ Download annotated image", st.session_state.annotated,
                                   "annotated_shoulder.png", "image/png")
                key = (up.name, len(data), pid, pose_name)
                if st.button("➕ Save to dashboard") and key != st.session_state.last_key:
                    st.session_state.last_key = key
                    st.session_state.history.append({
                        "time": datetime.now().strftime("%H:%M:%S"), "label": pid,
                        "movement": pose_name.split(" ")[0],
                        "left_deg": ms[0][1], "right_deg": ms[1][1]})
                    st.success("Saved - see the Dashboard tab.")

# ---------------------------------------------------------------- Dashboard
with tab_dash:
    hist = st.session_state.history
    if not hist:
        st.info("No readings yet. Analyze an image and press **Save to dashboard**.")
    else:
        df = pd.DataFrame(hist)
        df.index = range(1, len(df) + 1)
        last = df.iloc[-1]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Readings", len(df))
        k2.metric("Latest left", "N/A" if pd.isna(last.left_deg) else f"{last.left_deg:.1f}°")
        k3.metric("Latest right", "N/A" if pd.isna(last.right_deg) else f"{last.right_deg:.1f}°")
        k4.metric("Best angle so far", f"{np.nanmax(df[['left_deg','right_deg']].values):.1f}°"
                  if df[["left_deg", "right_deg"]].notna().any().any() else "N/A")
        st.subheader("Progress over readings")
        st.line_chart(df[["left_deg", "right_deg"]])
        a, b = st.columns(2)
        with a:
            st.subheader("Left vs right (latest)")
            st.bar_chart(pd.DataFrame({"angle": [last.left_deg, last.right_deg]},
                                      index=["Left", "Right"]))
        with b:
            st.subheader("Interpretation bands")
            for low, name, col in BANDS:
                st.markdown(f"<span class='pill' style='background:{col}'>{low}°+</span> {name}",
                            unsafe_allow_html=True)
            st.caption("Indicative bands for arm elevation only; clinical judgement decides.")
        st.subheader("All readings")
        st.dataframe(df, use_container_width=True)
        d1, d2 = st.columns(2)
        d1.download_button("⬇ Download CSV", df.to_csv().encode(), "readings.csv", "text/csv")
        if d2.button("🗑 Clear all readings"):
            st.session_state.history = []
            st.rerun()

# ------------------------------------------------------------------ Ayurveda
with tab_ayu:
    st.subheader("Frozen shoulder in Ayurveda (educational)")
    st.markdown("""
In Ayurvedic texts a stiff, painful shoulder with limited arm movement is commonly
compared to **Apabahuka** (often linked with *Vata* imbalance). Practitioners may combine
measured range of motion with traditional assessment, so a repeatable **angle reading**
gives a simple way to track change over time.

**How this app can support an integrative workflow**
- Record an angle at each visit and save it to the dashboard.
- Compare left and right sides to see how restricted the affected shoulder is.
- Export the CSV so the practitioner can review progress.

**General, non-prescriptive points often discussed**
- Gentle, supervised mobility and stretching; avoid forcing painful movement.
- Warmth and rest as advised by a qualified practitioner.
- Any herbs, oils or therapies (e.g. *Abhyanga*, *Swedana*) should be chosen and supervised
  by a qualified Ayurvedic doctor.
""")
    st.warning("This section is general information, not treatment advice. "
               "Consult a qualified doctor or Ayurvedic practitioner.")

# --------------------------------------------------------------------- About
with tab_about:
    st.markdown("""
**How it works:** MediaPipe Pose finds body landmarks → the app measures the angle at the
shoulder between the **elbow** and the **hip** → the result is shown on the photo and the dashboard.

**Angle meaning:** 0° arm by the side · 90° arm horizontal · 180° arm overhead.

**Limits:** 2-D photo (camera angle matters), no clinical validation, landmarks can be wrong
with loose clothes or poor light. Uploaded photos are processed in memory and not stored
by this app, but a cloud host still receives them - get patient consent.
""")
