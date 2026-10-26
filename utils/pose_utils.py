"""Pose detection and shoulder-angle maths (MediaPipe Pose)."""
import io

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw, ImageFont

mp_pose = mp.solutions.pose
LM = mp_pose.PoseLandmark
MIN_VISIBILITY = 0.5  # landmarks below this are treated as "not visible"

# (min_angle, label, colour) - indicative bands for arm elevation, NOT a diagnosis
BANDS = [
    (150, "Near-normal range", "#188038"),
    (120, "Mildly restricted", "#f9ab00"),
    (90, "Moderately restricted", "#e8710a"),
    (0, "Severely restricted", "#d93025"),
]


def classify(angle):
    """Return (label, colour) for an angle, or ('Unknown', grey)."""
    if angle is None:
        return "Unknown", "#80868b"
    for low, label, colour in BANDS:
        if angle >= low:
            return label, colour


def detect_pose_landmarks(image_rgb, min_detection_confidence=0.4):
    with mp_pose.Pose(static_image_mode=True, model_complexity=1,
                      min_detection_confidence=min_detection_confidence) as pose:
        return pose.process(image_rgb)


def calculate_angle(a, b, c):
    """Angle ABC in degrees, vertex at b. Returns None for zero-length vectors."""
    a, b, c = (np.array(p, dtype=np.float64) for p in (a, b, c))
    ba, bc = a - b, c - b
    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom == 0:
        return None
    cos = np.clip(np.dot(ba, bc) / denom, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos)))


def compute_shoulder_angle(results, width, height, side="left"):
    """Angle at the shoulder between the elbow and the hip.

    0 deg = arm hanging beside the body, 90 deg = arm horizontal,
    180 deg = arm straight overhead.
    Returns (angle | None, {'shoulder','elbow','hip'} pixel coords, reason | None).
    """
    if not results.pose_landmarks:
        return None, {}, "No person detected"
    lm = results.pose_landmarks.landmark
    names = {"left": (LM.LEFT_SHOULDER, LM.LEFT_ELBOW, LM.LEFT_HIP),
             "right": (LM.RIGHT_SHOULDER, LM.RIGHT_ELBOW, LM.RIGHT_HIP)}[side]
    pts = [lm[n] for n in names]
    px = [(int(p.x * width), int(p.y * height)) for p in pts]
    pos = dict(zip(("shoulder", "elbow", "hip"), px))
    if min(p.visibility for p in pts) < MIN_VISIBILITY:
        return None, pos, "Shoulder, elbow or hip not clearly visible"
    return calculate_angle(px[1], px[0], px[2]), pos, None


def annotate_image(image_bgr, measurements):
    """measurements: list of (side, angle, positions). Returns a PIL image."""
    im = Image.fromarray(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(im)
    w, h = im.size
    size = max(16, int(min(w, h) * 0.035))
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    r, lw = max(5, size // 3), max(3, size // 6)
    for side, angle, pos in measurements:
        s, e, hp = pos.get("shoulder"), pos.get("elbow"), pos.get("hip")
        if not s:
            continue
        if e:
            d.line([s, e], fill=(255, 215, 0), width=lw)
        if hp:
            d.line([s, hp], fill=(0, 200, 255), width=lw)
        for p, col in ((s, (255, 0, 0)), (e, (0, 255, 0)), (hp, (0, 0, 255))):
            if p:
                d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=col, outline="white")
        txt = f"{side[0].upper()}: " + ("N/A" if angle is None else f"{angle:.1f} deg")
        x, y = max(5, s[0] + 10), max(5, s[1] - 2 * size)
        for ox, oy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            d.text((x + ox, y + oy), txt, font=font, fill="black")
        d.text((x, y), txt, font=font, fill="white")
    return im


def to_png_bytes(pil_img):
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return buf.getvalue()
