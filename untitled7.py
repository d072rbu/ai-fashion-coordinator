# -*- coding: utf-8 -*-
"""AIファッションアドバイザー (安全版)"""

# ===============================
# ✅ 必要なライブラリをインストール
# ===============================
# ColabやStreamlit Cloudで動かすときに自動でインストールされるようにする
!pip install openai requests

# ===============================
# ✅ モジュールをインポート
# ===============================
import os
from openai import OpenAI
import requests
from IPython.display import Image, display

# ===============================
# 🔒 APIキーを安全に読み込む
# ===============================
# 環境変数 (Colabの場合はランタイムで設定 / Streamlitの場合は「secrets」で設定)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

# ✅ 確認（キーが設定されていない場合にエラー表示）
if not OPENAI_API_KEY or not OPENWEATHER_KEY:
    raise ValueError("❌ APIキーが設定されていません。Colabなら os.environ で、Streamlitなら secrets.toml に設定してください。")

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
