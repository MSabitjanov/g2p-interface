import json
import requests

import streamlit as st
import pandas as pd

from typing import Union

st.set_page_config(page_title="Grapheme to Phoneme", page_icon="🔊", layout="wide")
st.title("📄Matni IPA ko'rinishiga o'giring")
st.markdown("<br><br>", unsafe_allow_html=True)


def get_available_languages():
    try:
        response = requests.get("http://127.0.0.1:5000/g2p/epitran")
        if response.status_code == 200:
            return response.json().get("data")
        else:
            return response.json().get("message")
    except:
        return "Tashqi xizmat ishlashida xatolik yuz berdi"


col1, col2 = st.columns(2)

with col2:
    col3, col4 = st.columns(2)
    with col3:
        model = st.selectbox(
            "Modelni tanlang",
            ["Epitran"],
            index=0,
            help="O`zingizga mos modelni tanlang",
        )
    with col4:
        with st.spinner("Tillar yuklanmoqda..."):
            available_languages = get_available_languages()
        language = st.selectbox(
            "Tilni tanlang",
            available_languages,
            index=109,
            help="Qaysi tildan o`girishni xohlaysiz?",
        )
        st.session_state["language"] = available_languages.get(language, "")

st.markdown("<br>", unsafe_allow_html=True)

raw_input_tab, file_upload_tab = st.tabs(["Matnni qo`lda kiritish", "Fayldan yuklash"])


def draw_generate_button(key=None):
    col1, col2 = st.columns([9, 1])
    with col2:
        button = st.button(
            "IPAga o`girish",
            help="Matnni IPAga o`girish",
            use_container_width=True,
            key=key,
        )
        return button


def generate_phonemes(text):
    data = [{"text": text}]
    try:
        language = st.session_state["language"]
        response = requests.post(
            f"http://127.0.0.1:5000/g2p/epitran?lang_code={language}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
        )
        return True, response.json().get("data")[0]["phonetic_form"]
    except requests.exceptions.ConnectionError:
        return False, "Tashqi xizmat ishlashida xatolik yuz berdi"


def generate_phones_from_file(data):
    data = [{"text": text} for text in data]
    try:
        response = requests.post(
            "http://127.0.0.1:5000/g2p/epitran?lang_code=uzb-Latn",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
        )
    except requests.exceptions.ConnectionError:
        return False, "Tashqi xizmat ishlashida xatolik yuz berdi"
    if response.status_code == 200:
        try:
            converted_data = response.json().get("data")
            return True, converted_data
        except:
            return (
                False,
                "Javobni o'qishda xatolik yuz berdi yoki javobni tahlil qilishda xatolik yuz berdi",
            )
    else:
        return False, "Tashqi xizmatdan javob olishda xatolik yuz berdi"


# element = st.empty()
with raw_input_tab:
    txt = st.text_area(
        "Matnni kiritishingiz uchun joy", height=200, help="Matnni qo`lda kiriting"
    )
    st.write(f"Belgilar soni:{len(txt)}")
    button = draw_generate_button()
    if button and len(txt) > 0:
        msg = st.toast("Bajarilmoqda...", icon="♻️")
        status, phoneme_form = generate_phonemes(txt)
        if status is False:
            msg.toast(phoneme_form, icon="❌")
        msg.toast("Bajarildi!", icon="✅")
        st.markdown("## Fonetik ko`rinishi:", unsafe_allow_html=True)
        st.text_area(
            label="phonetic ko'rinishi", value=phoneme_form, label_visibility="hidden"
        )

with file_upload_tab:
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        uploaded_file = st.file_uploader(
            "CSV Faylni yuklang", type=["csv"], help="CSV faylni yuklang"
        )
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if not uploaded_file:
            button = st.button(
                "IPAga o`girish",
                help="Avval fileni yuklang",
                use_container_width=True,
                key="file_button",
                type="primary",
                disabled=True,
            )
        else:
            button = st.button(
                "IPAga o`girish",
                help="Matnni IPAga o`girish",
                use_container_width=True,
                key="file_button",
                type="primary",
            )
    if uploaded_file and button:
        msg = st.toast("Ma`lumotlar yuklanmoqda...", icon="♻️")
        df = pd.read_csv(uploaded_file, encoding="Windows-1252")
        data = df.iloc[:, 0].tolist()
        status, phoneme_form = generate_phones_from_file(data)
        if status is False:
            msg.toast(phoneme_form, icon="❌")
        df = pd.DataFrame(phoneme_form)
        st.data_editor(df, num_rows="dynamic", use_container_width=True)
        msg.toast("Bajarildi!", icon="✅")


def customize_tabs_style():
    return st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )


def main():
    customize_tabs_style()


if "__main__" == __name__:
    main()
