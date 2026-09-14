import streamlit as st
import base64
import os

# =====================================
# إعداد الصفحة
# =====================================
st.set_page_config(
    page_title="Telecom Dashboard",
    page_icon="📱",
    layout="centered"
)

# =====================================
# دالة معالجة الصور (Base64)
# =====================================
def get_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# تحميل الصور
robot_full = get_base64("robot_full.png.jpeg")
robot_head = get_base64("robot_head.png")

# =====================================
# CSS المطور (تعديل المساحات وتكبير الروبوت)
# =====================================
st.markdown(f"""
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body, [data-testid="stAppViewContainer"] {{
background:#f0f7ff;
font-family:'Segoe UI', sans-serif;
}}
section.main > div {{ padding-top:4px; }}
div[data-testid="stVerticalBlock"] {{ gap:0.4rem; }}

#MainMenu, header, footer {{ visibility:hidden; }}

.block-container {{
max-width:430px;
margin:auto;
padding:12px 16px;
background:linear-gradient(180deg,#dff2ff 0%,#c7e7ff 55%,#f4fbff 100%);
border-radius:42px;
box-shadow:0 14px 35px rgba(0,0,0,.15);
}}

.card {{
background:white;
border-radius:20px;
padding:10px 14px;
margin-bottom:8px;
box-shadow:0 6px 15px rgba(0,0,0,.06);
transition: all 0.3s ease;
}}

/* --- تصغير مساحة كرت الرصيد --- */
.balance-card {{
    padding: 6px 14px !important;
    margin-bottom: 4px !important;
}}

/* --- تصغير مساحة كرت التقييم --- */
.rating-card {{
    padding: 4px 14px 6px !important;
    margin-bottom: 4px !important;
}}

.card:hover, .mini:hover, .nav-item:hover, .bot-bg:hover {{
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}}

.title {{
font-size:15px;
font-weight:900;
color:#102646;
margin: 4px 0 4px 4px;
}}

.clickable {{ 
    cursor: pointer; 
    transition: all 0.3s ease; 
}}
.clickable:active {{ transform: scale(0.95); }}

.star-rating {{
    display: flex;
    flex-direction: row-reverse;
    justify-content: center;
    gap: 4px;
}}
.star-rating input {{ display: none; }}
.star-rating label {{
    font-size: 24px; /* تصغير النجوم أكثر */
    color: #ddd;
    cursor: pointer;
    transition: color 0.2s, transform 0.2s;
}}
.star-rating label:hover {{ transform: scale(1.2); }}
.star-rating input:checked ~ label,
.star-rating label:hover,
.star-rating label:hover ~ label {{
    color: #ffcc00;
}}

.welcome-card {{
    background: white;
    border-radius: 20px;
    padding: 8px 12px;
    margin-bottom: 8px;
    box-shadow: 0 6px 15px rgba(0,0,0,.06);
    display: flex;
    align-items: center;
    position: relative;
    height: 100px; /* زيادة الارتفاع قليلاً لاستيعاب الروبوت الأكبر */
    transition: all 0.3s ease;
}}

/* --- تكبير الروبوت وجعله متداخلاً --- */
.robot-img-welcome {{
    width: 95px; 
    height: 95px;
    background: #f8fbff !important;
    border-radius: 14px;
    margin-right: 12px;
    object-fit: contain;
    padding: 4px;
    border: 1px solid #eef5ff;
    transition: transform 0.4s ease;
}}
.robot-img-welcome:hover {{ transform: scale(1.05); }}

.welcome-text-container {{
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

.needle {{
    position: absolute;
    bottom: 0;
    left: 50%;
    width: 2px;
    height: 30px;
    background: #333;
    transform-origin: bottom center;
    z-index: 5;
}}

.grid4 {{ 
    display:grid; 
    grid-template-columns:repeat(4,1fr); 
    gap:6px; 
    margin: 8px 0 6px; 
}}

.mini {{
background:white; border-radius:18px; min-height:90px;
padding:8px 4px; text-align:center; box-shadow:0 6px 15px rgba(0,0,0,.06);
transition: all 0.3s ease;
}}
.mini-text {{ font-size:10px; font-weight:800; line-height:1.1; }}

.nav {{
margin-top:8px; display:grid; grid-template-columns:repeat(5,1fr);
text-align:center; color:#6b6b6b; align-items: end;
}}
.nav-item {{ font-size: 22px; font-weight: 800; transition: all 0.3s ease; }}
.nav-text {{ font-size: 10px; display: block; }}
.bot-bg {{
width:50px; height:50px; background:white; border-radius:12px;
margin: 0 auto 4px; display:flex; align-items:center; justify-content:center;
box-shadow: 0 4px 10px rgba(0,0,0,0.1);
transition: all 0.3s ease;
}}
.active {{ color:#0d69dd; }}
</style>
""", unsafe_allow_html=True)

