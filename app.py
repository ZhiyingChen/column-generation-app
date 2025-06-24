import streamlit as st
import os
import sys


if 'win' not in sys.platform:
    # 防止 matplotlib 和上传报错
    os.environ["MPLCONFIGDIR"] = "/tmp/mplcache"
    os.makedirs("/tmp", exist_ok=True)
    os.makedirs("/tmp/mplcache", exist_ok=True)

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
