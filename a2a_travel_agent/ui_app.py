import streamlit as st
import requests

API_URL = "http://localhost:8000"  # change this if needed

st.set_page_config(page_title="Local Agent Chat", page_icon="💬")

st.title("💬 Local Agent Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Ask something...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/plan",
                    json={"query": query},
                    timeout=300,
                )

                response.raise_for_status()
                data = response.json()

                answer = (
                    data.get("answer")
                    or data.get("response")
                    or data.get("itinerary")
                    or str(data)
                )

            except Exception as e:
                answer = f"Error: {e}"

            st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )