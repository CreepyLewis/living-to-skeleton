import streamlit as st
import numpy as np
from PIL import Image
import cv2

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴")

st.title("🦴 Living to Skeleton AI")
st.write("Upload an image and convert it to skeleton lines.")

def skeletonize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)

    skel = np.zeros(binary.shape,np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))

    while True:
        eroded = cv2.erode(binary,element)
        temp = cv2.dilate(eroded,element)
        temp = cv2.subtract(binary,temp)
        skel = cv2.bitwise_or(skel,temp)
        binary = eroded.copy()

        if cv2.countNonZero(binary)==0:
            break

    return skel


uploaded = st.file_uploader("Upload Image",type=["png","jpg","jpeg"])

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    img = np.array(image)

    skeleton = skeletonize(img)

    col1,col2 = st.columns(2)

    with col1:
        st.image(img,caption="Original")

    with col2:
        st.image(skeleton,caption="Skeleton")
