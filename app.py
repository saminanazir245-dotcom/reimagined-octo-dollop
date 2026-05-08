import streamlit as st
import google.generativeai as genai
import json
import os
from typing import List, Dict

# Page Configuration
st.set_page_config(
    page_title="Etsy Art Architect",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Gemini
def init_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Please set GEMINI_API_KEY in your Streamlit Secrets or Environment Variables.")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash-latest')

model = init_gemini()

# CSS for Sleek Theme
st.markdown("""
<style>
    .stApp {
        background-color: #F9F8F6;
    }
    .main {
        color: #2D2A26;
    }
    .stButton>button {
        border-radius: 50px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        background-color: #1A1C19 !important;
        color: white !important;
        border: none;
        padding: 0.5rem 2rem;
    }
    .stTextInput>div>div>input {
        border-radius: 25px;
    }
    .card {
        background-color: white;
        padding: 2rem;
        border-radius: 25px;
        border: 1px solid #E5E3DF;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 10px;
        text-transform: uppercase;
        font-weight: bold;
        background-color: #F0EEEA;
        color: #8B7E66;
        margin-bottom: 10px;
    }
    .palette-dot {
        height: 12px;
        width: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 4px;
        border: 1px solid rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Helper for parsing JSON
def robust_json_load(text):
    try:
        # Clean potential markdown code blocks
        clean_text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        st.error(f"Failed to parse AI response: {e}")
        st.code(text)
        return None

# Sidebar Navigation Summary
with st.sidebar:
    st.title("🎨 Art Architect")
    st.markdown("---")
    if 'stage' not in st.session_state:
        st.session_state.stage = 1
    
    st.markdown(f"**Current Stage:** {st.session_state.stage}/3")
    
    if st.button("Reset Session", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- STAGE 1: NICHE IDEATION ---
if st.session_state.stage == 1:
    st.title("Stage 1: Niche Generation")
    st.markdown("Enter a theme or aesthetic to generate 10 high-potential Etsy wall art ideas.")
    
    theme = st.text_input("Theme / Niche", placeholder="e.g. Sage Green Japandi, Mid-Century Modern Abstract...")
    
    if st.button("Generate Ideas") and theme:
        with st.spinner("Analyzing Etsy trends..."):
            prompt = f"""
            Generate 10 HIGH-POTENTIAL Etsy wall art ideas for the theme: {theme}.
            Focus on minimalist luxury, modern home decor, and commercial viability.
            Return ONLY a JSON array of objects with keys: 
            "id", "title", "style", "palette" (array of hex strings), "targetBuyer", "bestFor", "whySells".
            """
            response = model.generate_content(prompt)
            st.session_state.ideas = robust_json_load(response.text)
            
    if 'ideas' in st.session_state and st.session_state.ideas:
        st.markdown("### Select an Idea to Refine")
        for idea in st.session_state.ideas:
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div class="badge">Idea: {idea.get('id', '??')}</div>
                    <h3 style="margin-top:0">{idea.get('title')}</h3>
                    <p style="font-size: 14px; color: #5C5851;">{idea.get('whySells')}</p>
                    <div style="margin-bottom: 15px">
                        {" ".join([f'<span class="palette-dot" style="background-color:{c}"></span>' for c in idea.get('palette', [])])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Refine: {idea.get('title')}", key=f"btn_{idea.get('id')}"):
                    st.session_state.selected_idea = idea
                    st.session_state.stage = 2
                    st.rerun()

# --- STAGE 2: VARIATIONS ---
elif st.session_state.stage == 2:
    st.title("Stage 2: Visual Variations")
    st.markdown(f"Generating unique artistic directions for: **{st.session_state.selected_idea['title']}**")
    
    if 'variations' not in st.session_state:
        with st.spinner("Designing variations..."):
            idea = st.session_state.selected_idea
            prompt = f"""
            Generate 4 UNIQUE visual variations for: {idea['title']} - {idea['whySells']}.
            Return ONLY a JSON array of objects with keys:
            "id", "styleDirection", "mood", "palette" (array), "composition", "texture", "aiPrompt".
            Prompts must be highly descriptive and aesthetic.
            """
            response = model.generate_content(prompt)
            st.session_state.variations = robust_json_load(response.text)

    if 'variations' in st.session_state and st.session_state.variations:
        cols = st.columns(2)
        for i, v in enumerate(st.session_state.variations):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="card" style="height: 100%;">
                    <div class="badge">Variation #0{i+1}</div>
                    <h4 style="font-family: serif; font-style: italic;">{v.get('styleDirection')}</h4>
                    <p style="font-size: 11px; opacity: 0.7;">Mood: {v.get('mood')}</p>
                    <p style="font-size: 11px; font-style: italic;">"{v.get('aiPrompt')}"</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Build Asset: {v.get('styleDirection')}", key=f"v_btn_{v.get('id')}"):
                    st.session_state.selected_variation = v
                    st.session_state.stage = 3
                    st.rerun()
    
    if st.button("← Back to Ideas"):
        st.session_state.stage = 1
        st.rerun()

# --- STAGE 3: SEO & PREP ---
elif st.session_state.stage == 3:
    st.title("Stage 3: Production & SEO")
    v = st.session_state.selected_variation
    idea = st.session_state.selected_idea
    
    with st.expander("🚀 Master Generation Prompts", expanded=True):
        st.markdown("### Master AI Prompt")
        st.code(v['aiPrompt'], language="text")
        st.markdown("### Negative Prompt")
        st.code("watermark, blurry, distorted text, low quality, messy composition, oversaturated", language="text")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏷️ Etsy SEO Listing")
        if 'seo' not in st.session_state:
            with st.spinner("Optimizing SEO..."):
                prompt = f"""
                Generate Etsy SEO for: {idea['title']} - {v['styleDirection']}.
                Return JSON: {{"title": "...", "description": "...", "tags": ["..."], "socialCaption": "..."}}
                """
                response = model.generate_content(prompt)
                st.session_state.seo = robust_json_load(response.text)
        
        seo = st.session_state.seo
        if seo:
            st.text_input("Optimized Title", value=seo.get('title'))
            st.text_area("Product Description", value=seo.get('description'), height=200)
            st.multiselect("Keywords (13 Tags)", options=seo.get('tags', []), default=seo.get('tags', []))

    with col2:
        st.markdown("### 🖼️ Realistic Mockup Prompts")
        if 'mockups' not in st.session_state:
            with st.spinner("Visualizing scenes..."):
                prompt = f"""
                Generate 4 mockup prompts for: {v['styleDirection']}.
                Return JSON list of objects: {{"scene": "...", "prompt": "..."}}
                """
                response = model.generate_content(prompt)
                st.session_state.mockups = robust_json_load(response.text)
        
        if st.session_state.mockups:
            for m in st.session_state.mockups:
                st.info(f"**{m['scene']}**\n\nPrompt: `{m['prompt']}`")

    if st.button("← Back to Variations"):
        st.session_state.stage = 2
        st.rerun()
