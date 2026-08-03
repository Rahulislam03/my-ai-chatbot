import os
from groq import Groq
import streamlit as st

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="My AI Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS for UI polish
st.markdown(
    """
    <style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ---------------- 2. SIDEBAR CONFIGURATION ----------------
with st.sidebar:
  st.title("⚙️ সেটিংস")

  # API Key Input Option (যদি Streamlit Secrets এ না থাকে)
  user_api_key = st.text_input(
      "Groq API Key (ঐচ্ছিক):",
      type="password",
      help="এখানে সরাসরি API Key দিতে পারেন অথবা Streamlit Secrets এ সেট করে রাখতে পারেন।",
  )

  # System Prompt Customization
  system_prompt = st.text_area(
      "AI-এর নির্দেশনা (System Prompt):",
      value=(
          "তুমি একটি অত্যন্ত বুদ্ধিমান, ভদ্র এবং সহায়ক AI অ্যাসিস্ট্যান্ট। "
          "কাস্টমারের সাথে বাংলায় সাবলীল, সুন্দর ও নির্ভুলভাবে কথা বলো। "
          "যেকোনো প্রশ্নের সঠিক উত্তর দাও।"
      ),
      height=120,
  )

  st.divider()

  # Clear Chat History Button
  if st.button("🗑️ চ্যাট হিস্ট্রি ক্লিয়ার করুন", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# ---------------- 3. INITIALIZE GROQ CLIENT ----------------
# Secrets অথবা Sidebar থেকে API Key গ্রহণ
api_key = user_api_key or os.getenv("GROQ_API_KEY")

st.title("🤖 আমার নিজস্ব AI অ্যাসিস্ট্যান্ট")
st.caption("Powered by Groq (Llama-3.3-70B) & Streamlit")

if not api_key:
  st.warning(
      "⚠️ অনুগ্রহ করে সাইডবারে আপনার Groq API Key দিন অথবা Streamlit Secrets এ"
      " GROQ_API_KEY সেট করুন।"
  )
  st.info(
      "💡 ফ্রি API Key পেতে ব্রাউজারে console.groq.com ভিজিট করে একটি Key তৈরি করে"
      " নিন।"
  )
  st.stop()

# Groq Client Initialization
try:
  client = Groq(api_key=api_key)
except Exception as e:
  st.error(f"Groq Client সাজাতে সমস্যা হয়েছে: {e}")
  st.stop()

# ---------------- 4. CHAT HISTORY MANAGEMENT ----------------
if "messages" not in st.session_state:
  st.session_state.messages = []

# পূর্বে পাঠানো মেসেজগুলো স্ক্রিনে দেখানো
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# ---------------- 5. USER INPUT & RESPONSE GENERATION ----------------
if prompt := st.chat_input("কী জানতে চান? লিখুন..."):
  # ১. ইউজারের মেসেজ স্ক্রিনে ও হিস্ট্রিতে যোগ করা
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # ২. AI থেকে স্ট্রিম রিপ্লাই জেনারেট করা
  with st.chat_message("assistant"):
    try:
      # System Prompt + Chat History একত্র করা
      messages_payload = [{"role": "system", "content": system_prompt}] + [
          {"role": m["role"], "content": m["content"]}
          for m in st.session_state.messages
      ]

      # Groq API Request with Streaming
      stream = client.chat.completions.create(
          model="llama-3.3-70b-versatile",
          messages=messages_payload,
          stream=True,
      )

      # রিয়েল-টাইমে লেখা টাইপ হতে থাকবে (ChatGPT/Gemini Style)
      response = st.write_stream(stream)

      # AI এর রেসপন্স হিস্ট্রিতে সেভ করা
      st.session_state.messages.append(
          {"role": "assistant", "content": response}
      )

    except Exception as e:
      st.error(f"দুঃখিত, একটি ত্রুটি ঘটেছে: {e}")
