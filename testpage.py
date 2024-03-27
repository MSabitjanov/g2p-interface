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

SHOW_INPUT_TABLE = True
SHOW_GENERATED_TABLE = False

def update_session_state(key, data):
    st.session_state[key] = data

def get_prepared_data():
    # Prepares data for submission to external service. 
    # Refer to service documentation for example format
    data_table = st.session_state['data_table']
    first_column_name = data_table.columns[0]
    first_column_data = data_table[first_column_name].values
    prepared_data = [{'text': text} for text in first_column_data]
    return prepared_data

def get_converted_data(data) -> tuple[bool, Union[str, list]]:
    # Making request 
    try:    
        response = requests.post(
            'http://127.0.0.1:5000/g2p/epitran?lang_code=uzb-Latn', 
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data))
    except requests.exceptions.ConnectionError:
        return False, "Tashqi xizmat ishlashida xatolik yuz berdi"
    if response.status_code == 200:
        try:
            converted_data = [obj['phonetic_form'] for obj in response.json().get('data')]
            return True, converted_data
        except:
            return False, "Javobni o'qishda xatolik yuz berdi yoki javobni tahlil qilishda xatolik yuz berdi"
    else:
        return False, "Tashqi xizmatdan javob olishda xatolik yuz berdi"

def generate_phonemes() -> bool:
    # Gets data_table from session and generates phoneme for each row
    msg = st.toast('Bajarilmoqda...', icon='♻️')
    prepared_data = get_prepared_data()
    status, data = get_converted_data(prepared_data)
    if status is False:
        msg.toast(data, icon='❌')
        return False

    # # appending as result to second columnt to our existing table
    data_table = st.session_state['data_table']
    second_column_name = data_table.columns[1]
    data_table[second_column_name] = data
    update_session_state(data_table, 'data_table')
    global SHOW_INPUT_TABLE
    SHOW_INPUT_TABLE = False
    global SHOW_GENERATED_TABLE
    SHOW_GENERATED_TABLE = True
    msg.toast('Fonemalr generatsiyasi tayyor', icon='✅')
    return True
    

col1, col2 = st.columns([0.8, 0.2])
with col1:
    uploaded_file = st.file_uploader("Faylni tanlang", type="csv", help="Faylni tanlang va uni yuklang")

with col2:
    st.selectbox("Tilni tanlang", ['English', 'Uzbek', 'Russian'], index=1)
    if st.button("Generate Phonemes", use_container_width=True, type='primary'):
        status = generate_phonemes()
        if status is True:
            ...
            
df = pd.DataFrame(columns=("Original so'z yoki matn", "Fonetik ko`rinishi"))
if SHOW_INPUT_TABLE:
    data_table = st.data_editor(df, num_rows='dynamic', use_container_width=True, key='input_table')
    update_session_state('data_table', data_table)

if SHOW_GENERATED_TABLE:
    data_table = st.session_state['data_table']
    data_table = st.data_editor(data_table, num_rows='dynamic', use_container_width=True)
    st.session_state['data_table'] = data_table