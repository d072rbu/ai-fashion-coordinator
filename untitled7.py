import streamlit as st
from openai import OpenAI
import requests
import random
from io import BytesIO

# ===============================
# 🔑 Secrets 読み込みとクライアント初期化
# ===============================
# 環境変数またはsecrets.tomlからキーを読み込む
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    OPENWEATHER_KEY = st.secrets["OPENWEATHER_KEY"]
    HUGGINGFACE_TOKEN = st.secrets["HUGGINGFACE_TOKEN"]
except KeyError as e:
    st.error(f"⚠️ Secrets設定エラー: {e} が見つかりません。`.streamlit/secrets.toml`を確認してください。")
    st.stop()

# NameError 対策：client オブジェクトを初期化
client = OpenAI(api_key=OPENAI_API_KEY)


# ===============================
# 🌤️ 天気取得 (キャッシュ利用)
# ===============================
@st.cache_data(ttl=3600) # 1時間は結果をキャッシュ
def get_weather(city="Tokyo"):
    """OpenWeatherMapから天気情報を取得する関数"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric&lang=ja"
        res = requests.get(url, timeout=10).json()
        
        if res.get("cod") != 200:
             return f"天気情報が見つかりません: {res.get('message', '不明なエラー')}"
        
        desc = res["weather"][0]["description"]
        temp = res["main"]["temp"]
        return f"{city}の天気は{desc}、気温は{temp}℃です。"
    except requests.exceptions.RequestException:
        return f"天気取得に失敗しました。デフォルト値を使用します。"

# ===============================
# 👚 コーデ生成（OpenAI）
# ===============================
def ai_stylist(keyword, city="Tokyo"):
    """OpenAI APIを使ってコーディネートを生成する関数"""
    weather = get_weather(city) # 天気情報を取得
    style = "シンプルクール系" # スタイルはAIに決めさせるか、プロンプトで固定する

    prompt = f"""
あなたはVOGUEのカリスマスタイリストです。
今日の{city}の天気は{weather}です。
ユーザーからのキーワード: {keyword}を考慮し、以下の条件でコーデを提案してください。

- {weather}に合う、シンプルで洗練されたコーデ。
- 提案するコーディネートの全体像（スタイル、色、アイテム）を記述してください。
- 最後に、どんなシーン（例：カフェ、デート、オフィス）に合うか、具体的なアドバイスも加えてください。

提案は日本語で行い、スタイル名と詳細を分けて記述してください。
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    text = res.choices[0].message.content
    return style, text, weather # 天気情報も一緒に返す

