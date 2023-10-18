from flask import Flask, render_template, request, flash, redirect, url_for
from bs4 import BeautifulSoup
import boto3
import os
import requests
import langid
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Run this once to create the database
with app.app_context():
    print("Before create_all")
    # Create the database tables
    db.create_all()
    print("After create_all")



app.secret_key = b'b\xbb\xc5\x9c\xd6\xd85\xaf\xdd\xbf\xea\xcc\xf8\xe67\xba\r>\xdf@\xb5\x88N\xb8'
users = {}

# Add your AWS S3 configuration here
S3_BUCKET_NAME = 'tts-demo3-bucket'
S3_OBJECT_KEY = 'output_combined.mp3'
s3 = boto3.client('s3')

@app.route('/')
def login():
    # Render the login page template
    return render_template('login.html')
@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    # Perform login logic here (e.g., check credentials)
    user = User.query.filter_by(username=username).first()

    if user and user.password == password:
        flash('Login successful!', 'success')
        print("loging successfull")
        return redirect(url_for('main'))  # Redirect to the home page
    else:
        flash('Login failed. Please check your credentials.', 'error')
        return redirect(url_for('login'))  # Redirect back to the login page

@app.route('/signup')
def signup():
    
    # Render the signup page template
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    name = request.form.get('name')
    dob = request.form.get('dob')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Perform signup logic here (e.g., validate input and create user)
    if password != confirm_password:
        flash('Passwords do not match. Please try again.', 'error')
        return redirect(url_for('signup'))  # Redirect back to the signup page

    existing_user = User.query.filter_by(username=name).first()
    if existing_user:
        flash('Username already exists. Please choose a different one.', 'error')
        return redirect(url_for('signup'))  # Redirect back to the signup page

    new_user = User(username=name, email=dob, password=password)
    print("loging successfull")

    db.session.add(new_user)
    db.session.commit()

    flash('Account created successfully! You can now log in.', 'success')
    return redirect(url_for('login'))  # Redirect to the login page

@app.route('/home')
def home():
    return render_template('home.html')

# Your other routes and functions go here...
@app.route('/Aboutus')
def Aboutus():
    return render_template('Aboutus.html')
@app.route('/contact')
def Contact():
    return render_template('Contact.html')

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Create a new ContactMessage instance
        new_message = ContactMessage(name=name, email=email, message=message)

        # Add and commit the message to the existing database session
        db.session.add(new_message)
        db.session.commit()

        # Redirect to a thank-you page
        return redirect(url_for('thankyou'))
    
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')




def aws_polly_text_to_speech(text):
    aws_mag_con = boto3.session.Session(profile_name='test_user')
    client = aws_mag_con.client(service_name='polly', region_name='us-east-1')

    chunk_size = 2000
    i = 0
    audio_chunks = []  

    while i < len(text):
        chunk = text[i:i + chunk_size]
        ssml = '<speak>' + chunk.replace(".", "<break time='1s'/>").replace("।", "<break time='1s'/>").replace("•", "<break time='0.5s'/>").replace(",", "<break time='0.5s'/>").replace(":", "<break time='0.5s'/>") + '</speak>'

        response = client.synthesize_speech(
            VoiceId='Aditi',
            OutputFormat='mp3',
            TextType="ssml",  
            Text=ssml  
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

def add_spaces_and_pauses(content):
    soup = BeautifulSoup(content, 'html.parser')

    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        heading.insert_before(BeautifulSoup('<emphasis level="strong">', 'html.parser'))
        heading.insert_after(BeautifulSoup('</emphasis>', 'html.parser'))
        
    for strong_tag in soup.find_all(['strong', 'b']):
        strong_tag.insert_before(BeautifulSoup('<emphasis level="strong">', 'html.parser'))
        strong_tag.insert_after(BeautifulSoup('</emphasis>', 'html.parser'))

    for span_tag in soup.find_all('span'):
        span_tag.insert_before(BeautifulSoup('<emphasis level="strong">', 'html.parser'))
        span_tag.insert_after(BeautifulSoup('</emphasis>', 'html.parser'))

    for text in soup.find_all(['p', 'div', 'span']):
        text.insert_before(BeautifulSoup('<prosody rate="slow">', 'html.parser'))
        text.insert_after(BeautifulSoup('</prosody>', 'html.parser'))

    for numerical_tag in soup.find_all(['p', 'div', 'span'], text=True):
        if any(char.isdigit() for char in numerical_tag.get_text()):
            numerical_tag.insert_before(BeautifulSoup('<prosody rate="slow">', 'html.parser'))
            numerical_tag.insert_after(BeautifulSoup('</prosody>', 'html.parser'))

    modified_content = str(soup)

    return modified_content

def skip_media_sections(content):
    soup = BeautifulSoup(content, 'html.parser')

    media_tags = ['img', 'video', 'audio','vdo']

    for tag in media_tags:
        for media_tag in soup.find_all(tag):
            media_tag.extract()  
            
    for id_tag in soup.find_all(id="parentDiv0"):
        id_tag.extract() 

    modified_content = str(soup)

    return modified_content


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

@app.route('/main')
def main():
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
            html_content = skip_media_sections(html_content)

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

            content_to_convert_with_spaces_and_pauses = add_spaces_and_pauses(content_to_convert)
            

            if detected_lang in {'bn', 'pa', 'gu', 'ta'}:
                if detected_lang == 'bn':
                    devanagari_text = convert_bengali_to_devanagari(content_to_convert_with_spaces_and_pauses)
                elif detected_lang == 'pa':
                    devanagari_text = convert_gurmukhi_to_devanagari(content_to_convert_with_spaces_and_pauses)
                elif detected_lang == 'gu':
                    devanagari_text = convert_gujarati_to_devanagari(content_to_convert_with_spaces_and_pauses)
                elif detected_lang == 'ta':
                    devanagari_text = convert_tamil_to_devanagari(content_to_convert_with_spaces_and_pauses)

                aws_polly_text_to_speech(content_to_convert_with_spaces_and_pauses)

                audio_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{S3_OBJECT_KEY}"

                return render_template('result.html', devanagari_text=devanagari_text, audio_url=audio_url)

            else:
                aws_polly_text_to_speech(content_to_convert_with_spaces_and_pauses)

                audio_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{S3_OBJECT_KEY}"

                return render_template('result.html', devanagari_text=content_to_convert_with_spaces_and_pauses, audio_url=audio_url)

        except requests.exceptions.RequestException as e:
            return f"<h2>Error</h2><p>Failed to fetch URL: {e}"

    # ...

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

# ...

if __name__ == '__main__':
    app.run(debug=True)
