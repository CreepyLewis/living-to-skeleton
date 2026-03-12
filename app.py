import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# -----------------------
# Page config
# -----------------------
st.set_page_config(
    page_title="Living to Skeleton AI",
    page_icon="🦴",
    layout="wide"
)

st.title("🦴 Living to Skeleton AI")
st.write("Upload an image, draw something, or take a photo to convert it into a skeleton!")

# -----------------------
# Skeletonization function
# -----------------------
def skeletonize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    skel = np.zeros(binary.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))

    while True:
        eroded = cv2.erode(binary, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(binary, temp)
        skel = cv2.bitwise_or(skel, temp)
        binary = eroded.copy()

        if cv2.countNonZero(binary) == 0:
            break

    return skel


# -----------------------
# Upload Image Section
# -----------------------
st.header("📤 Upload Image")

uploaded_file = st.file_uploader(
    "Upload Image",
    type=["png","jpg","jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img = np.array(image)

    skeleton = skeletonize(img)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        st.image(img)

    with col2:
        st.subheader("Skeleton Image")
        st.image(skeleton)

    st.download_button(
        "Download Skeleton",
        data=cv2.imencode(".png", skeleton)[1].tobytes(),
        file_name="skeleton.png",
        mime="image/png"
    )

# -----------------------
# Drawing Canvas Section
# -----------------------
st.header("✏️ Draw Something")

canvas_result = st_canvas(
    stroke_width=5,
    stroke_color="black",
    background_color="white",
    height=300,
    width=300,
    drawing_mode="freedraw",
    key="canvas",
)

if canvas_result.image_data is not None:

    img = canvas_result.image_data.astype(np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    skeleton = skeletonize(img)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Drawing")
        st.image(img)

    with col2:
        st.subheader("Skeleton")
        st.image(skeleton)


# -----------------------
# Webcam Section
# -----------------------
st.header("📷 Webcam Skeleton Mode")

camera_image = st.camera_input("Take a picture")

if camera_image:
    image = Image.open(camera_image).convert("RGB")
    img = np.array(image)

    skeleton = skeletonize(img)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Camera Image")
        st.image(img)

    with col2:
        st.subheader("Skeleton")
        st.image(skeleton)
