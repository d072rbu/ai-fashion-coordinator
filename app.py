import streamlit as st
import requests
import base64
import time

# -------------------------
# シークレット
# -------------------------
HUGGINGFACE_TOKEN = st.secrets["HUGGINGFACE_TOKEN"]

# SDXL Router URL
HF_ROUTER = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

st.set_page_config(layout="wide")
st.title("🎀 擬似360° マネキン（Phase1）")

keyword = st.text_input("キーワード（例：pastel dress kawaii）", value="pastel dress kawaii")
fps = st.slider("回転スピード（fps）", 1, 8, 2)

def generate_one_view(prompt):
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True},
        "parameters": {"num_inference_steps": 28, "guidance_scale": 7.5, "width":512, "height":768}
    }
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    r = requests.post(HF_ROUTER, headers=headers, json=payload, timeout=120)
    if r.status_code != 200:
        st.error(f"HF エラー: {r.status_code} {r.text}")
        return None
    content_type = r.headers.get("content-type","")
    if "application/json" in content_type:
        b64 = r.json().get("data")[0].get("image_base64")
        return base64.b64decode(b64)
    else:
        return r.content

def generate_4_views(base_prompt):
    directions = ["front view", "right side view", "back view", "left side view"]
    results = []
    for d in directions:
        prompt = f"{base_prompt}, {d}, cute 3D mannequin, pastel, studio, high detail"
        img = generate_one_view(prompt)
        if img is None:
            return None
        results.append(img)
    return results

if st.button("生成して擬似360°表示"):
    with st.spinner("生成中…（4方向画像）"):
        prompt_base = f"cute anime-style 3D mannequin wearing {keyword}"
        imgs = generate_4_views(prompt_base)
        if imgs is None:
            st.stop()
    st.success("生成完了！")

    # サムネイル表示
    cols = st.columns(4)
    for c, img, label in zip(cols, imgs, ["前","右","後","左"]):
        c.image(img, caption=label, use_column_width=True)

    # 擬似360°表示
    display = st.empty()
    delay = 1.0 / fps
    idx = 0
    loops = st.number_input("ループ回数（1回=4フレーム）", 1, 20, 5)
    for i in range(loops*4):
        display.image(imgs[idx], use_column_width=True)
        idx = (idx + 1) % 4
        time.sleep(delay)
    st.info("回転表示終了")
