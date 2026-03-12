import streamlit as st
import cv2
import numpy as np
from PIL import Image

# ------------------------
# Page Configuration
# ------------------------
st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴", layout="wide")

st.title("🦴 Living to Skeleton AI")
st.write("Upload an image to see its skeletonized version. Adjust the threshold for best results!")

# ------------------------
# File uploader
# ------------------------
uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

# ------------------------
# Threshold slider
# ------------------------
threshold = st.slider("Threshold for binarization", 50, 200, 127)

# ------------------------
# Skeletonization function
# ------------------------
def skeletonize(image_array, thresh_val):
    # Convert to grayscale
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    # Binarize with threshold
    _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
    # Morphological thinning (real skeleton)
    skeleton = cv2.ximgproc.thinning(binary)
    # Invert back to normal colors
    skeleton = cv2.bitwise_not(skeleton)
    # Optional: colorize skeleton (red)
    colored = cv2.cvtColor(skeleton, cv2.COLOR_GRAY2RGB)
    colored[np.where((colored==[255,255,255]).all(axis=2))] = [255,0,0]  # red skeleton
    return colored

# ------------------------
# Main logic
# ------------------------
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img = np.array(image)

    skeleton = skeletonize(img, threshold)

    # Display side-by-side
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Image")
        st.image(img, use_column_width=True)
    with col2:
        st.subheader("Skeleton Image")
        st.image(skeleton, use_column_width=True)

    # Download button
    st.download_button(
        "Download Skeleton Image",
        data=cv2.imencode(".png", skeleton)[1].tobytes(),
        file_name="skeleton.png",
        mime="image/png"
    )

else:
    # Use static PNG demo preview instead of GIF
    st.image("assets/demo.png", caption="Demo Preview")
