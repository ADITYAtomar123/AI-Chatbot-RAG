import os
import time
import streamlit as st

from chatbot import get_response
from pdf_chat import create_vectorstore, search_pdf

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)


# ---------------- SESSION STATE ---------------- #

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

st.title("💬 AI Chatbot")

if len(st.session_state.messages) == 0:
    st.info("""
👋 Welcome!

You can:
- 💬 Chat with AI
- 📄 Upload a PDF
- 🔍 Ask questions from the PDF
- 📥 Download Chat
""")
# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.title("🤖 AI Chatbot")

    st.markdown("### Powered by Groq + Llama 3.3")

    st.markdown("---")

    st.subheader("📊 Chat Statistics")

    st.write(f"Messages: {len(st.session_state.messages)}")

    # New Chat Button

    if st.button("🆕 New Chat"):

        st.session_state.messages = []

        st.rerun()

    st.markdown("---")

    
# Download Chat
history = ""

for msg in st.session_state.messages:
    history += f"{msg['role'].capitalize()} : {msg['content']}\n\n"

st.download_button(
    label="📥 Download Chat",
    data=history,
    file_name="chat_history.txt",
    mime="text/plain"
)

st.markdown("---")
st.caption("Developed by Aditya Tomar")

# ---------------- MAIN PAGE ---------------- #

st.title("💬 AI Chatbot")

st.caption("Ask anything or upload a PDF to chat with it.")

# Display Previous Messages

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])
# ---------------- USER INPUT ---------------- #

col1, col2 = st.columns([4, 1])

with col1:
    uploaded_file = st.file_uploader(
        "📄 Upload PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )

with col2:
    if st.button("🗑 Remove PDF"):
        st.session_state.vectorstore = None
        st.rerun()

if uploaded_file and st.session_state.vectorstore is None:

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    pdf_path = os.path.join("uploads", uploaded_file.name)

    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Processing PDF..."):
        st.session_state.vectorstore = create_vectorstore(pdf_path)

    st.success("✅ PDF Ready for Chat")
    
prompt = st.chat_input("Ask me anything...")

if prompt:

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Copy chat history
    messages = st.session_state.messages.copy()

    # ---------- PDF RAG ---------- #

    if st.session_state.vectorstore is not None:

        context, pages = search_pdf(
        st.session_state.vectorstore,
        prompt
        )

        messages.append(
            {
                "role": "system",
                "content": f"""
You are a helpful AI assistant.

Answer ONLY using the PDF context below.

If the answer is not present in the PDF, reply:
"I couldn't find this information in the uploaded PDF."

PDF Context:
{context}
"""
            }
        )

    # ---------- AI Response ---------- #

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = get_response(messages)

        placeholder = st.empty()

        full_response = ""

        for word in answer.split():

            full_response += word + " "

            placeholder.markdown(full_response)

            time.sleep(0.02)
        if st.session_state.vectorstore is not None and pages:
            st.caption(f"📄 Source Pages: {', '.join(map(str, pages))}")

    # Save AI response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
    # ---------------- PDF STATUS ---------------- #

st.markdown("---")

if st.session_state.vectorstore is not None:

    st.success("📄 PDF is loaded and ready for questions.")

else:

    st.info("💡 Upload a PDF from the sidebar to ask questions from it.")

# ---------------- FOOTER ---------------- #

st.markdown("---")

st.caption("🚀 AI Chatbot with RAG | Powered by Groq + LangChain + FAISS")

st.caption("© 2026 Aditya Tomar")