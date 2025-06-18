import requests
import streamlit as st
from urllib.parse import quote
import time

def fetch_company_logo(company_name):
    """
    会社名からロゴURLを取得する
    複数のAPIを試行し、最初に成功したものを返す
    """
    
    # Clearbit Logo API (無料で利用可能)
    try:
        # 会社名からドメインを推測
        clean_name = company_name.lower().replace(' ', '').replace(',', '').replace('.', '').replace('株式会社', '').replace('inc', '').replace('ltd', '')
        domain_guess = f"{clean_name}.com"
        clearbit_url = f"https://logo.clearbit.com/{domain_guess}"
        
        response = requests.head(clearbit_url, timeout=5)  # HEAD request for faster check
        if response.status_code == 200:
            return clearbit_url
    except Exception as e:
        st.write(f"Clearbit API エラー: {str(e)}")
    
    # 一般的なドメインパターンを試行
    domain_patterns = [
        f"{clean_name}.co.jp",
        f"{clean_name}.jp", 
        f"{clean_name}.net",
        f"{clean_name}.org"
    ]
    
    for domain in domain_patterns:
        try:
            clearbit_url = f"https://logo.clearbit.com/{domain}"
            response = requests.head(clearbit_url, timeout=3)
            if response.status_code == 200:
                return clearbit_url
        except:
            continue
    
    # Google Favicon API (バックアップ)
    try:
        favicon_url = f"https://www.google.com/s2/favicons?sz=64&domain={clean_name}.com"
        return favicon_url
    except:
        pass
    
    return None
