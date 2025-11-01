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
# 🎨 コーデ画像を生成する関数
# ===============================
def generate_image(description):
    image_prompt = f"{description}, おしゃれな全身コーデ, リアルな人物, 明るい背景, 韓国風"
    image = client.images.generate(
        model="gpt-image-1",
        prompt=image_prompt,
        size="1024x1024"
    )
    url = image.data[0].url
    return url

# ===============================
# 🎀 Streamlit画面構成
# ===============================
st.title("👗 AIファッションアドバイザー")
st.write("天気と気分から今日のコーデをAIが提案します💡")

keyword = st.text_input("今日の気分やキーワードを入力してね（例：デート、韓国っぽ、カジュアル）")

if st.button("コーデを提案して！"):
    with st.spinner("AIが考え中です...🧠💭"):
        coord_text = ai_stylist(keyword)
        st.subheader("🧥 今日のAIコーデ提案")
        st.write(coord_text)

        st.subheader("🎨 コーデ画像")
        image_url = generate_image(coord_text)
        st.image(image_url, caption="AIが提案したコーデ", use_column_width=True)
        st.success("🌸 今日も素敵な一日を！いってらっしゃい 💕")
