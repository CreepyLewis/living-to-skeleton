import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import tempfile
import os

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴")
st.title("🦴 Living to Skeleton AI (X-ray Style)")
st.write(
    "Upload an image, video, or draw something. Humans/animals will be skeletonized in X-ray style."
)

# --- Skeleton/X-ray effect function ---
def skeleton_effect(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    edges = cv2.Canny(blurred, 50, 150)
    try:
        skeleton = cv2.ximgproc.thinning(edges)
    except AttributeError:
        skeleton = edges
    
    skeleton_rgb = cv2.cvtColor(skeleton, cv2.COLOR_GRAY2RGB)
    skeleton_rgb[skeleton_rgb > 0] = 255
    
    result = np.zeros_like(img)
    mask = skeleton_rgb > 0
    result[mask] = skeleton_rgb[mask]
    return result

# --- Upload section ---
uploaded_file = st.file_uploader("Upload Image or Video", type=["png", "jpg", "jpeg", "mp4"])

if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()
    
    if file_ext in ["png", "jpg", "jpeg"]:
        img = Image.open(uploaded_file).convert("RGB")
        img_np = np.array(img)
        skeleton_img = skeleton_effect(img_np)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="Original Image", use_column_width=True)
        with col2:
            st.image(skeleton_img, caption="Skeleton/X-ray Image", use_column_width=True)
    
    elif file_ext == "mp4":
        # Save uploaded video to temporary file
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        stframe = st.empty()
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        progress_bar = st.progress(0)
        
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            sk_frame = skeleton_effect(frame_rgb)
            out.write(cv2.cvtColor(sk_frame, cv2.COLOR_RGB2BGR))
            
            stframe.image(sk_frame, channels="RGB", use_column_width=True)
            
            frame_count += 1
            progress_bar.progress(frame_count / total_frames)
        
        cap.release()
        out.release()
        st.success("Video processing complete!")
        st.download_button(
            label="Download Skeletonized Video",
            data=open(output_path, "rb").read(),
            file_name="skeleton_video.mp4",
            mime="video/mp4"
        )

# --- Drawing canvas ---
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
    drawn_img = cv2.cvtColor(canvas_result.image_data.astype(np.uint8), cv2.COLOR_RGBA2RGB)
    skeleton_drawn = skeleton_effect(drawn_img)
    st.image(skeleton_drawn, caption="Skeletonized Drawing", use_column_width=True)
