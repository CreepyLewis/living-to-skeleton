import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import tempfile

# ✅ Correct MediaPipe import
from mediapipe.python.solutions import pose as mp_pose_module

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴")
st.title("🦴 Living to Skeleton AI")
st.write(
    "Upload an image, video, or draw something. Humans will be skeletonized with a glowing X-ray style."
)

# --- Glow settings ---
glow_color = st.color_picker("Select Glow Color", "#ffffff")
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
glow_rgb = hex_to_rgb(glow_color)

glow_strength = st.slider("Glow Strength", 0.0, 1.0, 0.6, 0.05)

# --- Skeleton effect ---
def skeleton_glow_effect(img: np.ndarray, color=(255,255,255), strength=0.6):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    try:
        skeleton = cv2.ximgproc.thinning(edges)
    except AttributeError:
        skeleton = edges
    skeleton_rgb = np.zeros_like(img)
    for i in range(3):
        skeleton_rgb[:,:,i] = skeleton * (color[i]/255)
    skeleton_rgb = skeleton_rgb.astype(np.uint8)
    glow = cv2.GaussianBlur(skeleton_rgb, (15,15), 0)
    result = np.zeros_like(img)
    mask = skeleton_rgb>0
    result[mask] = skeleton_rgb[mask]
    result = cv2.addWeighted(result, 1.0, glow, strength, 0)
    return result

# --- MediaPipe Pose setup ---
pose = mp_pose_module.Pose(static_image_mode=True)

def apply_skeleton_only_humans(img: np.ndarray, color=(255,255,255), strength=0.6):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    if results.pose_landmarks:
        h, w = img.shape[:2]
        for landmark in results.pose_landmarks.landmark:
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(mask, (x,y), 10, 255, -1)
        mask = cv2.dilate(mask, np.ones((20,20), np.uint8), iterations=2)
    skeleton_img = skeleton_glow_effect(img, color, strength)
    result = img.copy()
    result[mask>0] = skeleton_img[mask>0]
    return result

# --- Upload section ---
uploaded_file = st.file_uploader("Upload Image or Video", type=["png","jpg","jpeg","mp4"])

if uploaded_file:
    ext = uploaded_file.name.split(".")[-1].lower()

    # ---------- IMAGE ----------
    if ext in ["png","jpg","jpeg"]:
        img = Image.open(uploaded_file).convert("RGB")
        img_np = np.array(img)
        result_img = apply_skeleton_only_humans(img_np, glow_rgb, glow_strength)
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="Original", use_column_width=True)
        with col2:
            st.image(result_img, caption="Glowing Skeleton", use_column_width=True)
        save_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        Image.fromarray(result_img).save(save_path)
        st.download_button("Download Skeleton Image", open(save_path,"rb").read(), "skeleton.png", "image/png")

    # ---------- VIDEO ----------
    elif ext=="mp4":
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
        width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        out = cv2.VideoWriter(out_path, fourcc, fps, (width,height))
        stframe = st.empty()
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        progress = st.progress(0)
        frame_count = 0
        skip_preview = 3
        preview_width = 400

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_res = apply_skeleton_only_humans(frame, glow_rgb, glow_strength)
            out.write(cv2.cvtColor(frame_res, cv2.COLOR_RGB2BGR))
            if frame_count%skip_preview==0:
                preview = cv2.resize(frame_res, (preview_width,int(preview_width*height/width)))
                stframe.image(preview)
            frame_count+=1
            progress.progress(frame_count/total_frames)

        cap.release()
        out.release()
        st.success("Video Processing Complete!")
        st.video(out_path)
        st.download_button("Download Skeleton Video", open(out_path,"rb").read(), "skeleton_video.mp4", "video/mp4")

# ---------- DRAWING ----------
st.write("---")
st.write("Or draw something:")
canvas_result = st_canvas(
    fill_color="rgba(0,0,0,0)",
    stroke_width=3,
    stroke_color="#FFFFFF",
    background_color="#000000",
    height=300,
    width=300,
    drawing_mode="freedraw",
    key="canvas",
)
if canvas_result.image_data is not None:
    drawn = cv2.cvtColor(canvas_result.image_data.astype(np.uint8), cv2.COLOR_RGBA2RGB)
    skeleton_drawn = apply_skeleton_only_humans(drawn, glow_rgb, glow_strength)
    st.image(skeleton_drawn, caption="Glowing Skeleton Drawing", use_column_width=True)
    save_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    Image.fromarray(skeleton_drawn).save(save_path)
    st.download_button("Download Drawing Skeleton", open(save_path,"rb").read(), "skeleton_drawing.png", "image/png")
