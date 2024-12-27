import os
import json
import requests
from pydub import AudioSegment

# Function to split audio
def split_audio(input_file, chunk_length_ms=20000, output_folder="chunks"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    audio = AudioSegment.from_mp3(input_file)
    audio = audio.set_channels(1).set_frame_rate(16000)
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_filename = os.path.join(output_folder, f"chunk_{i}.wav")
        chunk.export(chunk_filename, format="wav")
        chunk_files.append(chunk_filename)

    return chunk_files

# Function to send audio to Wit.ai
def send_to_wit(file_path):
    url = "https://api.wit.ai/speech"
    headers = {
        "Authorization": f"Bearer FIFTUUEZJSN246KVJCQDTZDDXR4GIQ2V",
        "Content-Type": "audio/wav",
        "Accept-Language": "th"
    }

    try:
        with open(file_path, "rb") as audio_file:
            response = requests.post(url, headers=headers, data=audio_file)
            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code}")
                print(f"Response: {response.text}")
            return response
    except Exception as e:
        print(f"Error: {e}")
        return None


import json

def process_wit_response(response):
    # Split the concatenated JSON string into individual JSON objects
    response_text = response.text.strip().split('\n}\r\n{')

    # Add braces to properly format split objects
    json_objects = ['{' + obj + '}' if not obj.startswith('{') else obj for obj in response_text]

    last_object = None
    for obj in json_objects:
        try:
            parsed_obj = json.loads(obj)
            last_object = parsed_obj  # Keep updating to ensure we capture the last object
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON object: {obj}\n{e}")

    # If we found a last valid object, get its 'text' field
    full_text = last_object['text'] if last_object and 'text' in last_object else ""

    # Log the last parsed object and its text
    print("Last JSON object:")
    print(json.dumps(last_object, indent=2, ensure_ascii=False))
    print("Full Text:", full_text.strip())

    return full_text.strip()


def save_transcription_to_file(text_data, filename="transcription.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text_data)

# Main function
def process_audio(input_file):
    chunk_files = split_audio(input_file)
    full_transcription = ""

    for chunk_file in chunk_files:
        print(f"Sending {chunk_file} to Wit.ai...")
        response = send_to_wit(chunk_file)

        if response:
            text = process_wit_response(response)
            if text:
                full_transcription += text + "\n"
        else:
            print(f"Error with {chunk_file}: No response from Wit.ai")

        os.remove(chunk_file)

    if full_transcription:
        save_transcription_to_file(full_transcription, "transcription.txt")

# Start processing
input_audio_file = "input.mp3"
process_audio(input_audio_file)
