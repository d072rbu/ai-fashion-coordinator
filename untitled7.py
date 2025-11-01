import streamlit as st
from openai import OpenAI
import requests

# 🎨 Streamlit 韓国シンプルクール系デザイン
st.markdown(
    """
    <style>
    /* 背景を白ベースにして、ドット柄を控えめに */
    .stApp {
        background-color: #fafafa;
        background-image: radial-gradient(#dcdcdc 1px, transparent 1px);
        background-size: 18px 18px;
        color: #2b2b2b;
        font-family: "Noto Sans KR", "Yu Gothic", "Helvetica Neue", sans-serif;
    }

    /* タイトル */
    h1 {
        color: #2b2b2b;
        text-align: center;
        font-size: 2em;
        letter-spacing: 1px;
        font-weight: 600;
        border-bottom: 2px solid #dcdcdc;
        padding-bottom: 10px;
        margin-bottom: 25px;
    }

    /* サブタイトル */
    h2, h3 {
        color: #444;
        font-weight: 500;
        border-left: 4px solid #aaa;
        padding-left: 8px;
        margin-top: 25px;
    }

    /* 入力ボックス */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 1.5px solid #bcbcbc;
        background-color: #ffffff;
        color: #333;
        padding: 8px 12px;
        font-size: 1em;
        transition: all 0.2s ease-in-out;
    }

    .stTextInput>div>div>input:focus {
        border: 1.5px solid #666;
        box-shadow: 0 0 0 3px rgba(0,0,0,0.05);
    }

    /* ボタン */
    button[kind="primary"] {
        background-color: #2b2b2b !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 10px 28px !important;
        letter-spacing: 0.5px;
        transition: all 0.3s ease !important;
    }

    button[kind="primary"]:hover {
        background-color: #555 !important;
        transform: scale(1.03);
    }

    /* テキスト全体 */
    p, li {
        font-size: 1.05em;
        line-height: 1.7em;
        color: #333;
    }

    /* 成功メッセージ */
    .stSuccess {
        background-color: #f6f6f6 !important;
        border-left: 4px solid #555 !important;
        color: #2b2b2b !important;
        font-weight: 400;
    }

    /* 画像を少し角丸に */
    img {
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }

    /* フッター非表示（すっきり） */
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)


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
