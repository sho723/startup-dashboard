import json
import os
from typing import List, Dict

DATA_FILE = "data/startups.json"

def load_data() -> List[Dict]:
    """スタートアップデータを読み込む"""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(startups: List[Dict]):
    """スタートアップデータを保存する"""
    if not os.path.exists("data"):
        os.makedirs("data")
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(startups, f, ensure_ascii=False, indent=2)

def add_startup(startups: List[Dict], startup_data: Dict):
    """新しいスタートアップを追加する"""
    startups.append(startup_data)
