import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import tempfile
from mediapipe.solutions.pose import Pose, POSE_CONNECTIONS

st.set_page_config(page_title="🦴 Living to Skeleton AI", layout="wide")
st.title("🦴 Living to Skeleton AI")
st.write("Upload an image, video, or draw something and convert humans/animals into glowing skeletons!")

# -------------------------------
# Sidebar Controls
# -------------------------------
st.sidebar.header("Skeleton Style Controls")
glow_color = st.sidebar.color_picker("Glow Color", "#FF0000")
glow_strength = st.sidebar.slider("Glow Strength", 1, 10, 5)

# -------------------------------
# Initialize MediaPipe Pose
# -------------------------------
pose_detector = Pose(static_image_mode=True, min_detection_confidence=0.5)

# -------------------------------
# Helper Functions
# -------------------------------
def draw_skeleton_on_frame(frame):
    """Detect human pose and draw glowing skeleton on frame"""
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose_detector.process(img_rgb)
    if results.pose_landmarks:
        h, w, _ = frame.shape
        for start_idx, end_idx in POSE_CONNECTIONS:
            start = results.pose_landmarks.landmark[start_idx]
            end = results.pose_landmarks.landmark[end_idx]
            x1, y1 = int(start.x * w), int(start.y * h)
            x2, y2 = int(end.x * w), int(end.y * h)
            # Glow effect: multiple lines for thickness
            for i in range(glow_strength):
                cv2.line(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    tuple(int(glow_color.lstrip("#")[j:j+2],16) for j in (0,2,4)),
                    1+i
                )
    return frame

def process_image(img):
    frame = np.array(img.convert("RGB"))[:, :, ::-1]  # PIL -> BGR
    frame = draw_skeleton_on_frame(frame)
    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

def process_video(file_path):
    """Process video file frame by frame"""
    cap = cv2.VideoCapture(file_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    out = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = draw_skeleton_on_frame(frame)
        if out is None:
            h, w, _ = frame.shape
            out = cv2.VideoWriter(temp_out.name, fourcc, cap.get(cv2.CAP_PROP_FPS), (w, h))
        out.write(frame)
    cap.release()
    if out:
        out.release()
    return temp_out.name

# -------------------------------
# Main App: Tabs
# -------------------------------
tab1, tab2 = st.tabs(["Upload Image / Video", "Draw Something"])

with tab1:
    uploaded_file = st.file_uploader("Choose an image or video", type=["png","jpg","jpeg","mp4","mov"])
    if uploaded_file:
        file_type = uploaded_file.type
        if "image" in file_type:
            img = Image.open(uploaded_file)
            output_img = process_image(img)
            st.image(output_img, caption="Skeleton Preview", use_column_width=True)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                output_img.save(tmp_file.name)
                st.download_button("Download Image", tmp_file.name, file_name="skeleton.png")
        elif "video" in file_type:
            st.info("Processing video... Please wait")
            temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_file.read())
            skeleton_video = process_video(temp_video_path)
            st.video(skeleton_video)
            st.download_button("Download Video", skeleton_video, file_name="skeleton_video.mp4")

with tab2:
    canvas_result = st_canvas(
        fill_color="rgba(0,0,0,0)",
        stroke_width=3,
        stroke_color=glow_color,
        background_color="#FFFFFF",
        width=512,
        height=512,
        drawing_mode="freedraw",
        key="canvas"
    )
    if canvas_result.image_data is not None:
        img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA').convert("RGB")
        output_img = process_image(img)
        st.image(output_img, caption="Skeleton Preview", use_column_width=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            output_img.save(tmp_file.name)
            st.download_button("Download Image", tmp_file.name, file_name="skeleton.png")
