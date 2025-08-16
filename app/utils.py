import re
import trafilatura
import unicodedata

def detect_url(text: str):
    """Return the first URL found in the text, or None."""
    url_pattern = re.compile(r'https?://\S+')
    match = url_pattern.search(text)
    return match.group(0) if match else None

def extract_text_from_url(url: str):
    """Download page and extract main article text."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            return trafilatura.extract(downloaded)
        return None
    except Exception as e:
        print(f"Error extracting text from {url}: {e}")
        return None

def clean_text(text):
    text = text.lower()  # Convert text to lowercase
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters and punctuation
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8') # Normalize accented characters (e.g., é -> e)
    text = re.sub(r'\s+', ' ', text).strip()  # Remove unnecessary whitespace
    return text