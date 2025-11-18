import streamlit as st
from openai import OpenAI
import requests
import base64

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
def ai_stylist(keyword, city="Tokyo"):
    weather = get_weather(city)
    keyword_lower = keyword.lower()

    if "enzoblue" in keyword_lower or "モード" in keyword_lower or "韓国" in keyword_lower:
        style = "モード×ミニマルストリート（Enzoblue系）"
        prompt = f"""
あなたは韓国・ソウルの人気セレクトショップ『ENZOBLUE』のスタイリストです。
今日の{weather}
キーワード: {keyword}

- ミニマル、ニュートラルカラー、アーバン。
- 素材感・シルエットの説明。
- 最後に "画像生成用：◯◯" で服の色・形・素材を一文で出力。
"""
    elif "デート" in keyword_lower or "可愛い" in keyword_lower:
        style = "フェミニンナチュラル系"
        prompt = f"""
あなたは韓国の人気スタイリストです。
今日の{weather}
キーワード: {keyword}

- 柔らかい印象、シフォン・リネン・パステル。
- 最後に "画像生成用：◯◯" を出力。
"""
    else:
        style = "シンプルクール系"
        prompt = f"""
あなたはVOGUE Koreaのスタイリストです。
今日の{weather}
キーワード: {keyword}

- シンプルで洗練されたコーデ。
- 最後に "画像生成用：◯◯" を出力。
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

    # Router API は JSON で返す場合があるので対応
    try:
        result = response.json()
        if "generated_image" in result:
            image_bytes = base64.b64decode(result["generated_image"])
            return image_bytes
    except:
        pass

    # バイナリ直接返却の場合
    return response.content

# ===============================
# 💖 Streamlit UI
# ===============================
st.set_page_config(page_title="💖 AIファッションコーデアプリ", page_icon="👗")

st.title("💖 AIファッションコーデアプリ 👗")
st.write("今日はどんな服を着ようかな？キーワードを入れてね♪")

keyword = st.text_input("💬 キーワード（例：韓国、デート、モード）")

if st.button("コーデを作る！ ✨"):
    if not keyword.strip():
        st.warning("キーワードを入力してね！")
    else:
        with st.spinner("AIがコーデを考えています…💭"):
            style, coord_text = ai_stylist(keyword)
            st.subheader("👗 今日のコーデ提案")
            st.write(f"💫 スタイル: {style}")
            st.write(coord_text)

        with st.spinner("服の画像を生成中…🎨"):
            img_bytes = generate_outfit_image(coord_text)
            if img_bytes:
                st.image(img_bytes, caption="生成した服（ハンガー表示）", use_container_width=True)
            else:
                st.warning("⚠️ 画像を表示できませんでした。")