# =====================================
# 1. قسم الملف الشخصي
# =====================================
st.markdown(f"""
<div class="welcome-card clickable">
    <img src="data:image/png;base64,{robot_full}" class="robot-img-welcome">
    <div class="welcome-text-container">
        <div style="font-size:20px; font-weight:900; color:#102646; line-height:1.1;">Welcome</div>
        <div style="font-size:12px; color:#555; margin-top:2px;">+962 79 123 4567</div>
        <div style="font-size:10px; color:#777;">Valid until: May 25, 2026</div>
        <div style="font-size:11px; color:#102646; font-weight:700; margin-top:3px;">📍 Location: Amman</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================
# 2. معلومات الرصيد (تم تصغير المساحة)
# =====================================
st.markdown(f"""
<div class="title">Your Number Info</div>
<div class="card balance-card clickable">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div style="flex: 2;">
<div style="font-size:10px; font-weight:700; color:#666;">Remaining GB</div>
<div style="font-size:32px; font-weight:900; color:#102646; line-height:0.9;">4.7 <span style="font-size:14px;">GB</span></div>
</div>
<div style="flex: 1; text-align: right;">
<div style="position: relative; width: 60px; height: 30px; margin-left: auto;">
    <div style="width: 50px; height: 25px; border-radius: 50px 50px 0 0; background: linear-gradient(90deg, #0d69dd 60%, #e0e0e0 60%); position: relative; overflow: hidden;">
        <div style="position: absolute; bottom: 0; left: 5px; width: 40px; height: 20px; background: white; border-radius: 40px 40px 0 0;"></div>
        <div class="needle" style="height:20px; transform: rotate(45deg);"></div>
    </div>
</div>
<div style="font-size:10px; font-weight:900; color:#102646;">6 GB</div>
</div>
</div>
<div style="margin-top:4px; height:4px; border-radius:10px; background:#dce8f7; overflow:hidden;">
<div style="width:78%; height:100%; background:linear-gradient(90deg,#083d8c,#1567e0);"></div>
</div>
</div>
""", unsafe_allow_html=True)

# =====================================
# 3. أيقونات الخدمات
# =====================================
st.markdown("""
<div class="grid4">
<div class="mini clickable"><div style="font-size:24px;">📡</div><div class="mini-text">Internet<br>Packages</div></div>
<div class="mini clickable"><div style="font-size:24px;">🌍</div><div class="mini-text">Renewals +<br>Changes</div></div>
<div class="mini clickable"><div style="font-size:24px;">💰</div><div class="mini-text">International<br>Calls</div></div>
<div class="mini clickable"><div style="font-size:24px;">🔔</div><div class="mini-text">Network<br>Notifications</div></div>
</div>
""", unsafe_allow_html=True)

# =====================================
# 4. قسم التقييم (تم تصغير المساحة)
# =====================================
st.markdown("""
<div class="title">Service Ratings</div>
<div class="card rating-card">
<div style="font-weight:900; font-size:12px; color:#102646;">⭐ Service Security Rate</div>
<div style="margin-top:4px; height:10px; border-radius:15px; background:linear-gradient(90deg,#0047ba,#27a4ff,#ff8c00,#df4126);"></div>
<div style="text-align:center; margin-top:4px; font-weight:700; font-size:11px; color:#102646; margin-bottom:2px;">Rate our service</div>
<div class="star-rating">
    <input type="radio" id="5" name="rate"><label for="5">★</label>
    <input type="radio" id="4" name="rate"><label for="4">★</label>
    <input type="radio" id="3" name="rate"><label for="3">★</label>
    <input type="radio" id="2" name="rate"><label for="2">★</label>
    <input type="radio" id="1" name="rate"><label for="1">★</label>
</div>
</div>
""", unsafe_allow_html=True)

# =====================================
# 5. قوة الشبكة
# =====================================
st.markdown("""
<div class="title">Network Strength in your area</div>
<div class="card clickable">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div style="flex: 1.2;">
<div style="font-size:14px; font-weight:900; color:#102646;">📍 Amman</div>
<div style="font-size:12px; font-weight:700; color:#003366; margin-bottom:6px;">Very Strong Signal</div>
<div style="display: flex; gap: 4px;">
<div style="background: #f1f7ff; border-radius: 10px; padding: 6px; text-align: center; flex: 1;">
<div style="font-size: 7px; color: #666;">Packet Loss</div>
<div style="font-size: 16px; font-weight: 900; color: #000;">0</div>
</div>
<div style="background: #f1f7ff; border-radius: 10px; padding: 6px; text-align: center; flex: 1;">
<div style="font-size: 7px; color: #666;">Avg Jitter</div>
<div style="font-size: 16px; font-weight: 900; color: #000;">19</div>
</div>
</div>
</div>
<div style="flex: 1; text-align: center;">
<div style="position: relative; width: 80px; margin: 0 auto;">
    <div style="width: 80px; height: 40px; border-radius: 80px 80px 0 0; background: linear-gradient(90deg, #4caf50 20%, #ffeb3b 50%, #f44336 100%); position: relative; overflow: hidden;">
        <div style="position: absolute; bottom: 0; left: 8px; width: 64px; height: 32px; background: white; border-radius: 64px 64px 0 0;"></div>
        <div class="needle" style="height: 35px; transform: rotate(-60deg);"></div>
    </div>
<div style="font-size: 9px; font-weight: 900; color: #102646; margin-top: 4px;">Excellent</div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# =====================================
# 6. الشريط السفلي
# =====================================
st.markdown(f"""
<div class="nav">
<div class="nav-item clickable">⚙️<span class="nav-text">Settings</span></div>
<div class="nav-item clickable">🎡<span class="nav-text">Spin</span></div>
<div class="nav-item clickable">
<div class="bot-bg"><img src="data:image/png;base64,{robot_head}" style="width:34px;"></div>
<span class="nav-text">Chatbot</span>
</div>
<div class="nav-item active clickable">🏠<span class="nav-text">Home</span></div>
<div class="nav-item clickable">🎁<span class="nav-text">Game</span></div>
</div>
""", unsafe_allow_html=True)
