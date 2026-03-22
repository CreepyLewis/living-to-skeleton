import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import tempfile

st.set_page_config(page_title="Living to Skeleton AI", page_icon="🦴")
st.title("🦴 Living to Skeleton AI (Skeleton Overlay Mode)")
st.write("Upload an image, video, or draw something.")

# --- Glow color ---
glow_color = st.color_picker("Skeleton Color", "#ffffff")

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

glow_rgb = hex_to_rgb(glow_color)

# --- Glow strength ---
glow_strength = st.slider("Glow Strength", 0.0, 1.0, 0.6)

# --- Skeleton overlay (stick figure) ---
def draw_skeleton(img, color=(255,255,255), strength=0.6):
    h, w, _ = img.shape
    overlay = img.copy()

    # Skeleton drawing
    thickness = 3

    # Head
    cv2.circle(overlay, (w//2, h//4), 25, color, thickness)

    # Body
    cv2.line(overlay, (w//2, h//4+25), (w//2, h//2), color, thickness)

    # Arms
    cv2.line(overlay, (w//2, h//3), (w//2-60, h//3+50), color, thickness)
    cv2.line(overlay, (w//2, h//3), (w//2+60, h//3+50), color, thickness)

    # Legs
    cv2.line(overlay, (w//2, h//2), (w//2-50, h-50), color, thickness)
    cv2.line(overlay, (w//2, h//2), (w//2+50, h-50), color, thickness)

    # Glow effect
    glow = cv2.GaussianBlur(overlay, (21,21), 0)
    result = cv2.addWeighted(overlay, 1.0, glow, strength, 0)

    return result

# --- Upload ---
uploaded_file = st.file_uploader("Upload Image or Video", type=["png", "jpg", "jpeg", "mp4"])

if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()

    # ---------- IMAGE ----------
    if file_ext in ["png", "jpg", "jpeg"]:
        img = Image.open(uploaded_file).convert("RGB")
        img_np = np.array(img)

        result = draw_skeleton(img_np, glow_rgb, glow_strength)

        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="Original", use_column_width=True)
        with col2:
            st.image(result, caption="Skeleton Overlay", use_column_width=True)

        # Download
        save_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        Image.fromarray(result).save(save_path)

        st.download_button(
            "Download Image",
            data=open(save_path, "rb").read(),
            file_name="skeleton.png",
            mime="image/png"
        )

    # ---------- VIDEO ----------
    elif file_ext == "mp4":
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())

        cap = cv2.VideoCapture(tfile.name)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        stframe = st.empty()
        progress = st.progress(0)

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = draw_skeleton(frame_rgb, glow_rgb, glow_strength)

            out.write(cv2.cvtColor(result, cv2.COLOR_RGB2BGR))

            # Preview (scaled)
            if count % 3 == 0:
                preview = cv2.resize(result, (400, int(400*height/width)))
                stframe.image(preview, channels="RGB")

            count += 1
            progress.progress(count / total_frames)

        cap.release()
        out.release()

        st.success("Video ready!")
        st.video(output_path)

        st.download_button(
            "Download Video",
            data=open(output_path, "rb").read(),
            file_name="skeleton.mp4",
            mime="video/mp4"
        )

# ---------- DRAW ----------
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
    key="canvas",
)

if canvas_result.image_data is not None:
    drawn = cv2.cvtColor(canvas_result.image_data.astype(np.uint8), cv2.COLOR_RGBA2RGB)
    result = draw_skeleton(drawn, glow_rgb, glow_strength)

    st.image(result, caption="Skeleton Drawing")

    save_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    Image.fromarray(result).save(save_path)

    st.download_button(
        "Download Drawing",
        data=open(save_path, "rb").read(),
        file_name="drawing.png",
        mime="image/png"
    )
