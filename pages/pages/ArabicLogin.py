import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="تطبيق الاتصالات", layout="centered")

# ===== التنقل =====
page = st.query_params.get("page", "")

if page == "customer":
    st.switch_page("pages/Customer_ar.py")

elif page == "employee":
    st.switch_page("pages/employee_dashboard_ara.py")

elif page == "create":
    st.switch_page("pages/1_Create_Account_Arabic.py")

elif page == "forgot":
    st.switch_page("pages/2_Forgot_Password_Arabic.py")

elif page == "todo":
    st.switch_page("pages/4_To_Do_Arabic.py")

# ===== صورة البوت =====
with open("robot.png", "rb") as f:
    img = base64.b64encode(f.read()).decode()

# ===== واجهة HTML =====
html = """
<html>
<head>
<style>

body{
    margin:0;
    background:#eef3f6;
    font-family:Arial;
    direction:rtl;
}

.phone{
    width:360px;
    height:660px;
    margin:auto;
    border-radius:42px;
    overflow:hidden;
    position:relative;
    background:linear-gradient(180deg,#c9e7f7,#dff4ff)
}

.robot{
    position:absolute;
    top:85px;
    left:20px;
    width:145px;
    z-index:3
}

.form{
    position:absolute;
    top:200px;
    right:58px;
    width:244px;
    z-index:2
}

.input{
    width:100%;
    height:40px;
    border-radius:25px;
    margin-bottom:13px;
    padding-right:18px;
    border:none;
    background:white;
    box-sizing:border-box
}

.forgot{
    text-align:center;
    font-size:11px;
    color:#555;
    margin:8px 0 20px;
    cursor:pointer
}

.login{
    width:100%;
    height:46px;
    border-radius:25px;
    background:white;
    text-align:center;
    line-height:46px;
    font-weight:bold;
    border:none;
    cursor:pointer
}

.signup{
    display:block;
    text-align:center;
    font-size:13px;
    margin-top:15px;
    cursor:pointer;
    color:#222;
    text-decoration:none;
}

.error{
    text-align:center;
    color:#c62828;
    font-size:11px;
    margin-top:8px
}

</style>
</head>

<body>

<div class="phone">

<img class="robot" src="data:image/png;base64,IMG_HERE">

<form class="form" method="get" action="/" target="_self" onsubmit="return setPage()">

<input type="hidden" name="page" id="pageValue">

<input id="username" class="input"
placeholder="رقم الهاتف / رقم الهوية"
inputmode="numeric"
maxlength="11"
oninput="this.value=this.value.replace(/[^0-9]/g,'')">

<input class="input"
placeholder="كلمة المرور"
type="password">

<div class="forgot">
    <a href="/?page=forgot"
    target="_self"
    style="color:#555; text-decoration:none;">
        هل نسيت كلمة المرور؟
    </a>
</div>

<button class="login" type="submit">
تسجيل الدخول ›
</button>

<div id="error" class="error"></div>

<div class="signup">
👤 مستخدم جديد؟
<a href="/?page=create"
target="_self"
style="color:#222; text-decoration:underline;">
إنشاء حساب
</a>
</div>

</form>

<script>

function setPage(){

    const v = document.getElementById("username").value;
    const e = document.getElementById("error");
    const pageValue = document.getElementById("pageValue");

    // موظف = 11 رقم
    if(/^[0-9]{11}$/.test(v)){
        pageValue.value = "employee";
        return true;
    }

    // عميل = رقم يبدأ بـ 07 وطوله 10
    if(/^07[0-9]{8}$/.test(v)){
        pageValue.value = "customer";
        return true;
    }

    e.innerText = "رقم الهاتف أو الهوية غير صحيح";
    return false;
}

</script>

</body>
</html>
"""

html = html.replace("IMG_HERE", img)

components.html(html, height=700, scrolling=False)
