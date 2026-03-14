import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import tempfile
from mediapipe.solutions.pose import Pose
from mediapipe.solutions import drawing_utils as mp_drawing
from ultralytics import YOLO

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴")
st.title("🦴 Living to Skeleton AI (Humans & Animals)")
st.write(
    "Upload an image, video, or draw something. All living things (humans, animals) will be skeletonized, keeping all non-living objects intact."
)

# Settings
glow_color = st.color_picker("Select Glow Color", "#ffffff")
glow_strength = st.slider("Glow Strength", 0.0, 1.0, 0.6, 0.05)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

glow_rgb = hex_to_rgb(glow_color)

# --- Skeleton Glow Effect ---
def skeleton_glow_effect(img: np.ndarray, color=(255, 255, 255), strength=0.6) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    # Use edges directly if thinning unavailable
    try:
        skeleton = cv2.ximgproc.thinning(edges)
    except AttributeError:
        skeleton = edges
    skeleton_rgb = np.zeros_like(img)
    for i in range(3):
        skeleton_rgb[:, :, i] = skeleton * (color[i] / 255)
    glow = cv2.GaussianBlur(skeleton_rgb, (15, 15), 0)
    result = np.zeros_like(img)
    mask = skeleton_rgb > 0
    result[mask] = skeleton_rgb[mask]
    result = cv2.addWeighted(result, 1.0, glow, strength, 0)
    return result

# --- Human Detection ---
mp_pose = Pose(static_image_mode=True, min_detection_confidence=0.5)

def get_human_mask(img: np.ndarray) -> np.ndarray:
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = mp_pose.process(img_rgb)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    if results.pose_landmarks:
        h, w = img.shape[:2]
        for lm in results.pose_landmarks.landmark:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(mask, (cx, cy), radius=10, color=255, thickness=-1)
        mask = cv2.dilate(mask, np.ones((25, 25), np.uint8), iterations=2)
    return mask

# --- Animal Detection ---
model = YOLO("yolov8n-seg.pt")  # segmentation model for animals

def get_animal_mask(img: np.ndarray) -> np.ndarray:
    animal_mask = np.zeros(img.shape[:2], dtype=np.uint8)
    results = model(img)
    for r in results:
        if hasattr(r, 'masks') and r.masks is not None:
            for mask in r.masks.data:
                animal_mask += (mask * 255).astype(np.uint8)
    return np.clip(animal_mask, 0, 255)

# --- Combined Mask ---
def get_living_mask(img: np.ndarray) -> np.ndarray:
    human_mask = get_human_mask(img)
    animal_mask = get_animal_mask(img)
    combined_mask = np.clip(human_mask + animal_mask, 0, 255)
    return combined_mask

def skeleton_living_only(img: np.ndarray) -> np.ndarray:
    mask = get_living_mask(img)
    skeleton_img = skeleton_glow_effect(img, color=glow_rgb, strength=glow_strength)
    result = img.copy()
    result[mask > 0] = skeleton_img[mask > 0]
    return result

# --- Upload Image or Video ---
uploaded_file = st.file_uploader("Upload Image or Video", type=["png","jpg","jpeg","mp4"])

if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()
    
    # IMAGE
    if file_ext in ["png","jpg","jpeg"]:
        img = np.array(Image.open(uploaded_file).convert("RGB"))
        skeleton_img = skeleton_living_only(img)
        col1, col2 = st.columns(2)
        with col1: st.image(img, caption="Original Image", use_column_width=True)
        with col2: st.image(skeleton_img, caption="Skeleton Living Things", use_column_width=True)
        save_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        Image.fromarray(skeleton_img).save(save_path)
        st.download_button("Download Skeleton Image", open(save_path,"rb").read(), "skeleton_image.png", "image/png")
    
    # VIDEO
    elif file_ext == "mp4":
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        out = cv2.VideoWriter(output_path, fourcc, fps, (width,height))
        
        stframe = st.empty()
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        progress_bar = st.progress(0)
        frame_count = 0
        preview_skip = 3
        preview_width = 400
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            sk_frame = skeleton_living_only(frame)
            out.write(cv2.cvtColor(sk_frame, cv2.COLOR_RGB2BGR))
            if frame_count % preview_skip == 0:
                preview_frame = cv2.resize(sk_frame,(preview_width,int(preview_width*height/width)))
                stframe.image(preview_frame)
            frame_count += 1
            progress_bar.progress(frame_count/total_frames)
        
        cap.release()
        out.release()
        st.success("Video processing complete!")
        st.video(output_path)
        st.download_button("Download Skeleton Video", open(output_path,"rb").read(), "skeleton_video.mp4", "video/mp4")

# DRAWING
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
    key="canvas"
)
if canvas_result.image_data is not None:
    drawn_img = cv2.cvtColor(canvas_result.image_data.astype(np.uint8), cv2.COLOR_RGBA2RGB)
    skeleton_drawn = skeleton_glow_effect(drawn_img, color=glow_rgb, strength=glow_strength)
    st.image(skeleton_drawn, caption="Glowing Skeleton Drawing", use_column_width=True)
    save_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    Image.fromarray(skeleton_drawn).save(save_path)
    st.download_button("Download Skeleton Drawing", open(save_path,"rb").read(), "skeleton_drawing.png", "image/png")
