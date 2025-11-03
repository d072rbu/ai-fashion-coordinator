import streamlit as st
from openai import OpenAI
import requests
import urllib.parse

# ===============================
# 🌤️ APIキーの読み込み（安全）
# ===============================
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENWEATHER_KEY = st.secrets["OPENWEATHER_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# 🎨 デザイン設定（パステル空色×白）
# ===============================
st.markdown("""
    <style>
    body {
        background-color: #f8fbff;
        color: #335c81;
        font-family: 'Noto Sans JP', sans-serif;
    }
    .main {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 0 25px rgba(173, 216, 230, 0.25);
    }
    h1, h2, h3 {
        color: #3b6ea5;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #a3d5ff;
        color: #ffffff;
        font-size: 18px;
        font-weight: 600;
        border-radius: 12px;
        border: none;
        padding: 0.7em 1.4em;
    }
    .stButton>button:hover {
        background-color: #89c7f5;
        transition: 0.3s;
    }
    .stSuccess {
        color: #2a6f97 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ===============================
# ☁️ 天気を取得する関数
# ===============================
def get_weather(city="Tokyo"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric&lang=ja"
    res = requests.get(url).json()
    desc = res["weather"][0]["description"]
    temp = res["main"]["temp"]
    return f"{city}の天気は{desc}、気温は{temp}℃です。"

# ===============================
# 👚 AIにコーデ提案をしてもらう関数
# ===============================
def ai_stylist(keyword, city="Tokyo"):
    weather = get_weather(city)
    prompt = f"""
今日の{weather}
キーワード: {keyword}

この条件にぴったりのファッションコーデを提案して。
具体的な服の組み合わせと理由を説明して。
最後にポジティブな一言で締めて！
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    return text

# ===============================
# 📸 無料参考画像を取得（Unsplash）
# ===============================
def get_reference_image(keyword):
    english_keywords = {
        "韓国": "korean fashion outfit",
        "デート": "date outfit",
        "カジュアル": "casual outfit",
        "モノトーン": "minimal outfit",
        "フェミニン": "feminine outfit",
        "スポーティ": "sporty outfit",
    }

    search_term = english_keywords.get(keyword, f"{keyword} fashion outfit")
    search_term_encoded = urllib.parse.quote(search_term)
    url = f"https://source.unsplash.com/800x800/?{search_term_encoded}"
    return url

# ===============================
# 🎀 Streamlit画面構成
# ===============================
st.title("🌸 AIファッションアドバイザー 💙")
st.write("☁️ 天気と気分から今日のコーデをAIが提案します ✨🍀")

keyword = st.text_input("💬 今日の気分やキーワードを入力してね（例：デート、韓国、カジュアル）")

if st.button("コーデを提案して！ 💎"):
    with st.spinner("AIが考え中です...🧠💭"):
        coord_text = ai_stylist(keyword)
        st.subheader("👗 今日のAIコーデ提案")
        st.write(coord_text)

        st.subheader("📸 参考コーデ画像（無料・Unsplash）")
        image_url = get_reference_image(keyword)
        st.image(image_url, caption="AIが選んだ参考コーデ画像", use_column_width=True)

        st.success("🍀 今日もあなたらしく、空みたいに澄んだ一日を 💙")
