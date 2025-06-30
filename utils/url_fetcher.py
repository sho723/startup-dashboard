import requests
import streamlit as st
from urllib.parse import quote
import time
from bs4 import BeautifulSoup
import re

def fetch_company_url(company_name):
    """
    会社名から公式HPのURLを取得する
    複数の検索手法を試行し、最初に成功したものを返す
    """
    
    # 会社名のクリーニング
    clean_name = company_name.lower().replace(' ', '').replace(',', '').replace('.', '').replace('株式会社', '').replace('inc', '').replace('ltd', '')
    
    # 1. 直接的なドメイン推測
    try:
        domain_patterns = [
            f"{clean_name}.com",
            f"{clean_name}.co.jp",
            f"{clean_name}.jp", 
            f"{clean_name}.net",
            f"{clean_name}.org"
        ]
        
        for domain in domain_patterns:
            try:
                url = f"https://www.{domain}"
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    return response.url  # リダイレクト先のURLを返す
            except:
                continue
                
    except Exception as e:
        st.write(f"直接ドメイン検索エラー: {str(e)}")
    
    # 2. Google検索を使用してHPを検索
    try:
        search_query = f"{company_name} 公式サイト site:*.com OR site:*.co.jp OR site:*.jp"
        encoded_query = quote(search_query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 検索結果からURLを抽出
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/url?q=' in href:
                    # Google検索結果のURLから実際のURLを抽出
                    actual_url = href.split('/url?q=')[1].split('&')[0]
                    # 会社の公式サイトっぽいURLをフィルタリング
                    if any(pattern in actual_url.lower() for pattern in ['.com', '.co.jp', '.jp']) and \
                       not any(exclude in actual_url.lower() for exclude in ['google', 'youtube', 'facebook', 'twitter', 'linkedin']):
                        return actual_url
                        
    except Exception as e:
        st.write(f"Google検索エラー: {str(e)}")
    
    # 3. Bing検索をバックアップとして使用（DuckDuckGoの代替）
    try:
        search_query = f"{company_name} official website"
        encoded_query = quote(search_query)
        bing_url = f"https://www.bing.com/search?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # タイムアウトを短縮し、接続エラーに対してより寛容に
        response = requests.get(bing_url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Bing検索結果からURLを抽出
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('http') and \
                   any(pattern in href.lower() for pattern in ['.com', '.co.jp', '.jp']) and \
                   not any(exclude in href.lower() for exclude in ['bing', 'microsoft', 'google', 'wikipedia', 'facebook', 'twitter', 'linkedin']):
                    return href
                    
    except requests.exceptions.ConnectTimeout:
        st.write("Bing検索: 接続タイムアウトが発生しました")
    except requests.exceptions.ConnectionError:
        st.write("Bing検索: 接続エラーが発生しました")
    except Exception as e:
        st.write(f"Bing検索エラー: {str(e)}")
    
    # 4. Yahoo検索を追加のバックアップとして使用
    try:
        search_query = f"{company_name} 公式サイト"
        encoded_query = quote(search_query)
        yahoo_url = f"https://search.yahoo.co.jp/search?p={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(yahoo_url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Yahoo検索結果からURLを抽出
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('http') and \
                   any(pattern in href.lower() for pattern in ['.com', '.co.jp', '.jp']) and \
                   not any(exclude in href.lower() for exclude in ['yahoo', 'google', 'wikipedia']):
                    return href
                    
    except requests.exceptions.Timeout:
        st.write("Yahoo検索: タイムアウトが発生しました")
    except Exception as e:
        st.write(f"Yahoo検索エラー: {str(e)}")
    
    # 5. 最後の手段：一般的なドメインパターンの推測（httpなしで試行）
    try:
        for domain in domain_patterns:
            try:
                url = f"http://{domain}"
                response = requests.head(url, timeout=3, allow_redirects=True)
                if response.status_code == 200:
                    return response.url
            except:
                continue
    except:
        pass
    
    return None

def validate_url(url):
    """
    URLが有効かどうかを確認する
    """
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def fetch_company_url_safe(company_name):
    """
    エラーハンドリングを強化したバージョン
    """
    try:
        return fetch_company_url(company_name)
    except Exception as e:
        st.write(f"全体的なエラー: {str(e)}")
        return None
