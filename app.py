import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.title("🦴 Living to Skeleton App")

uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    skeleton = cv2.ximgproc.thinning(thresh)

    st.subheader("Original Image")
    st.image(img)

    st.subheader("Skeleton Image")
    st.image(skeleton)
