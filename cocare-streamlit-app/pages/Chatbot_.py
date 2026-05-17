import streamlit as st
import base64
import os
import sys
import html as html_lib
import time



# =========================
# IMPORT PATH
# =========================
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)



from cocare import process_message





# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="CoCare AI", layout="centered")





# =========================
# CONSTANTS
# =========================
PHONE_WIDTH = 430
PHONE_HEIGHT = 820



CHAT_KEY = "chat_messages_unified"
CONTEXT_KEY = "chat_context_unified"



if "language" not in st.session_state:
    st.session_state["language"] = "ar"



if "region" not in st.session_state:
    st.session_state["region"] = "Amman"





WELCOME = {
    "ar": "مرحباً 👋 أنا مساعد CoCare الذكي، كيف أقدر أساعدك؟",
    "en": "Hello 👋 I’m CoCare AI Assistant. How can I help you?"
}



TEXTS = {
    "ar": {
        "ready": "جاهز للمساعدة",
        "quick": "الخدمات السريعة",
        "clear": "مسح المحادثة",
        "placeholder": "اكتب رسالتك هنا...",
        "send": "➜",
        "typing": "جاري الكتابة...",
        "user": "أنت",
        "buttons": [
            ("فحص الشبكة", "فحص الشبكة"),
            ("استهلاك الإنترنت", "استهلاك الإنترنت"),
            ("تجديد الباقة", "تجديد الباقة"),
            ("المكالمات الدولية", "المكالمات الدولية"),
            ("العروض والألعاب", "العروض والألعاب"),
            ("التواصل مع الدعم", "التواصل مع الدعم"),
        ],
        "fallback": "يقوم مساعد CoCare بمعالجة طلبك."
    },
    "en": {
        "ready": "Ready to Assist",
        "quick": "Quick Services",
        "clear": "Clear Chat",
        "placeholder": "Type your message here...",
        "send": "➜",
        "typing": "Typing...",
        "user": "You",
        "buttons": [
            ("Check Network", "Check Network"),
            ("Internet Usage", "Internet Usage"),
            ("Renew Package", "Renew Package"),
            ("International Calls", "International Calls"),
            ("Offers & Games", "Offers & Games"),
            ("Contact Support", "Contact Support"),
        ],
        "fallback": "CoCare Assistant is processing your request."
    }
}





# =========================
# SESSION
# =========================
if CHAT_KEY not in st.session_state:
    lang = st.session_state["language"]
    st.session_state[CHAT_KEY] = [
        ("bot", WELCOME[lang])
    ]



if CONTEXT_KEY not in st.session_state:
    st.session_state[CONTEXT_KEY] = {
        "last_intent": None,
        "awaiting_details": False,
        "last_network_problem": False
    }





# =========================
# HELPERS
# =========================
def reset_context():
    st.session_state[CONTEXT_KEY] = {
        "last_intent": None,
        "awaiting_details": False,
        "last_network_problem": False
    }





