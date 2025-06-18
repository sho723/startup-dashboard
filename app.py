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
    status = st.selectbox("ステータス", ["初期接触", "商談中", "保留", "成約", "見送り"])  # 変更点
    notes = st.text_area("メモ")
    
    if st.form_submit_button("追加"):
        if company_name:
            # ロゴを自動取得
            with st.spinner(f"{company_name}のロゴを取得中..."):
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

# デバッグ情報（開発時のみ表示）
if st.sidebar.checkbox("デバッグ情報を表示"):
    import os
    st.sidebar.write("**ファイルパス情報:**")
    st.sidebar.write(f"現在のディレクトリ: `{os.getcwd()}`")
    st.sidebar.write(f"dataフォルダ存在: {os.path.exists('data')}")
    st.sidebar.write(f"startups.json存在: {os.path.exists('data/startups.json')}")

# データのバックアップ・復元機能
st.sidebar.markdown("---")
st.sidebar.subheader("データ管理")

if st.sidebar.button("データをダウンロード"):
    if startups:
        json_str = json.dumps(startups, ensure_ascii=False, indent=2)
        st.sidebar.download_button(
            label="startups.json をダウンロード",
            data=json_str,
            file_name="startups_backup.json",
            mime="application/json"
        )
    else:
        st.sidebar.warning("データがありません")

uploaded_file = st.sidebar.file_uploader("データをアップロード", type=['json'])
if uploaded_file is not None:
    try:
        uploaded_data = json.load(uploaded_file)
        if st.sidebar.button("データを復元"):
            save_data(uploaded_data)
            st.sidebar.success("データを復元しました！")
            st.rerun()
    except Exception as e:
        st.sidebar.error(f"ファイル読み込みエラー: {e}")

# メインエリア - タブ機能
if startups:
    # 統計情報（全体）
    st.subheader("📊 統計情報")
    col1, col2, col3, col4 = st.columns(4)
    
    # アクティブ案件の定義を変更（保留を含む）
    active_startups = [s for s in startups if s["status"] in ["初期接触", "商談中", "保留"]]
    success_count = len([s for s in startups if s["status"] == "成約"])
    
    with col1:
        st.metric("総スタートアップ数", len(startups))
    with col2:
        st.metric("アクティブ案件", len(active_startups))
    with col3:
        st.metric("成約数", success_count)
    with col4:
        success_rate = f"{(success_count/len(startups)*100):.1f}%" if startups else "0%"
        st.metric("成約率", success_rate)

    # タブの作成
    tab1, tab2, tab3 = st.tabs(["📋 全スタートアップ", "🔥 アクティブ案件", "📈 完了案件"])
    
    # タブ1: 全スタートアップ
    with tab1:
        st.subheader("💼 全スタートアップ一覧")
        
        # フィルター
        col1, col2 = st.columns([1, 1])
        with col1:
            status_filter = st.selectbox("ステータスでフィルター", 
                                       ["全て"] + list(set([s["status"] for s in startups])),
                                       key="all_status_filter")
        with col2:
            search_term = st.text_input("会社名で検索", key="all_search")

        # フィルタリング
        filtered_startups = startups
        if status_filter != "全て":
            filtered_startups = [s for s in filtered_startups if s["status"] == status_filter]
        if search_term:
            filtered_startups = [s for s in filtered_startups if search_term.lower() in s["company_name"].lower()]

        display_startup_cards(filtered_startups, startups, "all")
    
    # タブ2: アクティブ案件のみ
    with tab2:
        st.subheader("🔥 アクティブ案件（進行中）")
        
        if active_startups:
            # アクティブ案件の詳細統計
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                initial_count = len([s for s in active_startups if s["status"] == "初期接触"])
                st.metric("初期接触", initial_count)
            with col2:
                negotiation_count = len([s for s in active_startups if s["status"] == "商談中"])
                st.metric("商談中", negotiation_count)
            with col3:
                # 変更点: 提案済み → 保留
                hold_count = len([s for s in active_startups if s["status"] == "保留"])
                st.metric("保留", hold_count)
            with col4:
                avg_days = calculate_avg_days_since_creation(active_startups)
                st.metric("平均経過日数", f"{avg_days}日")
            
            # アクティブ案件用フィルター
            col1, col2 = st.columns([1, 1])
            with col1:
                # 変更点: 提案済み → 保留
                active_status_filter = st.selectbox("アクティブステータス", 
                                                  ["全て", "初期接触", "商談中", "保留"],
                                                  key="active_status_filter")
            with col2:
                active_search_term = st.text_input("会社名で検索", key="active_search")

            # アクティブ案件のフィルタリング
            filtered_active = active_startups
            if active_status_filter != "全て":
                filtered_active = [s for s in filtered_active if s["status"] == active_status_filter]
            if active_search_term:
                filtered_active = [s for s in filtered_active if active_search_term.lower() in s["company_name"].lower()]

            # 優先度順でソート（商談中 > 初期接触 > 保留）
            priority_order = {"商談中": 1, "初期接触": 2, "保留": 3}
            filtered_active.sort(key=lambda x: priority_order.get(x["status"], 4))
            
            st.info(f"📊 アクティブ案件 {len(filtered_active)} 件を表示中（優先度順）")
            
            display_startup_cards(filtered_active, startups, "active")
        else:
            st.info("現在アクティブな案件はありません。")
    
    # タブ3: 完了案件
    with tab3:
        st.subheader("📈 完了案件")
        
        completed_startups = [s for s in startups if s["status"] in ["成約", "見送り"]]
        
        if completed_startups:
            # 完了案件の統計
            col1, col2, col3 = st.columns(3)
            with col1:
                success_count = len([s for s in completed_startups if s["status"] == "成約"])
                st.metric("成約", success_count)
            with col2:
                rejected_count = len([s for s in completed_startups if s["status"] == "見送り"])
                st.metric("見送り", rejected_count)
            with col3:
                completion_rate = f"{(success_count/len(completed_startups)*100):.1f}%" if completed_startups else "0%"
                st.metric("成約率", completion_rate)
            
            # 完了案件用フィルター
            col1, col2 = st.columns([1, 1])
            with col1:
                completed_status_filter = st.selectbox("完了ステータス", 
                                                     ["全て", "成約", "見送り"],
                                                     key="completed_status_filter")
            with col2:
                completed_search_term = st.text_input("会社名で検索", key="completed_search")

            # 完了案件のフィルタリング
            filtered_completed = completed_startups
            if completed_status_filter != "全て":
                filtered_completed = [s for s in filtered_completed if s["status"] == completed_status_filter]
            if completed_search_term:
                filtered_completed = [s for s in filtered_completed if completed_search_term.lower() in s["company_name"].lower()]

            display_startup_cards(filtered_completed, startups, "completed")
        else:
            st.info("完了した案件はありません。")

