import streamlit as st


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