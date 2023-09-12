from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import boto3
import os
import requests
import langid
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

app = Flask(__name__)

S3_BUCKET_NAME = 'tts-demo3-bucket'
S3_OBJECT_KEY = 'output_combined.mp3'

s3 = boto3.client('s3')

def extract_main_content(soup):
    main_content = (
        soup.find(class_='main-content')
        or soup.find(id='main-content')
        or soup.find(id='postContent')
        or soup.find('section')
        or soup.find('main')
    )
    return main_content.get_text() if main_content else ''

def convert_to_devanagari(text, source_lang):
    try:
        devanagari_text = transliterate(text, source_lang, sanscript.DEVANAGARI)
        return devanagari_text
    except KeyError:
        return text

def convert_gurmukhi_to_devanagari(text):
    return convert_to_devanagari(text, 'gurmukhi')

def convert_gujarati_to_devanagari(text):
    return convert_to_devanagari(text, 'gujarati')

def convert_bengali_to_devanagari(text):
    return convert_to_devanagari(text, 'bengali')

def convert_tamil_to_devanagari(text):
    return convert_to_devanagari(text, 'tamil')

def aws_polly_text_to_speech(text):
    aws_mag_con = boto3.session.Session(profile_name='test_user')
    client = aws_mag_con.client(service_name='polly', region_name='us-east-1')

    chunk_size = 2000
    i = 0
    audio_chunks = []  

    while i < len(text):
        chunk = text[i:i + chunk_size]

        response = client.synthesize_speech(
            VoiceId='Aditi',
            OutputFormat='mp3',
            Text=chunk,
            Engine='standard'
        )

        if "AudioStream" in response:
            audio_filename = f"output_chunk_{i // chunk_size}.mp3"
            with open(audio_filename, "wb") as f:
                f.write(response["AudioStream"].read())
            audio_chunks.append(audio_filename)
            print(f"Speech synthesis successful for chunk {i // chunk_size}.")
        else:
            print(f"Speech synthesis failed for chunk {i // chunk_size}.")

        i += chunk_size

    combined_audio = b""
    for filename in audio_chunks:
        with open(filename, "rb") as f:
            audio_data = f.read()
            combined_audio += audio_data

    with open("output_combined.mp3", "wb") as f:
        f.write(combined_audio)
        
        s3.upload_file("output_combined.mp3", S3_BUCKET_NAME, S3_OBJECT_KEY)

    for filename in audio_chunks:
        os.remove(filename)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    input_option = request.form.get('inputOption')
    display_option = request.form.get('displayOption')
    detected_lang = 'unknown' 

    audio_url = None
    
    if input_option == 'url':
        url_input = request.form.get('urlInput')
        try:
            r = requests.get(url_input)
            html_content = r.content

            soup = BeautifulSoup(html_content, 'html.parser')
            extracted_text = soup.get_text()

            if display_option == 'main':
                main_content = extract_main_content(soup)
                detected_lang, _ = langid.classify(main_content)
                content_to_convert = main_content
            elif display_option == 'full':
                detected_lang, _ = langid.classify(extracted_text)
                content_to_convert = extracted_text
            else:
                return "Invalid display option selected"

            if detected_lang in {'bn', 'pa', 'gu', 'ta'}:
                if detected_lang == 'bn':
                    devanagari_text = convert_bengali_to_devanagari(content_to_convert)
                elif detected_lang == 'pa':
                    devanagari_text = convert_gurmukhi_to_devanagari(content_to_convert)
                elif detected_lang == 'gu':
                    devanagari_text = convert_gujarati_to_devanagari(content_to_convert)
                elif detected_lang == 'ta':
                    devanagari_text = convert_tamil_to_devanagari(content_to_convert)

                aws_polly_text_to_speech(devanagari_text)

                audio_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{S3_OBJECT_KEY}"

                return render_template('result.html', devanagari_text=devanagari_text, audio_url=audio_url)

            else:
                aws_polly_text_to_speech(content_to_convert)

                audio_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{S3_OBJECT_KEY}"

                return render_template('result.html', devanagari_text=content_to_convert, audio_url=audio_url)

        except requests.exceptions.RequestException as e:
            return f"<h2>Error</h2><p>Failed to fetch URL: {e}"

    elif input_option == 'text':
        text_input = request.form.get('textInput')
        detected_lang, _ = langid.classify(text_input)
        devanagari_text = ""

        if detected_lang == 'bn':
            devanagari_text = convert_bengali_to_devanagari(text_input)
        elif detected_lang == 'pa':
            devanagari_text = convert_gurmukhi_to_devanagari(text_input)
        elif detected_lang == 'gu':
            devanagari_text = convert_gujarati_to_devanagari(text_input)
        elif detected_lang == 'ta':
            devanagari_text = convert_tamil_to_devanagari(text_input)
        else:
            devanagari_text = text_input

        aws_polly_text_to_speech(devanagari_text)

        audio_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{S3_OBJECT_KEY}"

        return render_template('result.html', devanagari_text=devanagari_text, audio_url=audio_url)

if __name__ == '__main__':
    app.run(debug=True)
