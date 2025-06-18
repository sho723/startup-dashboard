import streamlit as st
import pandas as pd
import json
from datetime import datetime
from utils.logo_fetcher import fetch_company_logo
from utils.data_manager import load_data, save_data, add_startup

# ページ設定
st.set_page_config(
    page_title="Startup Contact Dashboard",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Startup Contact Dashboard")

# データ読み込み
startups = load_data()

# サイドバー - 新しいスタートアップ追加
st.sidebar.header("新しいスタートアップを追加")

with st.sidebar.form("add_startup"):
    company_name = st.text_input("会社名")
    contact_person = st.text_input("担当者名")
    email = st.text_input("メールアドレス")
    status = st.selectbox("ステータス", ["初期接触", "商談中", "保留", "成約", "見送り"])
    notes = st.text_area("メモ")
    
    if st.form_submit_button("追加"):
        if company_name:
            # ロゴを自動取得
            logo_url = fetch_company_logo(company_name)
            
            startup_data = {
                "company_name": company_name,
                "contact_person": contact_person,
                "email": email,
                "status": status,
                "notes": notes,
                "logo_url": logo_url,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            add_startup(startups, startup_data)
            save_data(startups)
            st.sidebar.success(f"{company_name} を追加しました！")
            st.rerun()

# メインエリア - ダッシュボード表示
if startups:
    # フィルター
    col1, col2 = st.columns([1, 1])
    with col1:
        status_filter = st.selectbox("ステータスでフィルター", 
                                   ["全て"] + list(set([s["status"] for s in startups])))
    with col2:
        search_term = st.text_input("会社名で検索")

    # フィルタリング
    filtered_startups = startups
    if status_filter != "全て":
        filtered_startups = [s for s in filtered_startups if s["status"] == status_filter]
    if search_term:
        filtered_startups = [s for s in filtered_startups if search_term.lower() in s["company_name"].lower()]

    # 統計情報
    st.subheader("📊 統計情報")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総スタートアップ数", len(startups))
    with col2:
        active_count = len([s for s in startups if s["status"] in ["初期接触", "商談中", "保留"]])
        st.metric("アクティブ案件", active_count)
    with col3:
        success_count = len([s for s in startups if s["status"] == "成約"])
        st.metric("成約数", success_count)
    with col4:
        success_rate = f"{(success_count/len(startups)*100):.1f}%" if startups else "0%"
        st.metric("成約率", success_rate)

    # スタートアップカード表示
    st.subheader("💼 スタートアップ一覧")
    
    # グリッドレイアウト
    cols = st.columns(3)
    for i, startup in enumerate(filtered_startups):
        with cols[i % 3]:
            with st.container():
                # ステータスに応じた色分け
                status_colors = {
                    "初期接触": "🔵",
                    "商談中": "🟡", 
                    "保留": "🟠",
                    "成約": "🟢",
                    "見送り": "🔴"
                }
                
                st.markdown(f"### {status_colors.get(startup['status'], '⚪')} {startup['company_name']}")
                
                # ロゴ表示
                if startup.get('logo_url'):
                    try:
                        st.image(startup['logo_url'], width=100)
                    except:
                        st.write("🏢 ロゴ未取得")
                else:
                    st.write("🏢 ロゴ未取得")
                
                st.write(f"**担当者:** {startup.get('contact_person', 'N/A')}")
                st.write(f"**メール:** {startup.get('email', 'N/A')}")
                st.write(f"**ステータス:** {startup['status']}")
                
                if startup.get('notes'):
                    with st.expander("メモを見る"):
                        st.write(startup['notes'])
                
                # 編集・削除ボタン
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button(f"編集", key=f"edit_{i}"):
                        st.session_state[f"edit_mode_{i}"] = True
                with col_delete:
                    if st.button(f"削除", key=f"delete_{i}"):
                        startups.remove(startup)
                        save_data(startups)
                        st.rerun()
                
                st.divider()

else:
    st.info("まだスタートアップが登録されていません。サイドバーから追加してください。")

# フッター
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
