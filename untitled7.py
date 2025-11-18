import streamlit as st
from openai import OpenAI
import requests
import base64

# ===============================
# 🔑 Secrets
# ===============================
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENWEATHER_KEY = st.secrets["OPENWEATHER_KEY"]
HUGGINGFACE_TOKEN = st.secrets["HUGGINGFACE_TOKEN"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# 🌤️ 天気取得
# ===============================
def get_weather(city="Tokyo"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric&lang=ja"
    res = requests.get(url).json()
    desc = res["weather"][0]["description"]
    temp = res["main"]["temp"]
    return f"{city}の天気は{desc}、気温は{temp}℃です。"

# ===============================
# 👗 AIコーデ生成
# ===============================
def ai_stylist(keyword, city="Tokyo"):
    weather = get_weather(city)
    keyword_lower = keyword.lower()

    if "enzoblue" in keyword_lower or "モード" in keyword_lower or "韓国" in keyword_lower:
        style = "モード×ミニマルストリート（Enzoblue系）"
        prompt = f"""
あなたは韓国『ENZOBLUE』のスタイリストです。
今日の{weather}
キーワード: {keyword}

- ミニマル・アーバン・ニュートラルカラー。
- 素材感やシルエットを詳しく説明。
- 最後に「画像生成用：◯◯」で服の色・形・素材を一文でまとめる。
"""
    elif "デート" in keyword_lower or "可愛い" in keyword_lower:
        style = "フェミニンナチュラル系"
        prompt = f"""
あなたは韓国の人気スタイリストです。
今日の{weather}
キーワード: {keyword}

- 柔らかい印象・パステルカラー・シフォン/リネン。
- 最後に「画像生成用：◯◯」を出力。
"""
    else:
        style = "シンプルクール系"
        prompt = f"""
あなたは『VOGUE Korea』のスタイリストです。
今日の{weather}
キーワード: {keyword}

- シンプルで洗練された雰囲気。
- 最後に「画像生成用：◯◯」を出力。
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    text = res.choices[0].message.content
    return style, text

# ===============================
# 🎨 服画像生成（SDXL）
# ===============================
def generate_outfit_image(coord_text):
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

    prompt = f"""
Fashion outfit only on hanger, clothing only, no person, no human.
High-quality studio lighting, minimal background.
{coord_text}
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 30,
            "guidance_scale": 7.0,
            "negative_prompt": "person, human, body, face"
        }
    }

    res = requests.post(api_url, headers=headers, json=payload)

    if res.status_code != 200:
        st.error(f"画像生成失敗: {res.text}")
        return None

    return res.content  # PNG bytes

# ===============================
# 🧊 2D → 3D（TripoSR）
# ===============================
def convert_to_3d(image_bytes):
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-fast-3d"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_TOKEN}",
        "Accept": "model/gltf-binary"
    }

    res = requests.post(api_url, headers=headers, data=image_bytes)

    if res.status_code != 200:
        st.error(f"3Dモデル生成失敗: {res.status_code} {res.text}")
        return None

    return res.content  # GLBバイナリ

# ===============================
# 🌀 Three.js 3Dビューア
# ===============================
def show_3d_model(glb_bytes):
    glb_b64 = base64.b64encode(glb_bytes).decode()

    st.components.v1.html(f"""
    <canvas id="canvas3d" style="width:100%; height:400px;"></canvas>
    <script type="module">
        import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.module.js';
        import {{ GLTFLoader }} from 'https://cdn.jsdelivr.net/npm/three@0.152.2/examples/jsm/loaders/GLTFLoader.js';

        const canvas = document.getElementById("canvas3d");
        const renderer = new THREE.WebGLRenderer({{ canvas, antialias: true }});
        renderer.setSize(canvas.clientWidth, canvas.clientHeight);

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, canvas.clientWidth/canvas.clientHeight, 0.1, 1000);
        camera.position.z = 2;

        const light = new THREE.HemisphereLight(0xffffff, 0x333333, 1.2);
        scene.add(light);

        const loader = new GLTFLoader();
        loader.parse(atob("{glb_b64}"), "", function (gltf) {{
            const model = gltf.scene;
            scene.add(model);

            function animate() {{
                requestAnimationFrame(animate);
                model.rotation.y += 0.01;  // 自動回転
                renderer.render(scene, camera);
            }}
            animate();
        }});
    </script>
    """, height=450)

# ===============================
# UI
# ===============================
st.title("💙 AIファッションアドバイザー（3D回転モデル付き）💙")
st.write("AIが服を生成し、さらに3Dモデル化して360°回します ✨")

keyword = st.text_input("今日のキーワード（韓国、モード、デート、シンプル…）")

if st.button("コーデを提案して！"):
    with st.spinner("AIがコーデを考えています…"):
        style, coord_text = ai_stylist(keyword)

    st.subheader("👗 コーデ提案")
    st.write(f"💫 スタイルタイプ: **{style}**")
    st.write(coord_text)

    with st.spinner("服画像を生成中…"):
        img = generate_outfit_image(coord_text)

    if img:
        st.image(img, caption="生成された服（2D画像）", use_container_width=True)

        with st.spinner("3Dモデル生成中…（30秒ほど）"):
            glb = convert_to_3d(img)

        if glb:
            st.subheader("🌀 360° 回転ビュー")
            show_3d_model(glb)
