import streamlit as st
import pandas as pd
import requests
import json

from typing import Union

st.set_page_config(
    page_title="Grapheme to Phoneme",
    page_icon="🔊",
    layout='wide',
)
st.title("📄Matni IPA ko'rinishiga o'giring")
st.markdown("<br><br>", unsafe_allow_html=True)


col1, col2 = st.columns(2)

with col2:
    col3, col4 = st.columns(2)
    with col3:
        model = st.selectbox('Modelni tanlang', ['Epitran', 'Espeak'], index=0, help='O`zingizga mos modelni tanlang')
    with col4:
        language = st.selectbox('Tilni tanlang', ['Uzbek', 'Russian', 'English'], index=0, help='Qaysi tildan o`girishni xohlaysiz?')

st.markdown("<br>", unsafe_allow_html=True)

raw_input_tab, file_upload_tab = st.tabs(['Matnni qo`lda kiritish', 'Fayldan yuklash'])

# element = st.empty()
with raw_input_tab:
    txt = st.text_area('Matnni kiritishingiz uchun joy', height=200, help='Matnni qo`lda kiriting')
    st.write(f'Belgilar soni:{len(txt)}')

with file_upload_tab:
    uploaded_file = st.file_uploader("Faylni yuklang", type=['txt', 'docx', 'pdf'], help='Matn faylini yuklang')

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
            gap: 0;
    }
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:1.1rem;
    }
    
    .stTabs [data-baseweb="tab-list"] button {  
        background-color: #f0f2f6;
        padding: 10px;
        border-right: 1px solid #d9d9d9;
        
    }
</style>
""", unsafe_allow_html=True)       
        