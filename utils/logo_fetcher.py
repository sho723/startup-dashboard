import requests
import streamlit as st
from urllib.parse import quote

def fetch_company_logo(company_name):
    """
    会社名からロゴURLを取得する
    複数のAPIを試行し、最初に成功したものを返す
    """
    
    # Clearbit Logo API (無料で利用可能)
    try:
        # 会社名からドメインを推測
        domain_guess = f"{company_name.lower().replace(' ', '').replace(',', '').replace('.', '')}.com"
        clearbit_url = f"https://logo.clearbit.com/{domain_guess}"
        
        response = requests.get(clearbit_url, timeout=5)
        if response.status_code == 200:
            return clearbit_url
    except:
        pass
    
    # Brandfetch API (要API キー - 無料枠あり)
    # brandfetch_api_key = st.secrets.get("BRANDFETCH_API_KEY")
    # if brandfetch_api_key:
    #     try:
    #         url = f"https://api.brandfetch.io/v2/search/{quote(company_name)}"
    #         headers = {"Authorization": f"Bearer {brandfetch_api_key}"}
    #         response = requests.get(url, headers=headers, timeout=5)
    #         if response.status_code == 200:
    #             data = response.json()
    #             if data and len(data) > 0:
    #                 return data[0].get('icon')
    #     except:
    #         pass
    
    # Google Favicon API (バックアップ)
    try:
        domain_guess = f"{company_name.lower().replace(' ', '').replace(',', '').replace('.', '')}.com"
        favicon_url = f"https://www.google.com/s2/favicons?sz=64&domain={domain_guess}"
        return favicon_url
    except:
        pass
    
    return None
