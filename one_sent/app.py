import streamlit as st
import ebooklib
from ebooklib import epub
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
import re

from pdfminer.high_level import extract_text

import nltk
nltk.download('punkt')
st.set_page_config(layout="wide")


class Summarizer:
    def __init__(self, file_path, file_type):
        self.file_path = file_path
        self.file_type = file_type
        self.text = self.extract_text()

    def extract_text(self):
        if self.file_type == 'txt':
            return self.get_txt_text(self.file_path)
        elif self.file_type == 'epub':
            return self.get_epub_text(self.file_path)
        elif self.file_type == 'pdf':
            return self.get_pdf_text(self.file_path)
        return ""

    def get_txt_text(self, file_path):
        return file_path.read().decode('utf-8')

    def get_epub_text(self, file_path):
        text = []
        book = epub.read_epub(file_path)
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                text.append(item.get_content().decode('utf-8'))
        return self.clean_text(''.join(text))

    def get_pdf_text(self,file_path):
        text = extract_text(file_path)
        return self.clean_text(text)
    
    def summarize(self):
        if not self.text:
            return "No text to summarize."

        tokenizer = Tokenizer('english')
        parser = PlaintextParser.from_string(self.text, tokenizer)
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, 1)
        return ' '.join([str(sentence) for sentence in summary])
    def clean_text(self, text):
        text = re.sub(r'-\s*\n\s*', '', text)
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
        text = re.sub(r'(?<=[a-z])(?=[a-zA-Z][A-Z])', ' ', text)  # Split when lowercase is followed by uppercase
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Add space between lowercase and uppercase
        text = re.sub(r'\s+', ' ', text)
        return text.strip()




if __name__ == '__main__':
    st.title('Most Important Sentence from a Book/Text')

    uploaded_file = st.file_uploader('Upload a file', type=['txt', 'pdf', 'epub'], key='file_uploader')

    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1]
        summarizer = Summarizer(uploaded_file, file_type)

        #st.text_area('Extracted Text', summarizer.text, height=300)

        #if st.button('Summarize', key='summarize_button'):
        summary = summarizer.summarize()
        st.write(summary)
