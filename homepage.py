import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(
    page_title="Grapheme to Phoneme",
    page_icon="🔊",
    layout='wide',
)
st.title("📄Matni IPA ko'rinishiga o'giring")
st.markdown("<br><br>", unsafe_allow_html=True)



col1, col2 = st.columns([0.8, 0.2])
with col1:
    uploaded_file = st.file_uploader("Faylni tanlang", type="csv", help="Faylni tanlang va uni yuklang")

with col2:
    st.selectbox("Tilni tanlang", ['English', 'Uzbek', 'Russian'], index=1)
    if st.button("Generate Phonemes", use_container_width=True, type='primary'):
        msg = st.toast("Generating Phonemes...",)
        edited_data = st.session_state['edited_data']
        original_text_data = [{'text': text} for text in edited_data['Original Text']]
        response = requests.post('http://127.0.0.1:5000/g2p/epitran?lang_code=uzb-Latn', data=json.dumps(original_text_data), headers={'Content-Type': 'application/json'})
        phonetic_data = [item['phonetic_form'] for item in response.json().get('data')]
        edited_data['Phonetic Form'] = phonetic_data
        st.data_editor(edited_data, num_rows="dynamic")
        msg.toast("Phonemes generated successfully!", icon="✅")

df = pd.DataFrame(columns=("Original so'z yoki matn", "Fonetik ko'rinishi"))
data_table = st.data_editor(df, num_rows='dynamic', use_container_width=True, key='input_table')
print(data_table)
    
if uploaded_file is not None:
    msg = st.toast('Yuklanmoqda...',)
    df = pd.read_csv(uploaded_file, encoding="Windows-1252")
    edited_data = st.data_editor(df, num_rows= "dynamic")
    st.session_state['edited_data'] = edited_data
    msg.toast('Yuklandi!', icon="✅")
