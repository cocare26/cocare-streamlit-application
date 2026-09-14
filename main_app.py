import streamlit as st

# =====================================
# Page Configuration
# =====================================
st.set_page_config(
    page_title="CoCare",
    page_icon="📱",
    layout="centered"
)

# =====================================
# Read Query Parameter
# =====================================
page = st.query_params.get("page", "")

# =====================================
# Page Navigation
# =====================================
if page == "change_password":
    st.switch_page("pages/ChangePassword.py")

elif page == "change_language":
    st.switch_page("pages/ChangeLanguage.py")

elif page == "rate_app":
    st.switch_page("pages/RateApp.py")

elif page == "contact":
    st.switch_page("pages/ContactUs.py")

elif page == "report":
    st.switch_page("pages/ReportProblem.py")

elif page == "settings_ar":
    st.switch_page("pages/settingar.py")

else:
    st.switch_page("pages/Settings.py")
