import streamlit as st
from web.language_dict import APP_LANG, ROLL_DOC_LANG

def render_language_selector():
    """在 sidebar 渲染语言选择器，并更新 session_state"""
    if "lang" not in st.session_state:
        st.session_state["lang"] = "中文"  # 默认语言
    lang = st.sidebar.selectbox("语言 / Language", ["中文", "English"], index=0 if st.session_state["lang"] == "中文" else 1)
    st.session_state["lang"] = lang

def get_language_dict(page: str = "app"):
    lang = st.session_state.get("lang", "中文")
    if page == "app":
        return lang, APP_LANG[lang]
    elif page == "doc":
        return lang, ROLL_DOC_LANG[lang]
    else:
        raise ValueError("Unknown page type. Use 'app', 'algo', 'doc'.")


def render_footer():
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.9em;'>
            © 2025 Zhiying Chen | All Rights Reserved | Column Generation Demo Powered by Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )