import streamlit as st
from openai import OpenAI
import requests

# 💙 Streamlit 韓国シンプルクール（青系）デザイン
st.markdown(
    """
    <style>
    /* 背景：くすみブルー×白のドット */
    .stApp {
        background-color: #f4f8fb;
        background-image: radial-gradient(#c9d8e6 1px, transparent 1px);
        background-size: 18px 18px;
        color: #2b2b2b;
        font-family: "Noto Sans KR", "Yu Gothic", "Helvetica Neue", sans-serif;
    }

    /* タイトル */
    h1 {
        color: #244f75;
        text-align: center;
        font-size: 2em;
        letter-spacing: 1px;
        font-weight: 600;
        border


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
    return f"{city}の天気が{desc}で気温は{temp}℃"

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
# 🎨 （今回は無効）コーデ画像生成関数
# ===============================
# def generate_image(description):
#     image_prompt = f"{description}, おしゃれな全身コーデ, リアルな人物, 明るい背景, 韓国風"
#     image = client.images.generate(
#         model="gpt-image-1",
#         prompt=image_prompt,
#         size="1024x1024"
#     )
#     url = image.data[0].url
#     return url

# ===============================
# 🎀 Streamlit画面構成
# ===============================
st.title("👗 AIファッションアドバイザー")
st.write("天気と気分から今日のコーデをAIが提案します💡")

keyword = st.text_input("今日の気分やキーワードを入力してね（例：デート、韓国っぽ、カジュアル）")

if st.button("コーデを提案して！"):
    with st.spinner("AIが考え中です...🧠💭"):
        coord_text = ai_stylist(keyword)

        # 🧥 結果表示
        st.subheader("🧥 今日のAIコーデ提案")
        st.write(coord_text)

        # 🎨 画像部分は無効化中
        # st.subheader("🎨 コーデ画像")
        # try:
        #     image_url = generate_image(coord_text)
        #     st.image(image_url, caption="AIが提案したコーデ", use_column_width=True)
        # except Exception as e:
        #     st.error("❌ 画像生成中にエラーが発生しました")
        #     st.write(f"エラー内容: {e}")

        st.success("🌸 今日も素敵な一日を！いってらっしゃい 💕")
