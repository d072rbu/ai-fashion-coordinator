import streamlit as st
from openai import OpenAI
import requests

# ===============================
# 🔑 APIキー設定
# ===============================
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENWEATHER_KEY = st.secrets["OPENWEATHER_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# 🌸 ページ設定
# ===============================
st.set_page_config(page_title="AIファッションアドバイザー", page_icon="👗", layout="centered")

# ===============================
# 💅 フォント選択
# ===============================
font_choice = st.selectbox(
    "フォントスタイルを選んでね 💅",
    ["Noto Sans KR", "Pretendard", "SUIT"]
)

font_urls = {
    "Noto Sans KR": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap",
    "Pretendard": "https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css",
    "SUIT": "https://cdn.jsdelivr.net/gh/sunn-us/SUIT/fonts/static/woff2/SUIT.css"
}

font_family = font_choice

# ===============================
# 🌿 スタイル
# ===============================
st.markdown(f"""
    <style>
    @import url('{font_urls[font_choice]}');

    html, body, [class*="css"] {{
        font-family: '{font_family}', sans-serif;
        background-color: #ffffff;
        color: #334155;
    }}

    h1 {{
        color: #2563eb;
        text-align: center;
        font-size: 2.4em;
        font-weight: 700;
        margin-bottom: 0.3em;
    }}

    .subtitle {{
        text-align: center;
        color: #64748b;
        font-size: 1.1em;
        margin-bottom: 2em;
    }}

    .stTextInput>div>div>input {{
        border: 1.5px solid #93c5fd;
        border-radius: 10px;
        background-color: #f8fafc;
        color: #334155;
        font-size: 1em;
        padding: 0.5em 0.8em;
    }}

    .stButton>button {{
        background-color: #3b82f6;
        color: white;
        font-weight: 600;
        border-radius: 14px;
        padding: 0.6em 1.4em;
        border: none;
        box-shadow: 0 3px 6px rgba(59,130,246,0.2);
        transition: all 0.2s ease-in-out;
        font-family: '{font_family}', sans-serif;
        font-size: 1em;
    }}

    .stButton>button:hover {{
        background-color: #2563eb;
        transform: scale(1.05);
    }}

    .stMarkdown p {{
        font-size: 1.05em;
        line-height: 1.8em;
        color: #334155;
    }}

    .card {{
        background: #f9fafb;
        border-radius: 20px;
        padding: 1.5em;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin: 1.5em 0;
    }}
    </style>
""", unsafe_allow_html=True)

# ===============================
# ☁️ 天気を取得
# ===============================
def get_weather(city="Tokyo"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric&lang=ja"
    res = requests.get(url).json()
    desc = res["weather"][0]["description"]
    temp = res["main"]["temp"]
    return f"{city}の天気は{desc}、気温は{temp}℃です。"

# ===============================
# 👗 AIファッション提案
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
# 🌸 UIレイアウト
# ===============================
st.markdown("<h1>👗 AIファッションアドバイザー 🍀🎵</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">天気と気分から、今日のあなたにぴったりのコーデを提案します💡</p>', unsafe_allow_html=True)

keyword = st.text_input("今日の気分やキーワードを入力してね（例：デート、韓国っぽ、カジュアル）")

if st.button("🌼 コーデを提案して！"):
    with st.spinner("AIが考え中です...🧠💭"):
        coord_text = ai_stylist(keyword)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧥 今日のAIコーデ提案 🍀")
        st.write(coord_text)
        st.markdown('</div>', unsafe_allow_html=True)
        st.success("🎵 今日も笑顔でいってらっしゃい 💙")
