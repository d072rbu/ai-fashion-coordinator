# ... (省略) ...

# ===============================
# 👚 コーデ生成（OpenAI）
# ===============================
def ai_stylist(keyword, city="Tokyo"):
    weather = get_weather(city) # 天気情報を取得
    style = "シンプルクール系"
    prompt = f"""
あなたはVOGUEのスタイリストです。
今日の{city}の天気は{weather}です。
キーワード: {keyword}を考慮して、以下の条件でコーデを提案してください。

- {weather}に合う、シンプルで洗練されたコーデ。
- どんなシーンに合うか、具体的なアドバイスも加えてください。
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    text = res.choices[0].message.content
    return style, text, weather # <<-- 天気情報も一緒に返すように変更

# ... (省略) ...

# ===============================
# 💙 Streamlit UI
# ===============================
# ... (省略) ...

if st.button("コーデを提案して！ 💖"):
    # キーワードが空の場合は警告
    if not keyword:
        st.warning("キーワードを入力してください！😊")
    else:
        with st.spinner("AIが可愛くコーデを考えています…"):
            style, coord_text, current_weather = ai_stylist(keyword) # <<-- 天気情報も受け取る

        # 天気情報を可愛く表示するセクションを追加
        st.markdown(f"""
            <div style='padding:15px; border:2px dashed #B0E0E6; border-radius:15px; background-color:#F0F8FF; color:#4A4A4A; text-align:center; margin-bottom:20px;'>
                <h4>今日の天気予報 ☀️</h4>
                <p>📍 {current_weather}</p>
            </div>
        """, unsafe_allow_html=True)


        # カード風UIを新しいCSSクラスで表示
        st.markdown(
            f"""
            <div class='coord-card'>
                <h3>🎀 今日のコーデ提案</h3>
                <p><strong>✨ {style} ✨</strong></p>
                <p>{coord_text}</p>
            </div>
            """, unsafe_allow_html=True
        )
        
        st.balloons() # 提案後に風船のエフェクト！

        # 画像生成セクション
        with st.spinner("服の画像を生成中… ちょっと待ってね！"):
            img_bytes = generate_outfit_image(coord_text)
            
            if img_bytes:
                st.image(img_bytes, caption="✨ あなただけのコーデが完成！ ✨", use_container_width=True) # キャプションも可愛く
            else:
                # 画像生成に失敗した場合のダミー画像を可愛く表示
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


        # ランダムポジティブメッセージを装飾
        messages = [
            "🌈 **今日もぜったい良い一日になるよ！楽しんでね💙**",
            "✨ **無理せず、自分のペースでいこうね。あなたなら大丈夫！**",
            "💫 **小さな一歩でも素敵な一日につながるよ。頑張りすぎないでね！**",
            "🌷 **今日のあなたもすごく素敵。リラックスしていってらっしゃい！**",
            "☀️ **今日はきっといいことがある日！楽しみにしててね💙**"
        ]
        st.markdown(f"<div style='margin-top:20px; text-align:center; font-size:1.1em; color:#E91E63;'>{random.choice(messages)}</div>", unsafe_allow_html=True)
