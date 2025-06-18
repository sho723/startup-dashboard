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


