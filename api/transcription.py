import requests
import os
import time
import json

def upload_file(api_key, file_path):
    upload_endpoint = "https://api.assemblyai.com/v2/upload"
    headers = {
        "authorization": api_key
    }

    with open(file_path, "rb") as f:
        response = requests.post(upload_endpoint, headers=headers, data=f)

    if response.status_code == 200:
        return response.json()['upload_url']
    else:
        raise Exception(f"Upload failed: {response.text}")

def transcribe_audio(api_key, audio_url):
    transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }

    data = {
        "audio_url": audio_url,
        "speaker_labels": True
    }

    response = requests.post(transcript_endpoint, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()['id']
    else:
        raise Exception(f"Transcription request failed: {response.text}")

def check_transcription_result(api_key, transcript_id):
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {
        "authorization": api_key
    }

    while True:
        response = requests.get(endpoint, headers=headers)
        result = response.json()

        if result['status'] == 'completed':
            return result
        elif result['status'] == 'error':
            raise Exception(f"Transcription failed: {result}")

        time.sleep(3)

def format_transcript(transcription_result):
    """
    Return plain transcript text (no speaker labels)
    """
    return ' '.join([utt.get('text', '') for utt in transcription_result.get('utterances', [])])

def transcribe_video(api_key, video_path, output_json=False,json_output_path=None):
    try:
        upload_url = upload_file(api_key, video_path)
        transcript_id = transcribe_audio(api_key, upload_url)
        transcription_result = check_transcription_result(api_key, transcript_id)
        formatted_transcript = format_transcript(transcription_result)

        if output_json and json_output_path:
            with open(json_output_path, 'w') as f:
                json.dump(transcription_result, f, indent=2)

        return formatted_transcript, transcription_result

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None



def transcription(video_path):
    API_KEY = "41542c3055da4775a9de3eab6ae4da55"

    # Get directory where video is stored
    video_dir = os.path.dirname(video_path)

    # Make an 'outputs' folder next to it
    output_dir = os.path.join(video_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    # Define file paths
    json_output_path = os.path.join(output_dir, "transcription_result.json")
    txt_output_path = os.path.join(output_dir, "transcript_text_only.txt")

    formatted_transcript, full_result = transcribe_video(
        API_KEY, video_path, output_json=True,json_output_path=json_output_path
    )    
    return formatted_transcript, full_result, txt_output_path

