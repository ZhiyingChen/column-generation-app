import streamlit as st
from web import function

if __name__ == '__main__':
    st.set_page_config(
        page_title="卷纸切割算法平台",
        page_icon="📦",
        layout="wide"
    )

    # 渲染语言栏
    function.render_language_selector()
    # 获取语言字典
    lang, T = function.get_language_dict("app")


    # 页面内容
    st.title(T["title"])
    st.markdown(T["welcome"])
    st.markdown(T["navigation"])

    function.render_footer()

