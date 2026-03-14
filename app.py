import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴")
st.title("🦴 Living to Skeleton AI (X-ray Style)")
st.write(
    "Upload an image or draw something. The app will convert humans/animals into a realistic skeleton/X-ray style."
)

# --- Skeleton/X-ray effect ---
def skeleton_effect(img: np.ndarray) -> np.ndarray:
    """Convert living shapes into realistic skeleton look (white bones on dark background)."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection (bones)
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)
    
    # Thinning if available
    try:
        skeleton = cv2.ximgproc.thinning(edges)
    except AttributeError:
        skeleton = edges  # fallback
    
    # Make skeleton white on black background
    skeleton_rgb = cv2.cvtColor(skeleton, cv2.COLOR_GRAY2RGB)
    skeleton_rgb[skeleton_rgb > 0] = 255
    
    # Overlay skeleton on black background
    result = np.zeros_like(img)
    mask = skeleton_rgb > 0
    result[mask] = skeleton_rgb[mask]
    
    return result

# --- Image upload ---
uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
col1, col2 = st.columns(2)

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(img)
    
    skeleton_img = skeleton_effect(img_np)
    
    with col1:
        st.image(img, caption="Original Image", use_column_width=True)
    with col2:
        st.image(skeleton_img, caption="Skeleton/X-ray Image", use_column_width=True)

st.write("---")
st.write("Or draw something:")

# --- Drawing canvas ---
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
