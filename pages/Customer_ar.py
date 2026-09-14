import streamlit as st
import base64
import os

# =====================================
# إعداد الصفحة
# =====================================
st.set_page_config(
    page_title="لوحة تحكم الاتصالات",
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


# تحميل الصور الأساسية
robot_full = get_base64("robot_full.png.jpeg")
robot_head = get_base64("robot_head.png")

# تحميل صور الأيقونات
icon_internet = get_base64("internet.png")
icon_renewals = get_base64("renewals.png")
icon_calls = get_base64("calls.png")
icon_notifications = get_base64("notifications.png")

# تحميل صور الشريط السفلي
icon_sitting = get_base64("sitting.png")
icon_spin = get_base64("spin.png")
icon_home = get_base64("home.png")
icon_game = get_base64("game.png")

# تعريف المتغير page
page = "2_Customer_AR"


# =====================================
# CSS المطور (دعم RTL)
# =====================================
st.markdown(f"""
<style>

* {{
    margin:0;
    padding:0;
    box-sizing:border-box;
    direction:rtl;
}}

html, body, [data-testid="stAppViewContainer"] {{
    background:#f0f7ff;
    font-family:'Segoe UI', sans-serif;
}}

section.main > div {{
    padding-top:4px;
}}

div[data-testid="stVerticalBlock"] {{
    gap:0.4rem;
}}

#MainMenu, header, footer {{
    visibility:hidden;
}}

.block-container {{
    max-width:430px;
    min-height:820px;
    margin:auto;
    padding:12px 16px;
    background:linear-gradient(
        180deg,
        #FFFFFF 0%,
        #E3F2FD 30%,
        #BBDEFB 100%
    );
    border-radius:42px;
    box-shadow:0 14px 35px rgba(0,0,0,.15);
}}

.card {{
    background:white;
    border-radius:20px;
    padding:10px 14px;
    margin-bottom:8px;
    box-shadow:0 4px 15px rgba(0,0,0,.05);
    transition:all 0.3s ease;
}}

.balance-card {{
    padding:6px 14px !important;
    margin-bottom:20px !important;
}}

.rating-card {{
    padding:4px 14px 6px !important;
    margin-bottom:4px !important;
}}

.title {{
    font-size:15px;
    font-weight:900;
    color:#102646;
    margin:4px 4px 4px 0;
    text-align:right;
}}

.clickable {{
    cursor:pointer;
    transition:all 0.3s ease;
    position:relative;
}}

.clickable:active {{
    transform:scale(0.95);
}}

.service-item {{
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    text-align:center;
    background:transparent;
    padding:8px 4px;
    height:100px;
    transition:transform 0.3s ease;
    position:relative;
}}

.service-item:hover {{
    transform:translateY(-10px);
}}

.service-icon-img {{
    width:65px;
    height:65px;
    object-fit:contain;
    margin-bottom:2px;
}}

.service-label {{
    font-size:10px;
    font-weight:800;
    color:#102646;
    line-height:1.1;
}}

.nav {{
    margin-top:15px;
    display:grid;
    grid-template-columns:repeat(5,1fr);
    text-align:center;
    align-items:end;
}}

.nav-item {{
    display:flex;
    flex-direction:column;
    align-items:center;
    color:#6b6b6b;
    font-size:11px;
    font-weight:700;
    transition:transform 0.3s ease;
    position:relative;
}}

.nav-item:hover {{
    transform:scale(1.15);
}}

.nav-img-footer {{
    width:38px;
    height:38px;
    object-fit:contain;
    margin-bottom:2px;
}}

.bot-bg {{
    width:60px;
    height:60px;
    background:white;
    border-radius:15px;
    margin:0 auto 2px;
    display:flex;
    align-items:center;
    justify-content:center;
    box-shadow:0 4px 10px rgba(0,0,0,0.1);
}}

div.stButton {{
    position:relative;
    width:100%;
    height:100px;
    margin-top:-100px;
    z-index:999;
}}

div.stButton > button {{
    width:100%;
    height:100%;
    opacity:0;
    cursor:pointer;
    border:none;
    background:transparent;
}}

.nav-button div.stButton {{
    height:70px !important;
    margin-top:-70px !important;
}}

.star-rating {{
    display:flex;
    flex-direction:row-reverse;
    justify-content:center;
    gap:4px;
}}

.star-rating input {{
    display:none;
}}

.star-rating label {{
    font-size:24px;
    color:#ddd;
    cursor:pointer;
}}

.star-rating input:checked ~ label {{
    color:#ffcc00;
}}

.rating-bar-container {{
    display:flex;
    align-items:center;
    justify-content:space-between;
    background:linear-gradient(
        90deg,
        #1A4FA0,
        #46A1E2,
        #D47E2E,
        #C63F2A
    );
    height:22px;
    border-radius:4px;
    margin-top:6px;
    padding:0 10px;
    color:white;
    font-size:11px;
    font-weight:bold;
    direction:ltr;
}}

.welcome-card {{
    background:white;
    border-radius:20px;
    padding:8px 12px;
    margin-bottom:8px;
    display:flex;
    align-items:center;
    height:100px;
    text-align:right;
}}

.robot-img-welcome {{
    width:95px;
    height:95px;
    object-fit:contain;
    margin-left:12px;
}}

.needle {{
    position:absolute;
    bottom:0;
    left:50%;
    width:2px;
    height:30px;
    background:#333;
    transform-origin:bottom center;
    z-index:5;
}}

</style>
""", unsafe_allow_html=True)


# =====================================
# 1. قسم الملف الشخصي
# =====================================
st.markdown(f"""
<div class="welcome-card clickable">

    <img
        src="data:image/png;base64,{robot_full}"
        class="robot-img-welcome"
    >

    <div class="welcome-text-container">

        <div style="
            font-size:18px;
            font-weight:900;
            color:#102646;
            line-height:1.1;
        ">
            أهلاً بك: اسم المستخدم
        </div>

        <div style="
            font-size:12px;
            color:#555;
            margin-top:2px;
            direction:ltr;
        ">
            +962 79 123 4567
        </div>

        <div style="
            font-size:10px;
            color:#777;
        ">
            صالح لغاية: 25 مايو، 2024
        </div>

        <div style="
            font-size:11px;
            background:#F0F7FF;
            border-radius:20px;
            padding:2px 10px;
            color:#102646;
            font-weight:700;
            margin-top:5px;
            border:1px solid #D0E0F0;
            display:inline-block;
        ">
            📍 الموقع: عمان
        </div>

    </div>

</div>
""", unsafe_allow_html=True)


# =====================================
# 2. معلومات الرصيد
# =====================================
st.markdown(f"""
<div class="title">
    معلومات رقمك
</div>

<div class="card balance-card clickable">

    <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;
        direction:ltr;
    ">

        <div style="
            flex:2;
            text-align:left;
        ">

            <div style="
                font-size:10px;
                font-weight:700;
                color:#666;
            ">
                الإنترنت المتبقي
            </div>

            <div style="
                font-size:32px;
                font-weight:900;
                color:#102646;
                line-height:0.9;
            ">
                4.7
                <span style="font-size:14px;">
                    جيجابايت
                </span>
            </div>

        </div>

        <div style="
            flex:1;
            text-align:right;
        ">

            <div style="
                position:relative;
                width:60px;
                height:30px;
                margin-left:auto;
            ">

                <div style="
                    width:50px;
                    height:25px;
                    border-radius:50px 50px 0 0;
                    background:linear-gradient(
                        90deg,
                        #1A4FA0 60%,
                        #E0E0E0 60%
                    );
                    position:relative;
                    overflow:hidden;
                ">

                    <div style="
                        position:absolute;
                        bottom:0;
                        left:5px;
                        width:40px;
                        height:20px;
                        background:white;
                        border-radius:40px 40px 0 0;
                    ">
                    </div>

                    <div
                        class="needle"
                        style="
                            height:20px;
                            transform:rotate(45deg);
                        ">
                    </div>

                </div>

            </div>

            <div style="
                font-size:10px;
                font-weight:900;
                color:#102646;
            ">
                6 جيجابايت
            </div>

        </div>

    </div>

    <div style="
        margin-top:4px;
        height:6px;
        border-radius:10px;
        background:#E0E0E0;
        overflow:hidden;
    ">

        <div style="
            width:78%;
            height:100%;
            background:#1A4FA0;
        ">
        </div>

    </div>

</div>
""", unsafe_allow_html=True)


# =====================================
# 3. أيقونات الخدمات
# =====================================
cols = st.columns(4)


with cols[0]:

    st.markdown(
        f"""
        <div class="service-item clickable">

            <img
                src="data:image/png;base64,{icon_internet}"
                class="service-icon-img"
            >

            <div class="service-label">
                حزم<br>الإنترنت
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "internet",
        key="s1"
    ):
        st.switch_page(
            "pages/InternetPackages_ar.py"
        )


with cols[1]:

    st.markdown(
        f"""
        <div class="service-item clickable">

            <img
                src="data:image/png;base64,{icon_renewals}"
                class="service-icon-img"
            >

            <div class="service-label">
                التجديد وتغيير<br>التعرفة
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "renewals",
        key="s2"
    ):
        st.switch_page(
            "pages/RenewalsTariff_ar.py"
        )


with cols[2]:

    st.markdown(
        f"""
        <div class="service-item clickable">

            <img
                src="data:image/png;base64,{icon_calls}"
                class="service-icon-img"
            >

            <div class="service-label">
                المكالمات<br>الدولية
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "calls",
        key="s3"
    ):
        st.switch_page(
            "pages/InternationalCalls_ar.py"
        )


with cols[3]:

    st.markdown(
        f"""
        <div class="service-item clickable">

            <img
                src="data:image/png;base64,{icon_notifications}"
                class="service-icon-img"
            >

            <div class="service-label">
                تنبيهات<br>الشبكة
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "notifications",
        key="s4"
    ):
        st.switch_page(
            "pages/NetworkNotifications_ar.py"
        )


# =====================================
# 4. قسم التقييم
# =====================================
st.markdown("""
<div class="title">
    تقييم الخدمات
</div>

<div class="card rating-card">

    <div style="
        font-weight:900;
        font-size:12px;
        color:#102646;
    ">
        ⭐ معدل أمان الخدمة
    </div>

    <div class="rating-bar-container">

        <span>★ 4.5</span>
        <span>4.5%</span>

        <span style="
            background:rgba(255,255,255,0.3);
            padding:0 5px;
            border-radius:2px;
        ">
            24%
        </span>

    </div>

    <div style="
        text-align:center;
        margin-top:8px;
        font-weight:700;
        font-size:11px;
        color:#666;
        margin-bottom:2px;
    ">
        قيم خدمتنا
    </div>

    <div class="star-rating">

        <input
            type="radio"
            id="5"
            name="rate"
        >
        <label for="5">★</label>

        <input
            type="radio"
            id="4"
            name="rate"
        >
        <label for="4">★</label>

        <input
            type="radio"
            id="3"
            name="rate"
        >
        <label for="3">★</label>

        <input
            type="radio"
            id="2"
            name="rate"
        >
        <label for="2">★</label>

        <input
            type="radio"
            id="1"
            name="rate"
        >
        <label for="1">★</label>

    </div>

</div>
""", unsafe_allow_html=True)


# =====================================
# 5. قوة الشبكة
# =====================================
st.markdown("""
<div class="title">
    قوة الشبكة في منطقتك
</div>

<div class="card clickable">

    <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;
    ">

        <div style="
            flex:1.2;
            text-align:right;
        ">

            <div style="
                font-size:14px;
                font-weight:900;
                color:#102646;
            ">
                📍 عمان
            </div>

            <div style="
                font-size:12px;
                font-weight:700;
                color:#1A4FA0;
                margin-bottom:6px;
            ">
                إشارة قوية جداً
            </div>

            <div style="
                display:flex;
                gap:4px;
                direction:ltr;
            ">

                <div style="
                    background:#F1F7FF;
                    border-radius:10px;
                    padding:6px;
                    text-align:center;
                    flex:1;
                    border:1px solid #E0E0E0;
                ">

                    <div style="
                        font-size:7px;
                        color:#666;
                        font-weight:bold;
                    ">
                        Loss (%)
                    </div>

                    <div style="
                        font-size:16px;
                        font-weight:900;
                        color:#000;
                    ">
                        0
                    </div>

                </div>

                <div style="
                    background:#F1F7FF;
                    border-radius:10px;
                    padding:6px;
                    text-align:center;
                    flex:1;
                    border:1px solid #E0E0E0;
                ">

                    <div style="
                        font-size:7px;
                        color:#666;
                        font-weight:bold;
                    ">
                        Jitter (ms)
                    </div>

                    <div style="
                        font-size:16px;
                        font-weight:900;
                        color:#000;
                    ">
                        19
                    </div>

                </div>

            </div>

        </div>

        <div style="
            flex:1;
            text-align:center;
        ">

            <div style="
                position:relative;
                width:80px;
                margin:0 auto;
            ">

                <div style="
                    width:80px;
                    height:40px;
                    border-radius:80px 80px 0 0;
                    background:linear-gradient(
                        90deg,
                        #4caf50 20%,
                        #ffeb3b 50%,
                        #f44336 100%
                    );
                    position:relative;
                    overflow:hidden;
                ">

                    <div style="
                        position:absolute;
                        bottom:0;
                        left:8px;
                        width:64px;
                        height:32px;
                        background:white;
                        border-radius:64px 64px 0 0;
                    ">
                    </div>

                    <div
                        class="needle"
                        style="
                            height:35px;
                            transform:rotate(-60deg);
                        ">
                    </div>

                </div>

                <div style="
                    font-size:9px;
                    font-weight:900;
                    color:#102646;
                    margin-top:4px;
                ">
                    -68dBm (ممتاز)
                </div>

            </div>

        </div>

    </div>

</div>
""", unsafe_allow_html=True)


# =====================================
# 6. الشريط السفلي
# =====================================
n_cols = st.columns(5)


# الإعدادات
with n_cols[0]:

    st.markdown(
        f"""
        <div class="nav-item clickable">

            <img
                src="data:image/png;base64,{icon_sitting}"
                class="nav-img-footer"
            >

            <span>الإعدادات</span>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "settings",
        key="nav_set"
    ):
        st.switch_page(
            "pages/settingar.py"
        )


# العب واربح
with n_cols[1]:

    st.markdown(
        f"""
        <div class="nav-item clickable">

            <img
                src="data:image/png;base64,{icon_spin}"
                class="nav-img-footer"
            >

            <span>العب واربح</span>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "spin",
        key="nav_spin"
    ):
        st.switch_page(
            "pages/15_Game.py"
        )


# المساعد
with n_cols[2]:

    st.markdown(
        f"""
        <div class="nav-item clickable">

            <div class="bot-bg">

                <img
                    src="data:image/png;base64,{robot_head}"
                    style="
                        width:40px;
                        height:40px;
                        object-fit:contain;
                    "
                >

            </div>

            <span>المساعد</span>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "chatbot",
        key="nav_bot"
    ):
        st.switch_page(
            "pages/Chatbot.py"
        )


# الرئيسية
with n_cols[3]:

    st.markdown(
        f"""
        <div class="nav-item clickable">

            <img
                src="data:image/png;base64,{icon_home}"
                class="nav-img-footer"
            >

            <span>الرئيسية</span>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "home",
        key="nav_home"
    ):
        st.switch_page(
            "pages/Customer_ar.py"
        )


# الألعاب
with n_cols[4]:

    st.markdown(
        f"""
        <div class="nav-item clickable">

            <img
                src="data:image/png;base64,{icon_game}"
                class="nav-img-footer"
            >

            <span>الألعاب</span>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "game",
        key="nav_game"
    ):
        st.switch_page(
            "pages/15_Game.py"
        )
