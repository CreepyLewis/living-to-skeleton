import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import tempfile
from moviepy.editor import VideoFileClip

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴")
st.title("🦴 Living to Skeleton AI")

# --- Glow color and strength ---
glow_color = st.color_picker("Select Glow Color", "#ffffff")
glow_strength = st.slider("Glow Strength", 0.0, 1.0, 0.6, 0.05)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2],16) for i in (0,2,4))
glow_rgb = hex_to_rgb(glow_color)

# --- Skeleton effect ---
def skeleton_glow_effect(img: np.ndarray, color=(255,255,255), strength=0.6) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blurred,50,150)
    try:
        skeleton = cv2.ximgproc.thinning(edges)
    except AttributeError:
        skeleton = edges
    skeleton_rgb = np.zeros_like(img)
    for i in range(3):
        skeleton_rgb[:,:,i] = skeleton * (color[i]/255)
    skeleton_rgb = skeleton_rgb.astype(np.uint8)
    glow = cv2.GaussianBlur(skeleton_rgb,(15,15),0)
    result = cv2.addWeighted(skeleton_rgb,1.0,glow,strength,0)
    return result

# --- File uploader ---
uploaded_file = st.file_uploader("Upload Image or Video", type=["png","jpg","jpeg","mp4"])

if uploaded_file:
    ext = uploaded_file.name.split(".")[-1].lower()
    
    # --- IMAGE ---
    if ext in ["png","jpg","jpeg"]:
        img = Image.open(uploaded_file).convert("RGB")
        img_np = np.array(img)
        skeleton_img = skeleton_glow_effect(img_np, glow_rgb, glow_strength)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="Original", use_column_width=True)
        with col2:
            st.image(skeleton_img, caption="Glowing Skeleton", use_column_width=True)
        
        save_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        Image.fromarray(skeleton_img).save(save_path)
        st.download_button("Download Skeleton Image", open(save_path,"rb").read(), "skeleton_image.png")
    
    # --- VIDEO ---
    elif ext=="mp4":
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
        w,h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        out = cv2.VideoWriter(temp_output, fourcc, fps, (w,h))
        
        stframe = st.empty()
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        progress = st.progress(0)
        
        frame_count = 0
        skip_preview = 3
        preview_w = 400
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            sk_frame = skeleton_glow_effect(frame_rgb, glow_rgb, glow_strength)
            out.write(cv2.cvtColor(sk_frame, cv2.COLOR_RGB2BGR))
            
            if frame_count % skip_preview == 0:
                preview_frame = cv2.resize(sk_frame, (preview_w,int(preview_w*h/w)))
                stframe.image(preview_frame)
            
            frame_count += 1
            progress.progress(frame_count/total)
        
        cap.release()
        out.release()
        
        # Merge original audio
        orig_clip = VideoFileClip(tfile.name)
        sk_clip = VideoFileClip(temp_output)
        final_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        final_clip = sk_clip.set_audio(orig_clip.audio)
        final_clip.write_videofile(final_output, codec="libx264", audio_codec="aac")
        
        st.success("Video processing complete!")
        st.video(final_output)
        st.download_button("Download Video with Original Audio", open(final_output,"rb").read(), "skeleton_video.mp4")
        
# --- DRAWING ---
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
    skeleton_drawn = skeleton_glow_effect(drawn_img, glow_rgb, glow_strength)
    st.image(skeleton_drawn, caption="Glowing Skeleton Drawing", use_column_width=True)
    save_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    Image.fromarray(skeleton_drawn).save(save_path)
    st.download_button("Download Drawing", open(save_path,"rb").read(), "skeleton_drawing.png")
