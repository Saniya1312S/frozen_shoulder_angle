# 🦾 Frozen Shoulder Angle Detector

A web app that measures **shoulder arm-elevation angle from a photo** using AI (MediaPipe Pose),
shows the result on an annotated image, and tracks readings on a **live dashboard**.
It includes a short **Ayurveda information tab** for integrative-care discussion.

> ⚠️ Educational / research tool. It is **not** a medical device and does not diagnose frozen shoulder.

![Pipeline](assets/pipeline.png)

## ✨ Features
- Upload a JPG/PNG photo; **left and right** shoulder angles are calculated together
- Annotated image (landmarks + angle) you can download
- Warns when the shoulder, elbow or hip is **not clearly visible** (no fake numbers)
- **Dashboard**: save readings, line chart of progress, left-vs-right chart, table, CSV export
- Colour-coded interpretation bands (indicative only)
- Ayurveda info tab (educational, non-prescriptive)

## 🧠 How it works (simple)
1. **MediaPipe Pose** finds 33 body points on the photo.
2. We take three: **shoulder, elbow, hip**.
3. We compute the angle at the shoulder between the elbow and the hip:

![Angle meaning](assets/angle_meaning.png)

| Angle | Meaning |
|---|---|
| 0° | arm hanging by the side |
| 90° | arm horizontal |
| 180° | arm straight overhead |

Example output (illustrative drawing):

![Sample](assets/sample_annotated.png)

## 📊 Dashboard
Press **Save to dashboard** after an analysis. Each reading is added to the charts and table.
Readings live in the browser session; use **Download CSV** to keep them.

![Dashboard](assets/dashboard_mock.png)

| Band | Angle |
|---|---|
| Near-normal range | 150°+ |
| Mildly restricted | 120–150° |
| Moderately restricted | 90–120° |
| Severely restricted | below 90° |

These bands are **indicative only** (they assume an abduction/elevation photo); clinical judgement decides.

## 🚀 Run locally
```bash
git clone https://github.com/<your-username>/frozen_shoulder_angle.git
cd frozen_shoulder_angle
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Use **Python 3.10, 3.11 or 3.12** (MediaPipe 0.10.21 does not support 3.13).

## 🌐 Put it live (free)
GitHub Pages can't run Streamlit, so keep the code on GitHub and deploy from it:

**Streamlit Community Cloud**
1. Push this folder to a GitHub repo (files must be in the repo **root**, not a sub-folder).
2. Go to <[LIVE DEMO](https://frozenshoulderangle.streamlit.app/)>, sign in with GitHub, click **New app**.
3. Choose the repo, branch `main`, main file `app.py`.
4. **Advanced settings → Python version → 3.11**, then **Deploy**.
5. Paste the live link under "Live demo" below.

`packages.txt` installs the system libraries OpenCV needs; `requirements.txt` installs Python packages.

**Docker / Render / Railway / Hugging Face Spaces:** the included `Dockerfile` reads `$PORT`, so it works on all of them.

**Live demo:** _add your Streamlit link here_

## 📁 Project structure
```
app.py               # Streamlit UI (tabs: Analyze, Dashboard, Ayurveda, About)
utils/pose_utils.py  # pose detection, angle maths, image annotation
tests/               # unit tests (pytest)
assets/              # README images
requirements.txt  packages.txt  Dockerfile  .streamlit/config.toml
```
Run tests: `pip install pytest && pytest`

## 📸 Tips for good results
Frontal photo, full torso and arm visible, plain background, good light, fitted clothing, camera at chest height.

## ⚠️ Limitations & privacy
- A single 2-D photo: camera angle and posture change the number.
- Not clinically validated; compare with a goniometer before relying on it.
- Photos are processed in memory and not stored by the app, but a cloud host still receives them. Get patient consent.

## 📚 Related research
I could not locate the exact paper titled *"Web-Based Application to Calculate the Angle of Frozen Shoulder Using AI and Machine Learning With Ayurveda Integration"*, so this project follows the same idea rather than copying it. Please add its citation here. Related published work:
- Takigami et al., *Estimation of Shoulder Joint Rotation Angle Using Tablet Device and Pose Estimation AI Model*, Sensors, 2024 (MediaPipe + machine learning).
- *Comparative accuracy of a shoulder range motion measurement sensor and Vicon 3D motion capture for shoulder abduction in frozen shoulder*, Technology and Health Care (AIRDS, CNN).
- *Shoulder Angle Measurement (SAM) system*, Songklanakarin J. Sci. Technol. 43(5) (webcam computer vision).

## 📝 License
Add a license of your choice (e.g. MIT) before publishing.