def img_to_base64(path):
    paths = [
        os.path.join(os.path.dirname(__file__), path),
        os.path.join(os.path.dirname(__file__), "..", path),
        path
    ]



    for full_path in paths:
        try:
            if os.path.exists(full_path):
                with open(full_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
        except Exception:
            pass



    return ""





def get_bot_response(message):
    lang = st.session_state["language"]
    text = str(message).strip()



    try:
        # يحافظ على المودلات والـ pipeline
        try:
            result = process_message(
                text,
                user_id="customer_1",
                region=st.session_state["region"],
                language=lang
            )
        except TypeError:
            # لو process_message عندك لا يستقبل language
            result = process_message(
                text,
                user_id="customer_1",
                region=st.session_state["region"]
            )



        if isinstance(result, dict):
            response = str(result.get("response", "")).strip()



            # حفظ آخر تحليل للاستفادة منه بالفلاتر أو الداشبورد
            st.session_state["last_analysis"] = result



            if response:
                return response



    except Exception as e:
        st.session_state["last_model_error"] = str(e)



    # fallback فقط لو صار خطأ بالمودلات
    lower = text.lower()



    if lang == "ar":
        if "شبكة" in lower or "فحص" in lower:
            return "جاري فحص الشبكة الآن..."
        elif "استهلاك" in lower or "انترنت" in lower or "الانترنت" in lower:
            return "يمكنك معرفة استهلاك الإنترنت من قسم الاستخدام."
        elif "تجديد" in lower or "باقة" in lower or "الباقة" in lower:
            return "يمكنك تجديد الباقة من قسم الباقات."
        elif "دعم" in lower or "التواصل" in lower:
            return "تم إرسال طلبك إلى فريق الدعم."
        return TEXTS["ar"]["fallback"]



    else:
        if "network" in lower or "check" in lower:
            return "Checking the network now..."
        elif "usage" in lower or "internet" in lower:
            return "You can check your internet usage from the usage section."
        elif "renew" in lower or "package" in lower:
            return "You can renew your package from the packages section."
        elif "support" in lower or "contact" in lower:
            return "Your request has been sent to the support team."
        return TEXTS["en"]["fallback"]





def send_message(text):
    if not text or not text.strip():
        return



    lang = st.session_state["language"]



    st.session_state[CHAT_KEY].append(("user", text.strip()))
    st.session_state[CHAT_KEY].append(("bot", TEXTS[lang]["typing"]))



    time.sleep(0.2)



    st.session_state[CHAT_KEY].pop()



    reply = get_bot_response(text)



    st.session_state[CHAT_KEY].append(("bot", reply))





# =========================
# IMAGE
# =========================
robot = (
    img_to_base64("robot_black.png")
    or img_to_base64("robot_black(2).png")
    or img_to_base64("robot_head.png")
    or img_to_base64("robot.png")
)



if robot:
    avatar_top = f'<img class="avatar-top" src="data:image/png;base64,{robot}">'
    avatar_msg = f'<img class="msg-avatar" src="data:image/png;base64,{robot}">'
else:
    avatar_top = '<div class="avatar-top fallback-avatar">AI</div>'
    avatar_msg = '<div class="msg-avatar fallback-small">AI</div>'





# =========================
# LANGUAGE SWITCH
# =========================
lang_choice = st.segmented_control(
    "",
    ["العربية", "English"],
    default="العربية" if st.session_state["language"] == "ar" else "English"
)



new_lang = "ar" if lang_choice == "العربية" else "en"



if new_lang != st.session_state["language"]:
    st.session_state["language"] = new_lang
    st.session_state[CHAT_KEY] = [("bot", WELCOME[new_lang])]
    reset_context()
    st.rerun()



lang = st.session_state["language"]
t = TEXTS[lang]
direction = "rtl" if lang == "ar" else "ltr"
align = "right" if lang == "ar" else "left"





# =========================
# CSS
# =========================
st.markdown(f"""
<style>
html, body, [data-testid="stAppViewContainer"] {{
    background:#eef2f7 !important;
    direction:{direction} !important;
}}



header, footer, #MainMenu, [data-testid="stToolbar"] {{
    display:none !important;
    visibility:hidden !important;
}}



.block-container {{
    width:430px !important;
    max-width:430px !important;
    height:820px !important;
    max-height:820px !important;
    margin:20px auto !important;
    padding:20px 16px 90px !important;
    background:linear-gradient(180deg,#c7e6fb,#dff1ff) !important;
    border-radius:38px !important;
    box-shadow:0 12px 35px rgba(0,0,0,.12) !important;
    overflow:hidden !important;
}}



.top-card {{
    background:white;
    border-radius:18px;
    padding:9px 12px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    box-shadow:0 5px 15px rgba(0,0,0,.10);
    margin-bottom:16px;
}}



.location {{
    font-size:11px;
    font-weight:800;
    color:#0f2446;
}}



.ready {{
    font-size:13px;
    font-weight:900;
    color:#111827;
    display:flex;
    align-items:center;
    gap:6px;
}}



.dot {{
    width:7px;
    height:7px;
    background:#22c55e;
    border-radius:50%;
    display:inline-block;
}}



.avatar-top {{
    width:42px;
    height:42px;
    border-radius:50%;
    object-fit:cover;
    background:#111827;
    box-shadow:0 3px 10px rgba(0,0,0,.15);
}}



.quick-title {{
    color:#0f2446;
    font-size:12px;
    font-weight:900;
    margin:8px 0 10px;
    text-align:{align};
}}



div[data-testid="column"] {{
    padding:4px !important;
}}



div[data-testid="stButton"] button {{
    width:100%;
    min-height:40px;
    border:none !important;
    border-radius:18px !important;
    background:white !important;
    color:#003f88 !important;
    font-weight:700 !important;
    font-size:13px !important;
    box-shadow:0 5px 14px rgba(0,0,0,.10) !important;
}}



.chat-area {{
    height:370px;
    overflow-y:auto;
    padding:10px 4px;
    margin-top:12px;
    margin-bottom:10px;
}}



.message-row {{
    display:flex;
    align-items:flex-end;
    gap:8px;
    margin-bottom:12px;
}}



.bot-row {{
    justify-content:flex-start;
}}



.user-row {{
    justify-content:flex-end;
}}



.msg {{
    max-width:72%;
    padding:10px 14px;
    border-radius:15px;
    font-size:13px;
    line-height:1.8;
    word-wrap:break-word;
    white-space:pre-wrap;
    box-shadow:0 3px 10px rgba(0,0,0,.08);
}}



.bot {{
    background:white;
    color:#111827;
    border-bottom-left-radius:5px;
    text-align:{align};
    direction:{direction};
}}



.user {{
    background:#1677e8;
    color:white;
    border-bottom-right-radius:5px;
    text-align:{align};
    direction:{direction};
}}



.msg-avatar, .user-avatar {{
    width:34px;
    height:34px;
    border-radius:50%;
    flex-shrink:0;
}}



.msg-avatar {{
    object-fit:cover;
    background:white;
    box-shadow:0 2px 8px rgba(0,0,0,.12);
}}



.user-avatar {{
    background:#dbeafe;
    color:#0f4f91;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:11px;
    font-weight:900;
}}



div[data-testid="stForm"] {{
    position:fixed !important;
    bottom:18px !important;
    left:50% !important;
    transform:translateX(-50%) !important;
    width:398px !important;
    z-index:999999 !important;
    background:white !important;
    padding:10px !important;
    border-radius:28px !important;
    box-shadow:0 4px 15px rgba(0,0,0,.12) !important;
    border:none !important;
}}



div[data-testid="stTextInput"] input {{
    border:none !important;
    box-shadow:none !important;
    background:transparent !important;
    font-size:14px !important;
    direction:{direction} !important;
    text-align:{align} !important;
}}



div[data-testid="stFormSubmitButton"] button {{
    width:42px !important;
    height:42px !important;
    min-height:42px !important;
    border:none !important;
    border-radius:50% !important;
    background:#1677e8 !important;
    color:white !important;
    font-size:18px !important;
    font-weight:900 !important;
}}
</style>
""", unsafe_allow_html=True)





# =========================
# TOP CARD
# =========================
st.markdown(f"""
<div class="top-card">
    <div class="location">Amman 📍</div>
    <div class="ready"><span class="dot"></span>{t["ready"]}</div>
    {avatar_top}
</div>
""", unsafe_allow_html=True)





# =========================
# QUICK SERVICES
# =========================
st.markdown(f'<div class="quick-title">{t["quick"]}</div>', unsafe_allow_html=True)



buttons = t["buttons"]



c1, c2, c3 = st.columns(3)
with c1:
    if st.button(buttons[0][0]):
        send_message(buttons[0][1])
        st.rerun()
with c2:
    if st.button(buttons[1][0]):
        send_message(buttons[1][1])
        st.rerun()
with c3:
    if st.button(buttons[2][0]):
        send_message(buttons[2][1])
        st.rerun()



c4, c5, c6 = st.columns(3)
with c4:
    if st.button(buttons[3][0]):
        send_message(buttons[3][1])
        st.rerun()
with c5:
    if st.button(buttons[4][0]):
        send_message(buttons[4][1])
        st.rerun()
with c6:
    if st.button(buttons[5][0]):
        send_message(buttons[5][1])
        st.rerun()





# =========================
# CHAT
# =========================
chat_html = '<div class="chat-area">'



for role, message in st.session_state[CHAT_KEY]:
    safe_msg = html_lib.escape(str(message))



    if role == "user":
        if lang == "ar":
            chat_html += f"""
            <div class="message-row user-row">
                <div class="user-avatar">{t["user"]}</div>
                <div class="msg user">{safe_msg}</div>
            </div>
            """
        else:
            chat_html += f"""
            <div class="message-row user-row">
                <div class="msg user">{safe_msg}</div>
                <div class="user-avatar">{t["user"]}</div>
            </div>
            """
    else:
        chat_html += f"""
        <div class="message-row bot-row">
            {avatar_msg}
            <div class="msg bot">{safe_msg}</div>
        </div>
        """



chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)





# =========================
# CLEAR CHAT
# =========================
if st.button(t["clear"]):
    st.session_state[CHAT_KEY] = [
        ("bot", WELCOME[st.session_state["language"]])
    ]
    reset_context()
    st.rerun()





# =========================
# INPUT
# =========================
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])



    with col1:
        user_input = st.text_input(
            "",
            placeholder=t["placeholder"],
            label_visibility="collapsed"
        )



    with col2:
        send_btn = st.form_submit_button(t["send"])



    if send_btn and user_input.strip():
        send_message(user_input)
        st.rerun()
