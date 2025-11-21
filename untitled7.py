import streamlit as st
from openai import OpenAI
import requests
import random

# ===============================
# 🔑 Secrets 読み込み
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
# 👚 コーデ生成（OpenAI）
# ===============================
def ai_stylist(keyword, city="Tokyo", mood_color=None):
    weather = get_weather(city)
    style = "シンプルクール系"
    prompt = f"""
あなたはVOGUEのスタイリストです。
今日の{weather}
キーワード: {keyword}

- シンプルで洗練されたコーデ。
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    text = res.choices[0].message.content
    return style, text

# ===============================
# 🎨 服画像生成（SDXL / Router API）
# ===============================
def generate_outfit_image(coord_text):
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

    prompt = f"""
Fashion outfit only on hanger, no human, no body, high-quality studio photo.
{coord_text}
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 30,
            "guidance_scale": 7.0,
            "negative_prompt": "person, human, face, body"
        }
    }

    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code != 200:
        st.warning(f"⚠️ 画像生成失敗: {response.text}")
        return None

    return response.content

# ===============================
# 💙 Streamlit UI
# ===============================
st.set_page_config(page_title="AIファッションアドバイザー", layout="centered")
st.title("💙 AIファッションアドバイザー 🎨")

# 背景色とボタンのカスタマイズ
st.markdown(
    """
    <style>
    body { background-color: #FFF8F0; }
    .stButton>button { background-color: #FF69B4; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True
)

# 今日の気分カラー選択
mood_color = st.color_picker("🎨 今日の気分カラーを選んでね")

keyword = st.text_input("💬 今日のキーワードを入力（例：デート、韓国、カジュアル）")

if st.button("コーデを提案して！ 💙"):
    with st.spinner("AIがコーデを考えています…"):
        style, coord_text = ai_stylist(keyword, mood_color=mood_color)

        # カード風UI
        st.markdown(
            f"""
            <div style='padding:15px; border:2px solid #FF69B4; border-radius:15px; background-color:#FFF0F5'>
                <h3>👗 今日のコーデ提案</h3>
                <p>{coord_text}</p>
                <p>💫 スタイル: {style}</p>
            </div>
            """, unsafe_allow_html=True
        )

    with st.spinner("服の画像を生成中…"):
        img_bytes = generate_outfit_image(coord_text)
        if img_bytes:
            st.image(img_bytes, caption="生成した服（2D画像）", use_container_width=True)
        else:
            st.warning("⚠️ 画像を表示できませんでした。")

    # ランダムポジティブメッセージ
    messages = [
        "🌈 **今日もぜったい良い一日になるよ！楽しんでね💙**",
        "✨ **無理せず、自分のペースでいこうね。あなたなら大丈夫！**",
        "💫 **小さな一歩でも素敵な一日につながるよ。頑張りすぎないでね！**",
        "🌷 **今日のあなたもすごく素敵。リラックスしていってらっしゃい！**",
        "☀️ **今日はきっといいことがある日！楽しみにしててね💙**"
    ]
    st.markdown(random.choice(messages))
