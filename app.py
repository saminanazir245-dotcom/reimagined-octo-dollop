import streamlit as st
from google import genai
import os

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Etsy Art Architect",
    page_icon="🎨",
    layout="wide"
)

# ---------------------------
# GEMINI CLIENT INIT
# ---------------------------
def init_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("❌ GEMINI_API_KEY missing in Streamlit Secrets or Environment Variables.")
        st.stop()

    return genai.Client(api_key=api_key)

client = init_gemini()

# ---------------------------
# GEMINI CALL FUNCTION
# ---------------------------
def generate_text(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# ---------------------------
# UI
# ---------------------------
st.title("🎨 Etsy Wall Art AI Generator")

niche = st.text_input("Enter your Etsy wall art niche (e.g. Islamic minimalist art)")

if st.button("Generate Ideas"):

    if niche:

        prompt = f"""
You are an expert Etsy wall art researcher.

Generate 10 profitable Etsy wall art ideas for this niche:
{niche}

For each idea include:
- Title
- Style
- Color Palette
- Target Audience
- Reason it can sell on Etsy
"""

        result = generate_text(prompt)

        if result:
            st.subheader("Generated Ideas")
            st.write(result)

    else:
        st.warning("Please enter a niche first.")
