import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴")
st.title("🦴 Living to Skeleton AI")
st.write("Upload an image or draw something. The app will skeletonize living-like objects and keep non-living parts unchanged.")

# --- Skeletonization function ---
def skeletonize_img(img: np.ndarray) -> np.ndarray:
    """
    Convert image to skeleton (thin lines) using OpenCV.
    Preserves non-living background.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    binary = cv2.bitwise_not(binary)

    # Use OpenCV ximgproc thinning
    try:
        skeleton = cv2.ximgproc.thinning(binary)
    except AttributeError:
        # fallback if ximgproc unavailable: simple morphological skeleton
        skeleton = cv2.morphologyEx(binary, cv2.MORPH_ERODE, np.ones((3,3), np.uint8))
    
    skeleton = cv2.bitwise_not(skeleton)
    skeleton_rgb = cv2.cvtColor(skeleton, cv2.COLOR_GRAY2RGB)

    # Overlay skeleton only where it exists
    mask = skeleton_rgb > 0
    result = img.copy()
    result[mask] = skeleton_rgb[mask]
    return result

# --- Image upload ---
uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
col1, col2 = st.columns(2)

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(img)

    skeleton_img = skeletonize_img(img_np)

    with col1:
        st.image(img, caption="Original Image", use_column_width=True)
    with col2:
        st.image(skeleton_img, caption="Skeletonized Image", use_column_width=True)

st.write("---")
st.write("Or draw something:")

# --- Drawing canvas ---
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
    skeleton_drawn = skeletonize_img(drawn_img)
    st.image(skeleton_drawn, caption="Skeletonized Drawing", use_column_width=True)
