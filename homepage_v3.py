import json
import requests

import pandas as pd
import streamlit as st
from typing import Union, Tuple


class TextToPhonemeService:
    service_url = st.secrets["service_url"]

    @staticmethod
    def get_available_languages() -> Tuple[bool, Union[str, dict]]:
        try:
            response = requests.get(TextToPhonemeService.service_url)
            if response.status_code == 200:
                return True, response.json().get("data")
            else:
                return False, response.json().get("message")
        except json.JSONDecodeError:
            return False, "JSONni o'qishda xatolik yuz berdi"
        except:
            return False, "Tashqi xizmat ishlashida xatolik yuz berdi"

    @staticmethod
    def convert_text_to_phoneme(
        data: list,
    ) -> Tuple[bool, Union[str, requests.Response]]:
        try:
            language = st.session_state.get("language")
            response = requests.post(
                f"{TextToPhonemeService.service_url}?lang_code={language}",
                headers={"Content-Type": "application/json"},
                data=json.dumps(data),
            )
            return True, response
        except:
            return False, "Tashqi xizmat ishlashida xatolik yuz berdi"


class DrawHomePage:
    def start(self):
        self.set_page_config()
        self.draw_select_language_section()
        self.draw_tabs()

    def set_page_config(self):
        st.set_page_config(
            page_title="Grapheme to Phoneme",
            page_icon="📄",
            layout="wide",
        )
        st.title("📄Matni IPA ko'rinishiga o'giring")
        st.markdown("<br><br>", unsafe_allow_html=True)

    def draw_select_language_section(self):
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
                    status, available_languages = (
                        TextToPhonemeService.get_available_languages()
                    )
                if status is False:
                    st.error(available_languages)
                    return
                language = st.selectbox(
                    "Tilni tanlang",
                    available_languages,
                    index=109,
                    help="Qaysi tildan o`girishni xohlaysiz?",
                )
                st.session_state["language"] = available_languages.get(language, "")
        st.markdown("<br>", unsafe_allow_html=True)

    def _draw_generate_button(self, key=None):
        col1, col2 = st.columns([9, 1])
        with col2:
            button = st.button(
                "IPAga o`girish",
                help="Matnni IPAga o`girish",
                use_container_width=True,
                key=key,
            )
            return button

    def _generate_phonemes(self, text):
        data = [{"text": text}]
        status, response = TextToPhonemeService.convert_text_to_phoneme(data)
        if status is False:
            return status, response
        return status, response.json().get("data")[0].get("phonetic_form")

    def _draw_raw_text_input_tab(self, raw_input_tab):
        with raw_input_tab:
            txt = st.text_area(
                "Matnni kiritishingiz uchun joy",
                height=200,
                help="Matnni qo`lda kiriting",
            )
            st.write(f"Belgilar soni:{len(txt)}")
            button = self._draw_generate_button()
            if button and len(txt) > 0:
                msg = st.toast("Bajarilmoqda...", icon="♻️")
                status, phoneme_form = self._generate_phonemes(txt)
                if status is False:
                    msg.toast(phoneme_form, icon="❌")
                msg.toast("Bajarildi!", icon="✅")
                st.markdown("## Fonetik ko`rinishi:", unsafe_allow_html=True)
                st.text_area(
                    label="phonetic ko'rinishi",
                    value=phoneme_form,
                    label_visibility="hidden",
                )

    def _draw_file_upload_tab(self, file_upload_tab):
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
                data = [{"text": text} for text in data]
                status, phoneme_form = TextToPhonemeService.convert_text_to_phoneme(
                    data
                )
                if status is False:
                    msg.toast(phoneme_form, icon="❌")
                df = pd.DataFrame(phoneme_form.json().get("data"))
                st.data_editor(df, num_rows="dynamic", use_container_width=True)
                msg.toast("Bajarildi!", icon="✅")

    def draw_tabs(self):
        raw_input_tab, file_upload_tab = st.tabs(
            ["Matnni qo`lda kiritish", "Fayldan yuklash"]
        )
        self._draw_raw_text_input_tab(raw_input_tab)
        self._draw_file_upload_tab(file_upload_tab)


def main():
    homepage = DrawHomePage()
    homepage.start()


if __name__ == "__main__":
    main()
