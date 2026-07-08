import streamlit as st

st.set_page_config(page_title="Identity Echo Interface", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("Identity Echo Interface")
st.write("Share your identity and transmit a message through this interface.")
st.divider()

with st.sidebar:
    st.header("Project Overview")
    st.write("This app lets users send a short message with their name. It includes validation, token estimation, and a clean layout.")
    st.divider()
    st.caption("Developed by GitHub Copilot")

main_col, side_col = st.columns([2, 1], gap="large")

with main_col:
    st.markdown("### Transmission Form")
    st.write("Fill in the details below and transmit your message.")

    name = st.text_input("Name", placeholder="Enter your name").strip()
    message = st.text_area("Message", placeholder="Type your message here", height=140).strip()

    total_chars = len(name) + len(message)
    st.caption(f"Character count: {total_chars}")
    st.info(f"Estimated AI Token Usage: {total_chars / 4:.2f} tokens")

    if st.button("Transmit", use_container_width=True):
        if not name:
            st.error("Please provide your name.")
        elif not message:
            st.warning("Please type a message to transmit.")
        else:
            st.success(f"Transmission successful!\n\nGreetings, {name}.\n\nWe received your message:\n\n\"{message}\"")

with side_col:
    st.markdown("### Quick Notes")
    st.write("- Trims whitespace before validating input.\n- Token estimates are total characters divided by four.\n- The layout uses columns and containers.")
