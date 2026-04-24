import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from utils import (
    apply_custom_css, render_header, render_section_header, render_metric_card, render_ict_zone,
    STOCKS_DATA, TIMEFRAMES, get_stock_data, calculate_technical_indicators,
    detect_market_structure, detect_fvg, detect_order_blocks, detect_liquidity_levels,
    detect_unicorn_model, calculate_ote_zone, 
    get_kill_zone_status, get_session_countdown, get_ny_time,
    calculate_premium_discount, get_premium_discount_signal,
    get_smt_divergence, calculate_position_size, calculate_risk_reward,
    calculate_ict_rating, ict_smart_scanner,
    get_ticker_tape_data, get_rating_from_storage, save_rating,
    get_target_from_storage, save_target, format_number, get_all_stocks_flat, RATING_LABELS
)

st.set_page_config(
    page_title="ICT محلل الأسهم الاحترافي | Al7ebi Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. إصلاح الـ Session State (يجب أن يكون قبل أي استدعاء آخر) ---
if 'account_balance' not in st.session_state:
    st.session_state['account_balance'] = 10000.0
if 'risk_percent' not in st.session_state:
    st.session_state['risk_percent'] = 1.0
if 'ratings' not in st.session_state:
    st.session_state['ratings'] = {}
if 'targets' not in st.session_state:
    st.session_state['targets'] = {}
if 'selected_timeframe' not in st.session_state:
    st.session_state['selected_timeframe'] = 'D1'
if 'hide_non_kz' not in st.session_state:
    st.session_state['hide_non_kz'] = False

apply_custom_css()

# ============ TOP BAR: TICKER TAPE + KILL ZONE COUNTDOWN ============
active_kz, next_kz, ny_now = get_kill_zone_status()
session_name, countdown = get_session_countdown()

# (بقية كود الـ Ticker Tape و Kill Zone تبقى كما هي...)
# ... [كود الـ Ticker Tape هنا] ...

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <div style="font-size: 3rem; margin-bottom: 10px;">📈</div>
        <h2 style="color: #f8fafc; margin: 0; font-weight: 800;">Al7ebi Pro</h2>
        <p style="color: #64748b; font-size: 0.85rem; margin-top: 4px;">ICT محلل الأسهم الاحترافي</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧭 التنقل")
    page = st.radio("", [
        "🏠 الرئيسية - ICT Analysis",
        "🔍 Smart Scanner",
        "📊 السوق",
        "⭐ قائمة المتابعة",
        "⚙️ الإعدادات"
    ], label_visibility="collapsed")

    st.markdown("---")

    # --- 2. تعديل طريقة كتابة المدخلات لتجنب الـ Exception ---
    st.markdown("### 💰 إعدادات الحساب")
    # نستخدم key مباشرة لربط القيمة بالـ session_state تلقائياً وبشكل آمن
    st.number_input("رصيد الحساب ($)", min_value=100.0, step=100.0, key='account_balance')
    st.slider("نسبة المخاطرة (%)", 0.5, 5.0, step=0.5, key='risk_percent')

    st.markdown("---")
    # (بقية كود الـ Sidebar تبقى كما هي...)
