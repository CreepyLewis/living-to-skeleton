import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Living to Skeleton", page_icon="🦴", layout="wide")

st.title("🦴 Living to Skeleton")
st.write("Upload an image and convert it into a skeleton representation.")

uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

def skeletonize(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
    skeleton = cv2.Canny(thresh,50,150)
    return skeleton

if uploaded_file:

    image = Image.open(uploaded_file)
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
        "Download Skeleton Image",
        data=cv2.imencode(".png", skeleton)[1].tobytes(),
        file_name="skeleton.png",
        mime="image/png"
    )

else:
    st.image("assets/demo.gif", caption="Demo Preview")