# ===============================
# 🎨 服画像生成（SDXL / Router API）
# ===============================
def generate_outfit_image(coord_text):
    """Hugging Face Inference APIを使って画像を生成する関数"""
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    # Bearerの重複を修正
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"} 

    prompt = f"""
Fashion outfit only on hanger, no human, no body, high-quality studio photo, 4k, clean background.
{coord_text}
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "negative_prompt": "person, human, face, body, deformed, ugly, disfigured, bad anatomy, low quality, noise, blurry"
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=90) # タイムアウトを長めに設定
        response.raise_for_status() # HTTPエラーがあれば例外を発生させる
        
        # 画像が正常に返されたか確認
        if 'image' in response.headers.get('Content-Type', ''):
            return response.content
        else:
            # エラーレスポンスの内容を表示
            st.warning(f"⚠️ 画像生成APIから画像以外のレスポンスが返されました: {response.text[:200]}...") 
            return None
            
    except requests.exceptions.RequestException as e:
        st.warning(f"⚠️ 画像生成APIとの通信エラーが発生しました: {e}")
        return None


# ===============================
# 💙 Streamlit UI (デザイン部分)
# ===============================
st.set_page_config(
    page_title="きらきら AIファッションアドバイザー", 
    layout="centered", 
    initial_sidebar_state="collapsed",
    page_icon="💖"
)

# ✨ CSSで可愛くデザイン
st.markdown(
    """
    <style>
    .stApp { background-color: #F8F4F8; color: #4A4A4A; font-family: 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif; }
    .stTitle { color: #E91E63; text-align: center; margin-bottom: 20px; text-shadow: 1px 1px 3px #FFC1E3; }
    div.stButton > button:first-child {
        background-color: #FF69B4; color: #FFFFFF; font-weight: bold; border-radius: 20px; padding: 10px 30px;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1); border: none; transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover { background-color: #FFB6C1; color: #E91E63; box-shadow: 0 0 10px #FFB6C1; }
    div[data-testid="stTextInput"] > div > div > input {
        border-radius: 15px; border: 2px solid #FFC0CB; padding: 10px; box-shadow: inset 1px 1px 3px rgba(0, 0, 0, 0.05);
    }
    .coord-card {
        padding: 25px; border: 3px solid #FFC0CB; border-radius: 25px; 
        background-color: #FFFFFF; color: #4A4A4A;
        box-shadow: 4px 4px 10px rgba(255, 105, 180, 0.2); margin-top: 20px;
    }
    .coord-card h3 { color: #E91E63; border-bottom: 2px dashed #FFC0CB; padding-bottom: 10px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True
)

st.title("💖 きらきら AIファッションアドバイザー ✨")

# --- UI コンポーネント ---
keyword = st.text_input(
    label="今日のキーワードを入力してください", 
    placeholder="例：デート、カジュアル、モード系",
    label_visibility="collapsed"
)
st.caption("💬 上のボックスに、着たい服のイメージや、行く場所を入力してね！")

if st.button("コーデを提案して！ 💖"):
    if not keyword:
        st.warning("キーワードを入力してください！😊")
        st.stop()
        
    # --- 処理実行 ---
    with st.spinner("AIが可愛くコーデを考えています…"):
        style, coord_text, current_weather = ai_stylist(keyword)

    # 1. 天気情報表示
    st.markdown(f"""
        <div style='padding:15px; border:2px dashed #B0E0E6; border-radius:15px; background-color:#F0F8FF; color:#4A4A4A; text-align:center; margin-bottom:20px;'>
            <h4>今日の天気予報 ☀️</h4>
            <p>📍 {current_weather}</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. コーデ提案表示
    st.markdown(
        f"""
        <div class='coord-card'>
            <h3>🎀 今日のコーデ提案</h3>
            <p><strong>✨ スタイル: {style} ✨</strong></p>
            <p>{coord_text}</p>
        </div>
        """, unsafe_allow_html=True
    )
    st.balloons() # 提案後に風船のエフェクト！

    # 3. 画像生成セクション
    with st.spinner("服の画像を生成中… ちょっと待ってね！"):
        img_bytes = generate_outfit_image(coord_text)
        
        if img_bytes:
            st.image(img_bytes, caption="✨ あなただけのコーデが完成！ ✨", use_container_width=True)
        else:
            # 画像生成に失敗した場合の可愛らしい代替案
            st.warning("⚠️ ごめんなさい！服の画像を生成できませんでした。")
            st.markdown(
                """
                <div style='text-align:center; margin-top:15px;'>
                    <p>でも、コーデのアイデアはとっても素敵だよ！✨</p>
                    <img src="https://images.unsplash.com/photo-1558230501-460d37e3d231?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" 
                         style="width:80%; max-width:400px; border-radius:15px; box-shadow: 3px 3px 8px rgba(0,0,0,0.1);" 
                         alt="コーデイメージ">
                    <p style="font-size:0.8em; color:#888;">（イメージ画像です）</p>
                </div>
                """, unsafe_allow_html=True
            )


    # 4. ポジティブメッセージ
    messages = [
        "🌈 **今日もぜったい良い一日になるよ！楽しんでね💙**",
        "✨ **無理せず、自分のペースでいこうね。あなたなら大丈夫！**",
        "💫 **小さな一歩でも素敵な一日につながるよ。頑張りすぎないでね！**",
        "🌷 **今日のあなたもすごく素敵。リラックスしていってらっしゃい！**",
        "☀️ **今日はきっといいことがある日！楽しみにしててね💙**"
    ]
    st.markdown(f"<div style='margin-top:20px; text-align:center; font-size:1.1em; color:#E91E63;'>{random.choice(messages)}</div>", unsafe_allow_html=True)
