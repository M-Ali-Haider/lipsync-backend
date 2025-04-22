import os
from django.conf import settings
from google.oauth2 import service_account
from moviepy.editor import VideoFileClip
from google.cloud import translate_v2 as translate

class TranslationService:
    def __init__(self, credentials_path):
        """
        Initialize Google Cloud Translation service with explicit credentials
        Args:
            credentials_path (str): Path to the service account JSON key file
        """

        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/cloud-translation']
            )
            self.client = translate.Client(credentials=credentials)
        else:
            self.client = translate.Client()

    def translate_text(self, text, target_language='ur', source_language='en'):
        """
        Translate text using Google Cloud Translation API

        Args:
            text (str): Text to translate
            target_language (str): Target language code (default: Urdu)
            source_language (str): Source language code (default: English)

        Returns:
            str: Translated text
        """
        try:
            result = self.client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            return result['translatedText']
        except Exception as e:
            print(f"Translation error: {e}")
            return text


def translate_transcript(transcription_text, 
                        #  output_file, 
                         credentials_path=None
    ):
    """
    Translate a transcript file to Urdu

    Args:
        input_file (str): Path to input transcript file
        output_file (str): Path to output translated transcript file
        credentials_path (str): Optional path to service account JSON key file
    """
    translator = TranslationService(credentials_path)

    # try:
    #     with open(input_file, 'r', encoding='utf-8') as f:
    #         transcript = f.read()
    # except FileNotFoundError:
    #     print(f"Input file {input_file} not found.")
    #     return

    translated_transcript = translator.translate_text(transcription_text)
    return translated_transcript


def translation(transcription_text,video_path):
    CREDENTIALS_PATH = os.path.join(settings.BASE_DIR,'config','fyp-translation-343ed05af2bb.json') 


    # Get directory where video is stored
    video_dir = os.path.dirname(video_path)
    # Make an 'outputs' folder next to it
    output_dir = os.path.join(video_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    # Define file paths
    # urdu_txt_output_path = os.path.join(output_dir, "urdu_transcript_text_only.txt")
   
    urdu_text = translate_transcript(
        transcription_text=transcription_text,
        # output_file=urdu_txt_output_path,
        credentials_path=CREDENTIALS_PATH
    )
    return urdu_text
