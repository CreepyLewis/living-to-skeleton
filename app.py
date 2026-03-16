import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import tempfile
import mediapipe as mp

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴")

st.title("🦴 Living to Skeleton AI")
st.write("Convert humans in images or videos into glowing skeletons while keeping the background unchanged.")

# -----------------------------
# Mediapipe Setup
# -----------------------------
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# -----------------------------
# Controls
# -----------------------------
glow_color = st.color_picker("Skeleton Glow Color", "#00FFFF")
glow_strength = st.slider("Glow Strength", 0.0, 1.0, 0.6)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

glow_rgb = hex_to_rgb(glow_color)

# -----------------------------
# Skeleton Function
# -----------------------------
def draw_glowing_skeleton(image):

    result_img = image.copy()

    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=False
    ) as pose:

        results = pose.process(image)

        if results.pose_landmarks:

            mp_drawing.draw_landmarks(
                result_img,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(
                    color=glow_rgb,
                    thickness=int(2 + glow_strength * 6),
                    circle_radius=2
                ),
                mp_drawing.DrawingSpec(
                    color=glow_rgb,
                    thickness=int(2 + glow_strength * 6),
                    circle_radius=2
                ),
            )

    return result_img

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload Image or Video", type=["png","jpg","jpeg","mp4"])

# -----------------------------
# IMAGE PROCESSING
# -----------------------------
if uploaded_file:

    file_ext = uploaded_file.name.split(".")[-1].lower()

    if file_ext in ["png","jpg","jpeg"]:

        image = Image.open(uploaded_file).convert("RGB")
        img_np = np.array(image)

        skeleton_img = draw_glowing_skeleton(img_np)

        col1, col2 = st.columns(2)

        with col1:
            st.image(img_np, caption="Original")

        with col2:
            st.image(skeleton_img, caption="Skeleton")

        # download
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        Image.fromarray(skeleton_img).save(tmp.name)

        st.download_button(
            "Download Skeleton Image",
            open(tmp.name,"rb"),
            "skeleton.png"
        )

# -----------------------------
# VIDEO PROCESSING
# -----------------------------
    elif file_ext == "mp4":

        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(uploaded_file.read())

        cap = cv2.VideoCapture(temp.name)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_display = st.empty()
        progress = st.progress(0)

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0

        preview_skip = 3

        while cap.isOpened():

            ret, frame = cap.read()

            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            sk_frame = draw_glowing_skeleton(frame_rgb)

            out.write(cv2.cvtColor(sk_frame, cv2.COLOR_RGB2BGR))

            if frame_count % preview_skip == 0:
                frame_display.image(sk_frame)

            frame_count += 1
            progress.progress(frame_count/total_frames)

        cap.release()
        out.release()

        st.success("Video Processing Complete")

        st.video(output_path)

        st.download_button(
            "Download Skeleton Video",
            open(output_path,"rb"),
            "skeleton_video.mp4"
        )

# -----------------------------
# DRAWING CANVAS
# -----------------------------
st.write("---")
st.write("Or draw a stick figure")

canvas = st_canvas(
    fill_color="rgba(0,0,0,0)",
    stroke_width=4,
    stroke_color="#FFFFFF",
    background_color="#000000",
    height=300,
    width=300,
    drawing_mode="freedraw",
    key="canvas"
)

if canvas.image_data is not None:

    img = canvas.image_data.astype(np.uint8)

    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    skeleton = draw_glowing_skeleton(img)

    st.image(skeleton)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")

    Image.fromarray(skeleton).save(tmp.name)

    st.download_button(
        "Download Drawing Skeleton",
        open(tmp.name,"rb"),
        "drawing_skeleton.png"
    )
