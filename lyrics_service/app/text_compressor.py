# app/text_compressor.py

from keybert import KeyBERT

# один раз инициализируем
model = KeyBERT(model='all-MiniLM-L6-v2')

def extract_keywords(text: str) -> list[str]:
    keywords = model.extract_keywords(text, top_n=5)
    return [kw for kw, _ in keywords]
