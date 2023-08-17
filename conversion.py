from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import requests
from bs4 import BeautifulSoup

def convert_gurmukhi_to_devanagari(text):
    return transliterate(text, sanscript.GURMUKHI, sanscript.DEVANAGARI)

def extract_text_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_text = soup.get_text()
        return extracted_text
    else:
        return None

# Provide the Punjabi URL here
punjabi_url = "https://punjabistories.com/punjabi-kahaniyan/%e0%a8%a6%e0%a8%be%e0%a8%a8-%e0%a8%a6%e0%a9%80-%e0%a8%ae%e0%a8%b9%e0%a8%bf%e0%a8%ae%e0%a8%be-mahatma-budh-di-kahani/"
extracted_text = extract_text_from_url(punjabi_url)

if extracted_text:
    devanagari_text = convert_gurmukhi_to_devanagari(extracted_text)
    print("Converted Text from URL:")
    print(devanagari_text)
else:
    print("Failed to fetch URL or extract text.")
