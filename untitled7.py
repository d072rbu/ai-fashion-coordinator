import streamlit as st
from openai import OpenAI
import requests
import random

# ===============================
# ☁️ APIキーの読み込み
# ===============================
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENWEATHER_KEY = st.secrets["OPENWEATHER_KEY"]
PIXABAY_KEY = st.secrets["PIXABAY_KEY"]

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
    keyword_lower = keyword.lower()

    if "enzoblue" in keyword_lower or "モード" in keyword_lower or "韓国" in keyword_lower:
        style = "モード×ミニマルストリート（Enzoblue系）"
        style_desc = f"""
あなたは韓国・ソウルの人気セレクトショップ『ENZOBLUE』のスタイリストです。
今日の{weather}
キーワード: {keyword}

[指示]
- [ユーザーのキーワード] に合うコーディネートを提案してください。
- enzoblueのような雰囲気（ミニマル、アーバン、ユニセックス、ニュートラルカラー、モード × ストリートのバランス）を参考にしてください。
- シルエットや素材感、色の組み合わせを詳しく説明し、写真のように自然で洗練されたスタイルにしてください。
- 性別は固定せず、誰でも真似できるスタイルに。
- 最後に“今日のスタイルで自信を持って歩こう”のような一言を添えて。
"""
    elif "デート" in keyword_lower or "可愛い" in keyword_lower:
        style = "フェミニンナチュラル系"
        style_desc = f"""
あなたは韓国の人気スタイリストです。
今日の{weather}
キーワード: {keyword}

[指示]
・デートやお出かけにぴったりな、優しくて柔らかい印象のコーデを提案してください。
・パステルカラーやシフォン、リネン素材を上品に組み合わせてください。
・全体の統一感とかわいさを意識して。
・最後にポジティブな一言を添えて。
"""
    else:
        style = "シンプルクール系"
        style_desc = f"""
あなたは韓国のファッション誌『VOGUE Korea』のスタイリストです。
今日の{weather}
キーワード: {keyword}

[指示]
・シンプルで洗練された、クールな大人のコーデを提案してください。
・無駄を省きながらも、素材感とシルエットで高見えするスタイルに。
・白・黒・ベージュ・グレーなどのニュートラルカラーを基調に。
・最後に前向きな一言を添えてください。
"""

    prompt = style_desc
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content
    return f"💫 スタイルタイプ: {style}\n\n{text}"

# ===============================
# 🎨 コーデ画像検索（Pixabay）
# ===============================
def generate_outfit_image(keyword):
    # 検索キーワードを少し具体的にする
    search_term = f"{keyword} fashion outfit full body"
    url = f"https://pixabay.com/api/?key={PIXABAY_KEY}&q={search_term}&image_type=photo&per_page=10"
    res = requests.get(url).json()

    if res["totalHits"] > 0:
        # ランダムに1枚選ぶ
        image_data = random.choice(res["hits"])
        return image_data["webformatURL"]
    else:
        st.warning("⚠️ Pixabayで画像が見つかりませんでした")
        return None

# ===============================
# 💙 Streamlit UI
# ===============================
st.title("💙 AIファッションアドバイザー 🎨")
st.write("🌤️ 天気と気分から今日のコーデと画像を提案します！")

keyword = st.text_input("💬 今日のキーワードを入力（例：デート、韓国、カジュアル）")

if st.button("コーデを提案して！ 💙"):
    with st.spinner("AIが考え中です...💭"):
        # コーデ提案
        coord_text = ai_stylist(keyword)
        st.subheader("👗 今日のコーデ提案")
        st.write(coord_text)

        # Pixabay画像表示
        st.subheader("🎨 イメージ画像")
        image_url = generate_outfit_image(keyword)
        if image_url:
            st.image(image_url, caption="今日のおすすめコーデ", use_container_width=True)
