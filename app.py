import streamlit as st
from web import function

if __name__ == '__main__':
    st.set_page_config(
        page_title="卷纸切割算法平台",
        page_icon="📦",
        layout="wide"
    )

    st.title("📦 卷纸切割算法平台")
    st.markdown("欢迎使用！请通过左侧导航栏选择功能页面：")

    st.markdown("""
        ### 📘 页面导航说明：
        - **项目背景**：了解问题背景
        - **执行算法**：了解输入输出文件格式，编辑输入文件，运行算法并查看结果
        """)

    function.render_footer()

