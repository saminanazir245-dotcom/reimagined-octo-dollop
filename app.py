import streamlit as st
import google.generativeai as genai
import os
import json

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Etsy Art Architect",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# GEMINI INITIALIZATION
# ---------------------------
def init_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error("Please set GEMINI_API_KEY in Streamlit Secrets or Environment Variables.")
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

model = init_gemini()

# ---------------------------
# GEMINI CALL FUNCTION
# ---------------------------
def generate_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# ---------------------------
# SIMPLE UI
# ---------------------------
st.title("🎨 Etsy Wall Art AI Generator")

user_input = st.text_input("Enter your niche idea (e.g. Islamic minimal wall art)")

if st.button("Generate Ideas"):
    if user_input:
        prompt = f"""
You are an Etsy Wall Art expert.

Generate 10 profitable Etsy wall art ideas for this niche:
{user_input}

For each idea include:
- Title
- Style
- Color Palette
- Target Audience
- Why it will sell on Etsy
"""
        
        result = generate_response(prompt)

        if result:
            st.subheader("Generated Ideas")
            st.write(result)
    else:
        st.warning("Please enter a niche idea.")
