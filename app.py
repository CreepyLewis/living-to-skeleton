import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import mediapipe as mp

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴")
st.title("🦴 Living to Skeleton AI")
st.write("Upload an image or draw something. The app will skeletonize humans/animals and keep non-living parts unchanged.")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def skeletonize_living(img):
    """Detect humans/animals and draw skeleton lines."""
    img_rgb = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img_copy = img.copy()

    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        results = pose.process(img_rgb)
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(img_copy, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    return img_copy

# Upload or draw image
uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

col1, col2 = st.columns(2)

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(img)

    skeleton_img = skeletonize_living(img_np)

    with col1:
        st.image(img, caption="Original Image", use_column_width=True)
    with col2:
        st.image(skeleton_img, caption="Skeletonized Image", use_column_width=True)

st.write("---")
st.write("Or draw something:")

canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",
    stroke_width=3,
    stroke_color="#FFFFFF",
    background_color="#000000",
    height=300,
    width=300,
    drawing_mode="freedraw",
    key="canvas",
)

if canvas_result.image_data is not None:
    drawn_img = cv2.cvtColor(canvas_result.image_data.astype(np.uint8), cv2.COLOR_RGBA2RGB)
    skeleton_drawn = skeletonize_living(drawn_img)
    st.image(skeleton_drawn, caption="Skeletonized Drawing", use_column_width=True)
