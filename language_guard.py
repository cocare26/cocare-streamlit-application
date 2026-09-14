import streamlit as st

AR_TO_EN = {
    "settingar.py": "pages/Settings.py",
    "Change_Languagear.py": "pages/ChangeLanguage.py",
    "Change_Passwordar.py": "pages/ChangePassword.py",
    "ContactUsar.py": "pages/ContactUs.py",
    "Rate_Appar.py": "pages/RateApp.py",
    "Report_Problemar.py": "pages/ReportProblem.py",
    "Customer_ar.py": "pages/2_Customer_EN.py",
}

EN_TO_AR = {
    "Settings.py": "pages/settingar.py",
    "ChangeLanguage.py": "pages/Change_Languagear.py",
    "ChangePassword.py": "pages/Change_Passwordar.py",
    "ContactUs.py": "pages/ContactUsar.py",
    "RateApp.py": "pages/Rate_Appar.py",
    "ReportProblem.py": "pages/Report_Problemar.py",
    "2_Customer_EN.py": "pages/Customer_ar.py",
}


def check_language(current_file):

    if "lang" not in st.session_state:
        st.session_state.lang = "en"

    lang = st.session_state.lang

    if lang == "ar" and current_file in EN_TO_AR:
        st.switch_page(EN_TO_AR[current_file])

    elif lang == "en" and current_file in AR_TO_EN:
        st.switch_page(AR_TO_EN[current_file])
