import streamlit as st
from openai import OpenAI
import requests

# ===============================
# APIキーの読み込み
# ===============================
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
HUGGINGFACE_TOKEN = st.secrets["HUGGINGFACE_TOKEN"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# コーデ提案（OpenAI）
# ===============================
def ai_stylist(keyword):
    style_desc = f"""
あなたは韓国の人気スタイリストです。
キーワード: {keyword}

[指示]
・服だけのコーデ画像を提案してください。
・人物は不要、ハンガーにかけた服のイメージ。
・画像生成用に、一文で「服の色・形・素材」をまとめてください。
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": style_desc}]
    )
    text = response.choices[0].message.content
    return text

# ===============================
# 服画像生成（人物なし）
# ===============================
def generate_outfit_image(coord_text):
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

    full_prompt = f"""
Fashion outfit only: {coord_text}, displayed on hangers or mannequin, high-quality fashion photography,
studio lighting, realistic textures, minimal background, no person, no human, clothing only
"""

    payload = {
        "inputs": full_prompt,
        "parameters": {
            "num_inference_steps": 30,
            "guidance_scale": 7.0,
            "negative_prompt": "person, human, face, head, body, model"
        }
    }

    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code != 200:
        st.warning(f"⚠️ 画像生成に失敗しました: {response.text}")
        return None

    return response.content

# ===============================
# Streamlit UI
# ===============================
st.title("💙 AIファッションアドバイザー 🎨")
st.write("🌤️ 今日のコーデを提案！（人物なし・服だけ）")

keyword = st.text_input("💬 今日のキーワードを入力（例：デート、韓国、カジュアル）")

if st.button("コーデを提案して！ 💙"):
    with st.spinner("AIが考え中です...💭"):
        # コーデテキスト生成
        coord_text = ai_stylist(keyword)
        st.subheader("👗 今日のコーデ提案")
        st.write(coord_text)

        # 画像生成
        st.subheader("🎨 イメージ画像（ハンガーにかけた服・人物ゼロ）")
        image = generate_outfit_image(coord_text)
        if image:
            st.image(image, caption="今日のおすすめコーデ（服だけ）", use_container_width=True)
        else:
            st.warning("⚠️ 画像を表示できませんでした。")
