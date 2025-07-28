# extractor/text_cleaner.py
import re

def clean_text(text):
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r'\b([A-Z])\s+([a-z]+)\b', r'\1\2', text)
    text = re.sub(r'\b([A-Z]+)\s+([A-Z]+)\b', r'\1\2', text)
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    return text.strip()
