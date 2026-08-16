import os
import time
import streamlit as st
import streamlit.components.v1 as components
import extra_streamlit_components as stx
import pandas as pd
import plotly.express as px

from chatbot import get_response
from database import (
    register,
    login,
    create_conversation,
    load_messages,
    save_message,
    get_conversations,
    rename_conversation,
    delete_conversation,
    save_memory,
    get_all_memory,
    delete_memory,
)
from vision import load_image, analyze_image
from pdf_chat import create_vectorstore, search_pdf
from voice import speech_to_text
from streamlit_mic_recorder import mic_recorder
from web_search import web_search
from memory import detect_memory
from csv_chat import load_csv, dataframe_to_text
from docx_chat import extract_docx


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# COOKIE MANAGER
# IMPORTANT: create it only ONCE
# ============================================================

cookie_manager = stx.CookieManager(key="main_cookie_manager")


# ============================================================
# MODERN UI
# ============================================================

st.markdown(
    """
<style>

/* ---------- GLOBAL ---------- */

.stApp {
    background: #0b0f14;
    color: #e6edf3;
}

.main .block-container {
    max-width: 1200px;
    padding-top: 1.8rem;
    padding-bottom: 7rem;
}

h1, h2, h3 {
    color: #f5f7fa !important;
}

h1 {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
}


/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background: #111820;
    border-right: 1px solid #26313d;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.2rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

section[data-testid="stSidebar"] * {
    color: #e6edf3;
}

section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid #293542;
    background: #151c24;
    color: #e6edf3;
    transition: all 0.2s ease;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    border-color: #6ea8fe;
    background: #1b2530;
    transform: translateY(-1px);
}


/* ---------- BUTTONS ---------- */

.stButton > button {
    border-radius: 10px;
    border: 1px solid #303b48;
    background: #151c24;
    color: #e6edf3;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    border-color: #6ea8fe;
    background: #1b2530;
    transform: translateY(-1px);
}


/* ---------- CHAT ---------- */

div[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 14px 18px;
    margin-bottom: 12px;
    border: 1px solid #26313d;
    background: #111820;
}

div[data-testid="stChatMessage"] p {
    font-size: 15px;
    line-height: 1.6;
}


/* ---------- CHAT INPUT ---------- */

div[data-testid="stChatInput"] {
    background: #151c24;
    border: 1px solid #303b48;
    border-radius: 18px;
    padding: 4px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
}

div[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 16px;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #8b98a5 !important;
}

div[data-testid="stChatInput"]:focus-within {
    border-color: #6ea8fe;
    box-shadow: 0 0 0 2px rgba(110,168,254,0.15);
}


/* ---------- METRICS ---------- */

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #151c24, #111820);
    border: 1px solid #26313d;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.20);
    transition: 0.2s;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: #6ea8fe;
}

div[data-testid="stMetric"] label {
    color: #8b98a5 !important;
}

div[data-testid="stMetricValue"] {
    color: #f5f7fa !important;
    font-weight: 700;
}


/* ---------- INPUTS ---------- */

div[data-baseweb="input"] {
    background: #151c24;
    border-radius: 10px;
    border: 1px solid #303b48;
}

div[data-baseweb="input"] input {
    color: #ffffff !important;
}

div[data-baseweb="select"] > div {
    border-radius: 10px;
    background: #151c24;
    border-color: #303b48;
}

div[data-baseweb="select"] input {
    color: white !important;
}


/* ---------- FILE UPLOADER ---------- */

section[data-testid="stFileUploaderDropzone"] {
    border-radius: 14px;
    border: 1px dashed #3b4754;
    background: #111820;
    padding: 20px;
    transition: all 0.2s ease;
}

section[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #6ea8fe;
    background: #151c24;
}


/* ---------- DATAFRAME ---------- */

div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #26313d;
}


/* ---------- EXPANDER / ALERT ---------- */

div[data-testid="stExpander"] {
    border-radius: 12px;
    border: 1px solid #26313d;
    background: #111820;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}


/* ---------- TEXT ---------- */

.stCaption {
    color: #8b98a5 !important;
}

hr {
    border-color: #26313d;
}


/* ---------- SCROLLBAR ---------- */

::-webkit-scrollbar {
    width: 7px;
}

::-webkit-scrollbar-track {
    background: #0b0f14;
}

::-webkit-scrollbar-thumb {
    background: #303b48;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #4a5868;
}


/* ---------- HEADER / FOOTER ---------- */

header[data-testid="stHeader"] {
    background: transparent;
}

footer {
    visibility: hidden;
}


/* ---------- MOBILE ---------- */

@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    h1 {
        font-size: 1.8rem !important;
    }

    div[data-testid="stChatMessage"] {
        padding: 10px 12px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def copy_text_button(text, key):
    safe_text = (
        str(text)
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )

    components.html(
        f"""
        <script>
        function copyText_{key}() {{
            const text = `{safe_text}`;
            navigator.clipboard.writeText(text);
            document.getElementById("copyBtn_{key}").innerText = "✅ Copied!";

            setTimeout(function() {{
                document.getElementById("copyBtn_{key}").innerText = "📋 Copy";
            }}, 1500);
        }}
        </script>

        <button
            id="copyBtn_{key}"
            onclick="copyText_{key}()"
            style="
                width:100%;
                padding:9px 16px;
                border:1px solid #303b48;
                border-radius:10px;
                background:#151c24;
                color:#ffffff;
                font-size:14px;
                cursor:pointer;
            "
        >
            📋 Copy
        </button>
        """,
        height=50,
    )


# ============================================================
# EXPORT CHAT
# ============================================================

def export_chat(messages):

    text = ""

    for msg in messages:

        role = msg["role"].upper()

        text += f"{role}\n"
        text += f"{msg['content']}\n"
        text += "\n" + "=" * 60 + "\n\n"

    return text


def create_chart(df, chart_type, x_column, y_column):
    if chart_type == "bar":
        return px.bar(
            df,
            x=x_column,
            y=y_column,
            title=f"{y_column} by {x_column}",
        )

    if chart_type == "line":
        return px.line(
            df,
            x=x_column,
            y=y_column,
            title=f"{y_column} by {x_column}",
        )

    if chart_type == "pie":
        return px.pie(
            df,
            names=x_column,
            values=y_column,
            title=f"{y_column} Distribution",
        )

    return px.scatter(
        df,
        x=x_column,
        y=y_column,
        title=f"{y_column} vs {x_column}",
    )


# ============================================================
# SESSION STATE
# IMPORTANT: initialize BEFORE using logged_in/cookies
# ============================================================

defaults = {
    "conversation_id": None,
    "messages": [],
    "logged_in": False,
    "vectorstore": None,
    "csv_context": None,
    "excel_context": None,
    "docx_context": None,
    "chart_df": None,
    "rename_chat": None,
    "attachment_type": "None",
    "documents_count": 0,
    "charts_count": 0,
    "last_prompt": None,
    "regenerate": False,
    "internet_search": False,
    "theme": "Dark",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# COOKIE LOGIN
# ============================================================

cookies = cookie_manager.get_all()

if (
    not st.session_state["logged_in"]
    and cookies.get("logged_in") == "true"
):
    st.session_state["logged_in"] = True


# ============================================================
# LOGIN / REGISTER PAGE
# ============================================================

if not st.session_state["logged_in"]:

    st.markdown(
        """
        <div style="
            max-width:600px;
            margin:60px auto 20px auto;
            text-align:center;
        ">
            <div style="font-size:55px;">🤖</div>
            <h1>AI Chatbot</h1>
            <p style="color:#8b98a5;">
                Your intelligent assistant for chat, documents,
                images and data.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    option = st.radio(
        "Select Option",
        ["Login", "Register"],
        horizontal=True,
    )

    if option == "Register":

        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input(
            "Password",
            type="password",
        )

        if st.button(
            "Create Account",
            use_container_width=True,
        ):
            result = register(
                name,
                email,
                password,
            )

            if result:
                st.success("Registration Successful. Please login.")
            else:
                st.error("Email already exists.")

    else:

        email = st.text_input("Email")
        password = st.text_input(
            "Password",
            type="password",
        )

        if st.button(
            "Login",
            use_container_width=True,
        ):

            user = login(
                email,
                password,
            )

            if user:

                st.session_state["logged_in"] = True

                cookie_manager.set(
                    "logged_in",
                    "true",
                )

                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid Email or Password")

    st.stop()


# ---------------- MODERN SIDEBAR ---------------- #
with st.sidebar:

    st.markdown("## 🤖 AI Chatbot")
    st.caption("Your Intelligent Assistant")

    st.divider()

    st.markdown("### 🌐 Internet Search")

    st.session_state["internet_search"] = st.toggle(
        "Enable Internet Search",
        value=st.session_state["internet_search"],
        help="Allow AI to use internet search for current information."
    )

    if st.session_state["internet_search"]:
        st.success("🌐 Internet Search ON")
    else:
        st.caption("Internet Search OFF")

    st.divider()
    
    page = st.radio(
        "Navigation",
        ["💬 Chat", "🏠 Dashboard"],
        label_visibility="collapsed",
        key="main_navigation"
    )

    st.divider()

    if st.button(
        "✨ New Chat",
        use_container_width=True,
        key="new_chat_sidebar"
    ):

        cid = create_conversation("New Conversation")

        st.session_state.conversation_id = cid
        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.markdown("### 💬 Recent Chats")

    conversations = get_conversations()

    if conversations:

        for cid, title in conversations[:8]:

            if st.button(
                f"💬 {title}",
                key=f"sidebar_chat_{cid}",
                use_container_width=True
            ):

                st.session_state.conversation_id = cid

                old_messages = load_messages(cid)

                st.session_state.messages = [
                    {
                        "role": role,
                        "content": message
                    }
                    for role, message in old_messages
                ]

                st.rerun()

    else:

        st.caption("No conversations yet.")

    st.divider()


    if st.button("Logout"):
        try:
            cookie_manager.delete("logged_in")
        except KeyError:
            pass    

        st.session_state["logged_in"] = False
        st.session_state["conversation_id"] = None
        st.session_state["messages"] = []
        st.session_state["vectorstore"] = None
        st.session_state["csv_context"] = None
        st.session_state["excel_context"] = None
        st.session_state["docx_context"] = None

        st.rerun()

    st.caption("🚀 AI Chatbot")
    st.caption("Powered by Groq + LangChain + FAISS")

# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    conversations = get_conversations()
    memories = get_all_memory()
    
    st.markdown(
        """
        <div style="padding:5px 0 15px 0;">
            <h1>🏠 Dashboard</h1>
            <p style="color:#8b98a5;">
                Overview of your AI Chatbot activity.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💬 Conversations",
            len(conversations),
        )

    with col2:

        document_count = 0

        if st.session_state["vectorstore"]:
            document_count += 1

        if st.session_state["docx_context"]:
            document_count += 1

        if st.session_state["csv_context"]:
            document_count += 1

        if st.session_state["excel_context"]:
            document_count += 1

        st.metric(
            "📄 Documents",
            document_count,
        )

    with col3:
        st.metric(
            "🧠 Memories",
            len(memories),
        )

    with col4:
        st.metric(
            "📊 Charts",
            st.session_state["charts_count"],
        )


        # ========================================================
    # MEMORY MANAGEMENT
    # ========================================================

    st.divider()

    st.subheader("🧠 Saved Memories")

    if memories:

        for index, (key, value) in enumerate(memories):

            col1, col2 = st.columns([8, 1])

            with col1:

                st.markdown(
                    f"**{key}**: {value}"
                )

            with col2:

                if st.button(
                    "🗑️",
                    key=f"delete_memory_{index}",
                    help="Delete this memory",
                ):

                    delete_memory(key)

                    st.success(
                        "Memory deleted successfully."
                    )

                    st.rerun()

    else:

        st.info(
            "🧠 No memories saved yet."
        )


        # ========================================================
    # AVAILABLE FEATURES
    # ========================================================

    st.divider()

    st.subheader("⚡ Available Features")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "📄 **Document AI**\n\n"
            "Chat with PDF and DOCX documents."
        )

    with col2:

        st.info(
            "📊 **Data Analysis**\n\n"
            "Analyze CSV and Excel files."
        )

    with col3:

        st.info(
            "🖼️ **Vision AI**\n\n"
            "Analyze uploaded images."
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "🧠 **AI Memory**\n\n"
            "Save and manage useful information."
        )

    with col2:

        st.info(
            "🌐 **Web Search**\n\n"
            "Get current information from the internet."
        )

    with col3:

        st.info(
            "🎤 **Voice AI**\n\n"
            "Interact with the assistant using voice."
        )
    # ========================================================
    # QUICK ACTIONS
    # ========================================================
    st.divider()
    st.subheader("🚀 Quick Actions")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🆕 Start New Chat",
            use_container_width=True,
            key="dashboard_new_chat",
        ):

            cid = create_conversation("New Conversation")

            st.session_state["conversation_id"] = cid
            st.session_state["messages"] = []

            st.rerun()

    with col2:
        st.info("📎 Upload documents from Chat.")

    st.divider()

    st.subheader("💬 Recent Conversations")

    if conversations:

        for cid, title in conversations[:5]:

            if st.button(
                f"💬 {title}",
                key=f"dashboard_open_{cid}",
                use_container_width=True,
            ):

                st.session_state["conversation_id"] = cid

                old_messages = load_messages(cid)

                st.session_state["messages"] = [
                    {
                        "role": role,
                        "content": message,
                    }
                    for role, message in old_messages
                ]

                st.rerun()

    else:
        st.info("No conversations yet.")

    st.divider()

    st.caption(
        "🚀 AI Chatbot | Powered by Groq + LangChain + FAISS"
    )

    st.stop()


# ---------------- CHAT HEADER ---------------- #

st.title("🤖 AI Chatbot")

st.caption(
    "Your intelligent assistant for chat, documents, images and data."
)

# ============================================================
# LOAD OLD CHAT
# ============================================================

if (
    len(st.session_state["messages"]) == 0
    and st.session_state["conversation_id"]
):

    old_messages = load_messages(
        st.session_state["conversation_id"]
    )

    for role, message in old_messages:

        st.session_state["messages"].append(
            {
                "role": role,
                "content": message,
            }
        )


# ============================================================
# CHAT HISTORY
# ============================================================

if st.session_state["messages"]:

    for msg in st.session_state["messages"]:

        avatar = "👤" if msg["role"] == "user" else "🤖"

        with st.chat_message(
            msg["role"],
            avatar=avatar,
        ):
            st.markdown(msg["content"])


# ============================================================
# DOWNLOAD CHAT
# ============================================================

if st.session_state["messages"]:

    st.download_button(
        label="📥 Download Chat",
        data=export_chat(
            st.session_state["messages"]
        ),
        file_name="ai_chat.txt",
        mime="text/plain",
        use_container_width=True,
    )
# ============================================================
# CHAT HISTORY MANAGEMENT
# ============================================================

with st.expander("💬 Manage Chats"):

    conversations = get_conversations()

    if conversations:

        for cid, title in conversations:

            col1, col2, col3 = st.columns([6, 1, 1])

            with col1:

                if st.button(
                    title,
                    key=f"open_chat_{cid}",
                    use_container_width=True,
                ):

                    st.session_state["conversation_id"] = cid

                    old_messages = load_messages(cid)

                    st.session_state["messages"] = [
                        {
                            "role": role,
                            "content": message,
                        }
                        for role, message in old_messages
                    ]

                    st.rerun()

            with col2:

                if st.button(
                    "✏️",
                    key=f"rename_chat_{cid}",
                ):
                    st.session_state["rename_chat"] = cid

            with col3:

                if st.button(
                    "🗑️",
                    key=f"delete_chat_{cid}",
                ):

                    delete_conversation(cid)

                    if (
                        st.session_state["conversation_id"]
                        == cid
                    ):
                        st.session_state["conversation_id"] = None
                        st.session_state["messages"] = []

                    st.rerun()

    else:
        st.info("No chats available.")


# ============================================================
# RENAME CHAT
# ============================================================

if st.session_state["rename_chat"]:

    st.divider()

    st.subheader("Rename Chat")

    new_name = st.text_input(
        "New Name",
        key="new_chat_name",
    )

    if st.button(
        "Save Name",
        use_container_width=True,
        key="save_chat_name",
    ):

        if new_name.strip():

            rename_conversation(
                st.session_state["rename_chat"],
                new_name.strip(),
            )

            st.session_state["rename_chat"] = None

            st.rerun()


# ============================================================
# ATTACHMENTS
# ============================================================

st.divider()

st.markdown("## 📎 Attachments")

st.caption(
    "Upload PDF, DOCX, CSV, Excel or Image"
)

attachment_type = st.selectbox(
    "Choose file type",
    [
        "None",
        "📄 PDF",
        "📝 DOCX",
        "📊 CSV",
        "📈 Excel",
        "🖼 Image",
    ],
    key="attachment_type",
)


# ============================================================
# PDF
# ============================================================

if attachment_type == "📄 PDF":

    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="attachment_pdf",
    )

    if uploaded_pdf:

        os.makedirs("uploads", exist_ok=True)

        pdf_path = os.path.join(
            "uploads",
            uploaded_pdf.name,
        )

        with open(pdf_path, "wb") as f:
            f.write(uploaded_pdf.getbuffer())

        with st.spinner("Processing PDF..."):

            st.session_state["vectorstore"] = create_vectorstore(
                pdf_path
            )


        st.success("✅ PDF Ready for Chat")

        if st.button(
            "🗑 Remove PDF",
            key="remove_pdf",
        ):

            st.session_state["vectorstore"] = None
            st.rerun()


# ============================================================
# DOCX
# ============================================================

elif attachment_type == "📝 DOCX":

    uploaded_docx = st.file_uploader(
        "Upload Word Document",
        type=["docx"],
        key="attachment_docx",
    )

    if uploaded_docx:

        with st.spinner("Processing DOCX..."):

            doc_text = extract_docx(
                uploaded_docx
            )

        st.session_state["docx_context"] = doc_text

        st.success("✅ DOCX Ready for Chat")


# ============================================================
# CSV
# ============================================================

elif attachment_type == "📊 CSV":

    uploaded_csv = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        key="attachment_csv",
    )

    if uploaded_csv:

        df = load_csv(uploaded_csv)

        st.dataframe(
            df,
            use_container_width=True,
        )

        st.session_state["csv_context"] = dataframe_to_text(df)
        st.session_state["chart_df"] = df

        st.success("✅ CSV Ready for Chat")

        # Chart creation
        st.subheader("📊 Create Chart")

        if len(df.columns) >= 2:

            chart_type = st.selectbox(
                "Chart Type",
                ["bar", "line", "pie", "scatter"],
                key="csv_chart_type",
            )

            x_column = st.selectbox(
                "X Column",
                df.columns,
                key="csv_x_column",
            )

            y_column = st.selectbox(
                "Y Column",
                df.columns,
                key="csv_y_column",
            )

            if st.button(
                "📈 Generate Chart",
                key="generate_csv_chart",
            ):

                try:

                    fig = create_chart(
                        df,
                        chart_type,
                        x_column,
                        y_column,
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                    )

                    st.session_state["charts_count"] += 1

                except Exception as e:
                    st.error(f"Chart Error: {e}")


# ============================================================
# EXCEL
# ============================================================

elif attachment_type == "📈 Excel":

    uploaded_excel = st.file_uploader(
        "Upload Excel",
        type=["xlsx"],
        key="attachment_excel",
    )

    if uploaded_excel:

        with st.spinner("Reading Excel..."):

            df = pd.read_excel(uploaded_excel)

        st.dataframe(
            df,
            use_container_width=True,
        )

        st.session_state["excel_context"] = dataframe_to_text(df)
        st.session_state["chart_df"] = df

        st.success("✅ Excel Ready for Chat")


# ============================================================
# IMAGE
# ============================================================

elif attachment_type == "🖼 Image":

    uploaded_image = st.file_uploader(
        "Upload Image",
        type=["jpg", "jpeg", "png"],
        key="attachment_image",
    )

    if uploaded_image:

        image = load_image(uploaded_image)

        st.image(
            image,
            caption="Uploaded Image",
            use_container_width=True,
        )

        image_question = st.text_input(
            "Ask about this image",
            placeholder="What is in this image?",
            key="image_question",
        )

        if st.button(
            "🔍 Analyze Image",
            key="attachment_analyze_image",
        ):

            question = (
                image_question
                if image_question
                else "Describe this image."
            )

            with st.spinner("Analyzing image..."):

                result = analyze_image(
                    uploaded_image,
                    question,
                )

            st.subheader("🤖 AI Response")
            st.write(result)


# ============================================================
# VOICE + CHAT INPUT
# ============================================================

audio = mic_recorder(
    start_prompt="🎤",
    stop_prompt="⏹",
    key="voice_input",
)

if audio:
    prompt = speech_to_text()
else:
    prompt = st.chat_input(
        "Ask me anything..."
    )


# ============================================================
# REGENERATE STATE
# ============================================================

is_regenerating = False

if st.session_state["regenerate"]:

    prompt = st.session_state["last_prompt"]

    is_regenerating = True

    st.session_state["regenerate"] = False


# ============================================================
# MEMORY
# ============================================================

if prompt and not is_regenerating:

    memory = detect_memory(prompt)

    if memory:

        save_memory(
            memory[0],
            memory[1],
        )


# ============================================================
# CHAT RESPONSE
# ============================================================

if prompt:

    # ---------- USER MESSAGE ----------

    if not is_regenerating:

        with st.chat_message(
            "user",
            avatar="👤",
        ):
            st.markdown(prompt)

        st.session_state["messages"].append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        if st.session_state["conversation_id"]:

            save_message(
                st.session_state["conversation_id"],
                "user",
                prompt,
            )


    # ---------- AI MESSAGES ----------

    messages = st.session_state["messages"].copy()


    # ---------- CSV CONTEXT ----------

    if st.session_state["csv_context"]:

        messages.append(
            {
                "role": "system",
                "content": f"""
Use the following CSV data to answer the user's question.

CSV DATA:

{st.session_state["csv_context"]}
""",
            }
        )


    # ---------- EXCEL CONTEXT ----------

    if st.session_state["excel_context"]:

        messages.append(
            {
                "role": "system",
                "content": f"""
Use the following Excel data to answer the user's question.

EXCEL DATA:

{st.session_state["excel_context"]}
""",
            }
        )


    # ---------- DOCX CONTEXT ----------

    if st.session_state["docx_context"]:

        messages.append(
            {
                "role": "system",
                "content": f"""
Use the following DOCX content to answer the user's question.

DOCX CONTENT:

{st.session_state["docx_context"]}
""",
            }
        )


    # ---------- MEMORY CONTEXT ----------

    memories = get_all_memory()

    if memories:

        memory_text = ""

        for key, value in memories:
            memory_text += f"{key}: {value}\n"

        messages.append(
            {
                "role": "system",
                "content": f"""
User Memory:

{memory_text}

Use the memory only when it is relevant.
""",
            }
        )


    # ---------- PDF CONTEXT ----------

    pages = []

    if st.session_state["vectorstore"]:

        context, pages = search_pdf(
            st.session_state["vectorstore"],
            prompt,
        )

        messages.append(
            {
                "role": "system",
                "content": f"""
Answer the user's question using the PDF context below.

PDF CONTEXT:

{context}

If the answer is not available in the PDF,
say that the information was not found in the PDF.
""",
            }
        )


    # ---------- INTERNET SEARCH ----------

    if st.session_state["internet_search"]:

        with st.spinner("Searching the internet..."):

            web_context = web_search(prompt)

        messages.append(
            {
                "role": "system",
                "content": f"""
Use the following internet information
to answer the user's question.

INTERNET INFORMATION:

{web_context}
""",
            }
        )


    # ---------- AI RESPONSE ----------

    with st.chat_message(
        "assistant",
        avatar="🤖",
    ):

        typing_box = st.empty()

        typing_box.markdown(
            "🤖 AI is typing... ● ● ●"
        )

        try:

            answer = get_response(messages)

        except Exception as e:

            typing_box.empty()

            st.error(
                f"❌ AI Error: {str(e)}"
            )

            answer = None


        # ---------- DISPLAY RESPONSE ----------

        if answer:

            typing_box.empty()

            placeholder = st.empty()

            full_response = ""

            for word in answer.split():

                full_response += word + " "

                placeholder.markdown(
                    full_response
                )

                time.sleep(0.02)


            if pages:

                st.caption(
                    "📄 Source Pages: "
                    + ", ".join(map(str, pages))
                )


            # ---------- COPY ----------

            copy_text_button(
                answer,
                f"copy_{len(st.session_state['messages'])}",
            )


            # ---------- SAVE AI RESPONSE ----------

            st.session_state["messages"].append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            if st.session_state["conversation_id"]:

                save_message(
                    st.session_state["conversation_id"],
                    "assistant",
                    answer,
                )


# ============================================================
# REGENERATE
# ============================================================

if (
    st.session_state["messages"]
    and st.session_state["messages"][-1]["role"] == "assistant"
):

    if st.button(
        "🔄 Regenerate",
        key="regenerate_button",
    ):

        # Remove current assistant response
        st.session_state["messages"].pop()

        # Find last user prompt
        last_user_prompt = None

        for msg in reversed(
            st.session_state["messages"]
        ):

            if msg["role"] == "user":

                last_user_prompt = msg["content"]
                break

        if last_user_prompt:

            st.session_state["last_prompt"] = last_user_prompt
            st.session_state["regenerate"] = True

            st.rerun()


# ============================================================
# STATUS
# ============================================================

st.divider()

if st.session_state["vectorstore"]:

    st.success(
        "📄 PDF Loaded — You can ask questions about it."
    )

else:

    st.info(
        "Upload PDF to chat with your document."
    )

st.divider()

st.caption(
    "🚀 AI Chatbot with RAG | Groq + LangChain + FAISS"
)

st.caption(
    "© 2026 Aditya Tomar"
)
