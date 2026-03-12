import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import mediapipe as mp
from ultralytics import YOLO

# ------------------------
# Page config
# ------------------------
st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴", layout="wide")
st.title("🦴 Living to Skeleton AI")
st.write("Upload an image, draw something, or take a photo to skeletonize living things only!")

# ------------------------
# Load models (cached)
# ------------------------
@st.cache_resource
def load_models():
    yolo = YOLO("yolov8n.pt")  # YOLOv8 nano model
    mp_pose = mp.solutions.pose.Pose()
    mp_draw = mp.solutions.drawing_utils
    return yolo, mp_pose, mp_draw

yolo, pose, mp_draw = load_models()

# ------------------------
# Human skeleton
# ------------------------
def draw_skeleton(img):
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)
    if results.pose_landmarks:
        mp_draw.draw_landmarks(img, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)
    return img

# ------------------------
# Detect living things and skeletonize
# ------------------------
def living_to_skeleton(img):
    results = yolo(img)[0]
    living_classes = ["person","dog","cat","horse","cow","sheep"]
    for box in results.boxes:
        cls = int(box.cls[0])
        label = yolo.names[cls]
        if label in living_classes:
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            roi = img[y1:y2, x1:x2]
            roi = draw_skeleton(roi)
            img[y1:y2, x1:x2] = roi
    return img

# ------------------------
# Upload Image
# ------------------------
st.header("📤 Upload Image")
uploaded = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])
if uploaded:
    image = Image.open(uploaded).convert("RGB")
    img = np.array(image)
    result = living_to_skeleton(img.copy())

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(img)
    with col2:
        st.subheader("Skeleton Result")
        st.image(result)

# ------------------------
# Draw Canvas
# ------------------------
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
    result = living_to_skeleton(img.copy())

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Drawing")
        st.image(img)
    with col2:
        st.subheader("Skeleton")
        st.image(result)

# ------------------------
# Webcam Mode
# ------------------------
st.header("📷 Webcam Skeleton Mode")
camera_image = st.camera_input("Take a picture")
if camera_image:
    image = Image.open(camera_image).convert("RGB")
    img = np.array(image)
    result = living_to_skeleton(img.copy())

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Camera Image")
        st.image(img)
    with col2:
        st.subheader("Skeleton")
        st.image(result)
