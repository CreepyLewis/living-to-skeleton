import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴", layout="wide")

st.title("🦴 Living to Skeleton AI")
st.write("Upload an image OR draw something and convert it into a skeleton!")

# -------- Skeleton function --------
def skeletonize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
    skeleton = cv2.ximgproc.thinning(binary)
    skeleton = cv2.bitwise_not(skeleton)
    return skeleton

# -------- Upload image --------
uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

# -------- Drawing canvas --------
st.subheader("Or draw something")

canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=5,
    stroke_color="black",
    background_color="white",
    height=300,
    width=300,
    drawing_mode="freedraw",
    key="canvas",
)

# -------- Process uploaded image --------
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img = np.array(image)

    skeleton = skeletonize(img)

    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Original")
    with col2:
        st.image(skeleton, caption="Skeleton")

# -------- Process drawing --------
elif canvas_result.image_data is not None:
    img = canvas_result.image_data.astype(np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    skeleton = skeletonize(img)

    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Drawing")
    with col2:
        st.image(skeleton, caption="Skeleton")
