import streamlit as st
from openai import OpenAI
import requests

# ===============================
# 🌤️ APIキーの読み込み（安全）
# ===============================
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENWEATHER_KEY = st.secrets["OPENWEATHER_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# 🌈 デザイン設定（青×白で爽やか）
# ===============================
st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        color: #1a2a6c;
        font-family: 'Noto Sans JP', sans-serif;
    }
    .main {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 0 20px rgba(0,0,0,0.05);
    }
    h1, h2, h3 {
        color: #1a2a6c;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #89CFF0;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        border: none;
        padding: 0.6em 1.2em;
    }
    .stButton>button:hover {
        background-color: #58A4E0;
        transition: 0.3s;
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
# 📸 無料の参考画像を取得する関数（Unsplash）
# ===============================
def get_reference_image(keyword):
    url = f"https://source.unsplash.com/800x800/?{keyword},outfit,fashion"
    return url

# ===============================
# 🎀 Streamlit画面構成
# ===============================
st.title("💙 AIファッションアドバイザー 💙")
st.write("☁️ 天気と気分から今日のコーデをAIが提案します ☀️🍀")

keyword = st.text_input("🌸 今日の気分やキーワードを入力してね（例：デート、韓国っぽ、カジュアル）")

if st.button("コーデを提案して！ 🎀"):
    with st.spinner("AIが考え中です...🧠💭"):
        coord_text = ai_stylist(keyword)
        st.subheader("🧥 今日のAIコーデ提案")
        st.write(coord_text)

        st.subheader("📸 参考コーデ画像（Unsplashより）")
        image_url = get_reference_image(keyword)
        st.image(image_url, caption="AIが選んだ参考コーデ画像", use_column_width=True)

        st.success("🍀 今日もあなたらしく、素敵な一日を！ 💙")
