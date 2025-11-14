import streamlit as st
from openai import OpenAI
import requests

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
- シルエットや素材感、色の組み合わせを詳しく説明し、自然で洗練されたスタイルに。
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

    # OpenAIでテキスト生成
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": style_desc}]
    )

    text = response.choices[0].message.content
    return style, text


# ===============================
# 🎨 コーデ画像生成（Stable Diffusion）
# ===============================
def generate_outfit_image(prompt):
   api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
   headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

    # ファッション誌のようなリアルでおしゃれな画像を生成
full_prompt = f"""
A full-body photo of a person wearing {prompt}, stylish outfit,
high-quality fashion photography, natural lighting, street style, minimal background.
"""

payload = {"inputs": full_prompt}
response = requests.post(api_url, headers=headers, json=payload)

if response.status_code != 200:
st.warning(f"⚠️ 画像生成に失敗しました: {response.text}")
return None

return response.content


# ===============================
# 💙 Streamlit UI
# ===============================
st.title("💙 AIファッションアドバイザー 🎨")
st.write("🌤️ 天気と気分から今日のコーデと画像を提案します！")

keyword = st.text_input("💬 今日のキーワードを入力（例：デート、韓国、カジュアル）")

if st.button("コーデを提案して！ 💙"):
    with st.spinner("AIが考え中です...💭"):
        # テキスト提案
        style, coord_text = ai_stylist(keyword)
        st.subheader("👗 今日のコーデ提案")
        st.write(f"💫 スタイルタイプ: {style}\n\n{coord_text}")

        # 画像生成
        st.subheader("🎨 イメージ画像")
        image = generate_outfit_image(f"{style}, {keyword} fashion outfit")
        if image:
            st.image(image, caption="今日のおすすめコーデ", use_container_width=True)
        else:
            st.warning("⚠️ 画像を表示できませんでした。")
