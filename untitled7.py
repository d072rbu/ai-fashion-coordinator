import streamlit as st
from openai import OpenAI
import requests
import base64

# ===============================
# ☁️ APIキーの読み込み
# ===============================
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENWEATHER_KEY = st.secrets["OPENWEATHER_KEY"]
HUGGINGFACE_TOKEN = st.secrets["HUGGINGFACE_TOKEN"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# 💙 天気取得
# ===============================
def get_weather(city="Tokyo"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric&lang=ja"
    res = requests.get(url).json()
    desc = res["weather"][0]["description"]
    temp = res["main"]["temp"]
    return f"{city}の天気は{desc}、気温は{temp}℃です。"

# ===============================
# 👚 コーデ提案（OpenAI）
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
    return response.choices[0].message.content

# ===============================
# 🎨 コーデ画像生成（Hugging Face）
# ===============================
def generate_outfit_image(prompt):
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    payload = {"inputs": prompt}
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        st.warning(f"⚠️ 画像生成に失敗しました: {response.text}")
        return None

    image_bytes = response.content
    return image_bytes

# ===============================
# 💙 Streamlit UI
# ===============================
st.title("💙 AIファッションアドバイザー 🎨")
st.write("🌤️ 天気と気分から今日のコーデと画像を提案します！")

keyword = st.text_input("💬 今日のキーワードを入力（例：デート、韓国、カジュアル）")

if st.button("コーデを提案して！ 💙"):
    with st.spinner("AIが考え中です...💭"):
        coord_text = ai_stylist(keyword)
        st.subheader("👗 今日のコーデ提案")
        st.write(coord_text)

        st.subheader("🎨 イメージ画像")
        image = generate_outfit_image(f"{keyword} fashion outfit, aesthetic, full body")
        if image:
            st.image(image, caption="今日のおすすめコーデ", use_container_width=True)
        else:
            st.warning("⚠️ 画像を表示できませんでした。")