else:
    st.info("まだスタートアップが登録されていません。サイドバーから追加してください。")

# 関数定義
def display_startup_cards(filtered_startups, all_startups, tab_type):
    """スタートアップカードを表示する関数"""
    if not filtered_startups:
        st.info("条件に一致するスタートアップがありません。")
        return
    
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
                
                # アクティブ案件の場合は経過日数も表示
                title = f"### {status_colors.get(startup['status'], '⚪')} {startup['company_name']}"
                if tab_type == "active":
                    days_passed = calculate_days_since_creation(startup)
                    title += f" ({days_passed}日経過)"
                
                st.markdown(title)
                
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
                
                # 作成日・更新日
                if startup.get('created_at'):
                    created_date = datetime.fromisoformat(startup['created_at'].replace('Z', '+00:00'))
                    st.write(f"**登録日:** {created_date.strftime('%Y-%m-%d')}")
                
                if startup.get('notes'):
                    with st.expander("メモを見る"):
                        st.write(startup['notes'])
                
                # 編集・削除ボタン
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button(f"編集", key=f"edit_{tab_type}_{i}"):
                        st.info("編集機能は開発中です")
                with col_delete:
                    if st.button(f"削除", key=f"delete_{tab_type}_{i}"):
                        if st.session_state.get(f"confirm_delete_{tab_type}_{i}"):
                            all_startups.remove(startup)
                            save_data(all_startups)
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{tab_type}_{i}"] = True
                            st.warning("もう一度クリックして削除を確認してください")
                
                st.divider()

def calculate_days_since_creation(startup):
    """作成日からの経過日数を計算"""
    try:
        if startup.get('created_at'):
            created_date = datetime.fromisoformat(startup['created_at'].replace('Z', '+00:00'))
            return (datetime.now() - created_date).days
    except:
        pass
    return 0

def calculate_avg_days_since_creation(startups_list):
    """平均経過日数を計算"""
    if not startups_list:
        return 0
    
    total_days = sum(calculate_days_since_creation(s) for s in startups_list)
    return round(total_days / len(startups_list), 1)

# フッター
st.markdown("---")
st.markdown("Made with using Streamlit")
