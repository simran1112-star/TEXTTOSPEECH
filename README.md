# Text-to-Speech Conversion for Indian Regional Languages

## Overview

This project is a web application that empowers users to convert text content from various Indian regional languages into speech. It integrates Amazon Polly for text-to-speech synthesis, Beautiful Soup for web scraping, Indic Transliteration for script conversion, and langid for language detection.

**Project Author:** Simran Arora

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Project Structure](#project-structure)
- [Acknowledgments](#acknowledgments)
- [Changelog](#changelog)

## Installation

To set up and run this project locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone <[TEXTTOSPEECH](https://github.com/simran1112-star/TEXTTOSPEECH)>
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - On Linux/macOS:

     ```bash
     source venv/bin/activate
     ```

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

4. **Install project dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure AWS credentials:**

   - Create an AWS account and configure your credentials using AWS CLI or environment variables. This is required to access the Polly service.

## Usage

Follow these steps to utilize the Text-to-Speech Conversion Tool:

1. **Run the application:**

   ```bash
   python app.py
   ```

2. **Open your web browser and navigate to `http://localhost:5000`.**

3. **Choose the input option:**

   - **Convert URL:** Enter a URL to fetch text content from a webpage.
   - **Convert Text:** Enter text directly.

4. **Customize the display option (applies to URL input):**

   - **Main Content Only:** Extract and convert the main content of the webpage.
   - **Entire Page:** Convert the entire webpage content.

5. **Submit the form to initiate the conversion.**

6. **Review the conversion result, including Devanagari script text and an audio player.**

## Configuration

Ensure the following configurations are set up:

- **AWS Credentials:** Configure your AWS credentials to enable access to the Polly service.

## Dependencies

This project relies on the following Python libraries:

- Flask: Web application framework.
- boto3: AWS SDK for Python.
- beautifulsoup4: HTML parsing and web scraping.
- indic-transliteration: For script conversion.
- langid: Language detection library.
## Documentation for More Reference:

- [Langid](https://pypi.org/project/langdetect/): Language detection library.
- [Flask](https://flask.palletsprojects.com/en/2.3.x/): Web application framework.
- [Indic-transliteration](https://indic-transliteration.readthedocs.io/en/latest/): Script transliteration library.
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html): AWS SDK for Python.
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): HTML parsing and web scraping.
- [Amazon Polly Services](https://docs.aws.amazon.com/polly/latest/dg/what-is.html): AWS Polly text-to-speech documentation.

## Project Structure

The project is structured as follows:

- **app.py:** Main Flask application.
- **templates/:** Contains HTML templates for the web interface.
- **static/:** Includes static files like CSS and JavaScript.

## Acknowledgments

We extend our gratitude to the creators of Flask, AWS Polly, Beautiful Soup, Indic Transliteration, and langid for their valuable libraries and contributions.

## Changelog

**Version 1.0 (September 2023):**
- Initial release of the text-to-speech conversion project.
- Supports URL and Text input options.
- Provides conversion for various Indian regional languages.
- Integrates with AWS Polly for speech synthesis.


---
13. **Contact Information:**
   - Simran Arora
   - Email: khushisimranarora@gmail.com
   - GitHub: [simran1112-star](https://github.com/simran1112-star)
