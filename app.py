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
    - **项目背景**：了解算法背景与输入输出格式
    - **执行算法**：上传输入文件，运行算法并查看结果
    """)

    function.render_footer()

