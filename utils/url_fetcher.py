import requests
import streamlit as st
from urllib.parse import quote, unquote
import time
from bs4 import BeautifulSoup
import re
import json

def fetch_company_url(company_name):
    """
    会社名から公式HPのURLを取得する
    複数の検索手法を試行し、最初に成功したものを返す
    """
    
    if not company_name or company_name.strip() == "":
        return None
    
    # より柔軟な会社名のクリーニング
    original_name = company_name.strip()
    clean_patterns = [
        # 元の名前そのまま
        original_name,
        # 基本的なクリーニング
        re.sub(r'[^\w\s]', '', original_name.lower()),
        # 株式会社、Inc、Ltd等を削除
        re.sub(r'(株式会社|有限会社|合同会社|inc|ltd|llc|corp|corporation)', '', original_name.lower(), flags=re.IGNORECASE).strip(),
        # スペース、ピリオド、カンマを削除
        re.sub(r'[\s\.,\-_]', '', original_name.lower()),
    ]
    
    # 1. 拡張されたドメイン推測（複数のクリーニングパターンを使用）
    for clean_name in clean_patterns:
        if not clean_name:
            continue
            
        # より多くのドメインパターンを試行
        domain_patterns = [
            f"{clean_name}.com",
            f"{clean_name}.co.jp", 
            f"{clean_name}.jp",
            f"{clean_name}.net",
            f"{clean_name}.org",
            f"{clean_name}.info",
            f"{clean_name}.biz",
            f"{clean_name}-corp.com",
            f"{clean_name}corp.com",
            f"www.{clean_name}.com",
        ]
        
        for domain in domain_patterns:
            for protocol in ['https://', 'http://']:
                try:
                    url = f"{protocol}{domain}"
                    response = requests.head(url, timeout=3, allow_redirects=True)
                    if response.status_code == 200:
                        return response.url
                except:
                    continue
    
    # 2. より効果的なGoogle検索（複数のクエリパターン）
    search_patterns = [
        f'"{original_name}" site:*.com OR site:*.co.jp OR site:*.jp',
        f'{original_name} 公式サイト',
        f'{original_name} official website',
        f'{original_name} homepage',
        f'{original_name} 会社概要',
    ]
    
    for search_query in search_patterns:
        try:
            encoded_query = quote(search_query)
            search_url = f"https://www.google.com/search?q={encoded_query}&num=10"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(search_url, headers=headers, timeout=8)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # より多くのGoogle検索結果パターンを検索
                link_selectors = [
                    'a[href*="/url?q="]',
                    'a[href^="http"]',
                    '.yuRUbf a',
                    '.kCrYT a',
                ]
                
                found_urls = set()
                for selector in link_selectors:
                    for link in soup.select(selector):
                        href = link.get('href', '')
                        if '/url?q=' in href:
                            try:
                                actual_url = unquote(href.split('/url?q=')[1].split('&')[0])
                                found_urls.add(actual_url)
                            except:
                                continue
                        elif href.startswith('http'):
                            found_urls.add(href)
                
                # URLの品質でソート
                for url in sorted(found_urls, key=lambda x: score_url_quality(x, original_name), reverse=True):
                    if is_valid_company_url(url, original_name):
                        if validate_url_quick(url):
                            return url
                            
        except Exception as e:
            continue
    
    # 3. Yahoo!検索（日本企業に特に有効）
    try:
        search_query = f"{original_name} 公式サイト"
        encoded_query = quote(search_query)
        yahoo_url = f"https://search.yahoo.co.jp/search?p={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(yahoo_url, headers=headers, timeout=6)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('http') and is_valid_company_url(href, original_name):
                    if validate_url_quick(href):
                        return href
                        
    except Exception as e:
        pass
    
    # 4. 会社名から推測される代替ドメインパターン
    try:
        # 会社名の一部を使った推測
        name_parts = re.findall(r'\w+', original_name.lower())
        if len(name_parts) >= 2:
            combined_patterns = [
                f"{''.join(name_parts[:2])}.com",
                f"{''.join(name_parts[:2])}.co.jp",
                f"{name_parts[0]}{name_parts[-1]}.com",
                f"{name_parts[0]}.co.jp",
            ]
            
            for domain in combined_patterns:
                for protocol in ['https://', 'http://']:
                    try:
                        url = f"{protocol}www.{domain}"
                        if validate_url_quick(url):
                            return url
                    except:
                        continue
                        
    except Exception as e:
        pass
    
    # 5. 最後の手段：より寛容なドメイン推測
    try:
        base_name = re.sub(r'[^\w]', '', original_name.lower())
        if len(base_name) >= 3:
            fallback_patterns = [
                f"{base_name[:10]}.com",  # 名前の最初の10文字
                f"{base_name[:5]}.co.jp",  # 名前の最初の5文字
                f"{base_name}.net",
                f"{base_name}.org",
            ]
            
            for domain in fallback_patterns:
                for protocol in ['https://', 'http://']:
                    try:
                        url = f"{protocol}{domain}"
                        response = requests.head(url, timeout=2, allow_redirects=True)
                        if response.status_code in [200, 301, 302]:
                            return response.url
                    except:
                        continue
    except:
        pass
    
    return None

def score_url_quality(url, company_name):
    """
    URLの品質をスコアリング（会社名との関連性）
    """
    score = 0
    url_lower = url.lower()
    company_lower = company_name.lower()
    
    # 会社名がURLに含まれている
    clean_company = re.sub(r'[^\w]', '', company_lower)
    if clean_company in url_lower:
        score += 10
    
    # .co.jp ドメインは日本企業の可能性が高い
    if '.co.jp' in url_lower:
        score += 5
    elif '.jp' in url_lower:
        score += 3
    elif '.com' in url_lower:
        score += 1
    
    # 公式サイトっぽいパス
    if any(path in url_lower for path in ['about', 'company', 'corporate']):
        score += 2
    
    # 除外すべきサイト
    if any(exclude in url_lower for exclude in ['wikipedia', 'facebook', 'twitter', 'linkedin', 'youtube']):
        score -= 10
    
    return score

def is_valid_company_url(url, company_name):
    """
    URLが会社の公式サイトらしいかを判定
    """
    url_lower = url.lower()
    
    # 除外すべきドメイン
    excluded_domains = [
        'google', 'yahoo', 'bing', 'wikipedia', 'facebook', 'twitter', 
        'linkedin', 'youtube', 'instagram', 'amazon', 'rakuten',
        'indeed', 'recruit', 'mynavi', 'doda'
    ]
    
    if any(domain in url_lower for domain in excluded_domains):
        return False
    
    # 有効なドメイン拡張子
    valid_extensions = ['.com', '.co.jp', '.jp', '.net', '.org', '.info', '.biz']
    if not any(ext in url_lower for ext in valid_extensions):
        return False
    
    return True

def validate_url_quick(url):
    """
    URLの有効性を素早くチェック
    """
    try:
        response = requests.head(url, timeout=3, allow_redirects=True)
        return response.status_code in [200, 301, 302]
    except:
        return False

def validate_url(url):
    """
    URLが有効かどうかを確認する（詳細版）
    """
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        try:
            # HEAD requestが失敗した場合はGET requestを試行
            response = requests.get(url, timeout=5, stream=True)
            return response.status_code == 200
        except:
            return False
