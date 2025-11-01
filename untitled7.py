# -*- coding: utf-8 -*-
"""AIファッションアドバイザー (安全版)"""

# ===============================
# ✅ 必要なライブラリをインストール
# ===============================
# ColabやStreamlit Cloudで動かすときに自動でインストールされるようにする


# ===============================
# ✅ モジュールをインポート
# ===============================
import os
# -*- coding: utf-8 -*-
from openai import OpenAI
import requests
from IPython.display import Image, display
import streamlit as st

# 🔑 APIキーは環境変数から取得
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
    return response.choices[0].message.content

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
# 💬 実行部分
# ===============================
keyword = input("今日の気分やキーワードを入力してね（例：デート、韓国っぽ、カジュアル）👉 ")

coord_text = ai_stylist(keyword)
print("🧥 今日のAIコーデ提案:\n")
print(coord_text)

print("\n🎨 コーデ画像生成中...")
image_url = generate_image(coord_text)
display(Image(url=image_url))
print(f"🖼️ 参考画像URL: {image_url}")
