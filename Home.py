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

# إعداد الصفحة - يجب أن يكون أول أمر في الملف
st.set_page_config(
    page_title="ICT محلل الأسهم الاحترافي | Al7ebi Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- إصلاح الـ Session State: تهيئة القيم قبل استدعائها ---
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

# Ticker Tape
ticker_data = get_ticker_tape_data()
ticker_html = ""
for name, data in ticker_data.items():
    color = "up" if data['change'] >= 0 else "down"
    arrow = "▲" if data['change'] >= 0 else "▼"
    ticker_html += f'<span class="ticker-item {color}">{name}: {data["price"]:.2f} {arrow} {abs(data["change"]):.2f}%</span>'

st.markdown(f"""
<div class="ticker-tape">
    <div style="animation: scroll 30s linear infinite; display: inline-block;">
        {ticker_html}
    </div>
</div>
<style>
@keyframes scroll {{
    0% {{ transform: translateX(100%); }}
    100% {{ transform: translateX(-100%); }}
}}
</style>
""", unsafe_allow_html=True)

# Kill Zone Status Bar
col_kz1, col_kz2, col_kz3, col_kz4 = st.columns([2, 2, 2, 2])
with col_kz1:
    kz_status = "🔥 نشطة" if active_kz else "⏳ غير نشطة"
    kz_color = "#fbbf24" if active_kz else "#64748b"
    st.markdown(f"""
    <div style="background: rgba(30,41,59,0.8); border-radius: 12px; padding: 12px; text-align: center;">
        <p style="color: #64748b; font-size: 0.75rem; margin: 0;">Kill Zones</p>
        <p style="color: {kz_color}; font-weight: 700; font-size: 1rem; margin: 4px 0 0 0;">{kz_status}</p>
    </div>
    """, unsafe_allow_html=True)

with col_kz2:
    hours, remainder = divmod(int(countdown.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    st.markdown(f"""
    <div class="countdown-box">
        <p style="color: #64748b; font-size: 0.7rem; margin: 0;">العد التنازلي لـ {session_name}</p>
        <p class="countdown-value">{hours:02d}:{minutes:02d}:{seconds:02d}</p>
    </div>
    """, unsafe_allow_html=True)

with col_kz3:
    st.markdown(f"""
    <div style="background: rgba(30,41,59,0.8); border-radius: 12px; padding: 12px; text-align: center;">
        <p style="color: #64748b; font-size: 0.75rem; margin: 0;">توقيت نيويورك</p>
        <p style="color: #60a5fa; font-weight: 700; font-size: 1rem; margin: 4px 0 0 0;">{ny_now.strftime('%H:%M:%S')} EST</p>
    </div>
    """, unsafe_allow_html=True)

with col_kz4:
    silver_bullet = "🔥 نشط" if any(z['name'] in ['London Kill Zone', 'New York Kill Zone'] for z in active_kz) else "❌ غير نشط"
    sb_color = "#fbbf24" if "🔥" in silver_bullet else "#64748b"
    st.markdown(f"""
    <div style="background: rgba(30,41,59,0.8); border-radius: 12px; padding: 12px; text-align: center;">
        <p style="color: #64748b; font-size: 0.75rem; margin: 0;">Silver Bullet Window</p>
        <p style="color: {sb_color}; font-weight: 700; font-size: 1rem; margin: 4px 0 0 0;">{silver_bullet}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

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

    # إعدادات الحساب (تم تعديلها لتعمل مع الـ Session State بشكل آمن)
    st.markdown("### 💰 إعدادات الحساب")
    st.number_input("رصيد الحساب ($)", min_value=100.0, step=100.0, key='account_balance')
    st.slider("نسبة المخاطرة (%)", 0.5, 5.0, step=0.5, key='risk_percent')

    st.markdown("---")
    # (بقية كود القوائم والإحصائيات...)
