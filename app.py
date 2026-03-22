import streamlit as st
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
import tempfile

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴")
st.title("🦴 Living to Skeleton AI (Real Pose Skeleton)")

# --- Mediapipe setup ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)
mp_draw = mp.solutions.drawing_utils

# --- Glow settings ---
color = st.color_picker("Skeleton Color", "#ffffff")
strength = st.slider("Glow Strength", 0.0, 1.0, 0.6)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

rgb = hex_to_rgb(color)

# --- Draw real skeleton ---
def draw_pose_skeleton(image):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    overlay = image.copy()

    if results.pose_landmarks:
        # Draw skeleton lines
        mp_draw.draw_landmarks(
            overlay,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_draw.DrawingSpec(color=rgb, thickness=3, circle_radius=2),
            mp_draw.DrawingSpec(color=rgb, thickness=3)
        )

    # Glow effect
    glow = cv2.GaussianBlur(overlay, (25,25), 0)
    final = cv2.addWeighted(overlay, 1.0, glow, strength, 0)

    return final

# --- Upload ---
file = st.file_uploader("Upload Image or Video", type=["png","jpg","jpeg","mp4"])

if file:
    ext = file.name.split(".")[-1].lower()

    # ---------- IMAGE ----------
    if ext in ["png","jpg","jpeg"]:
        img = Image.open(file)
        img_np = np.array(img)

        result = draw_pose_skeleton(img_np)

        col1, col2 = st.columns(2)
        col1.image(img, caption="Original")
        col2.image(result, caption="Skeleton")

    # ---------- VIDEO ----------
    elif ext == "mp4":
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(file.read())

        cap = cv2.VideoCapture(tfile.name)

        width = int(cap.get(3))
        height = int(cap.get(4))
        fps = cap.get(cv2.CAP_PROP_FPS)

        out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

        stframe = st.empty()
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            result = draw_pose_skeleton(frame)
            out.write(result)

            if count % 3 == 0:
                preview = cv2.resize(result, (400, int(400*height/width)))
                stframe.image(preview, channels="BGR")

            count += 1

        cap.release()
        out.release()

        st.success("Done!")
        st.video(out_path)
