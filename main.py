import os
import requests
from pydub import AudioSegment

# ฟังก์ชันที่ใช้แบ่งไฟล์เสียง
def split_audio(input_file, chunk_length_ms=2000000, output_folder="chunks"):
    # ตรวจสอบว่า folder สำหรับเก็บไฟล์ chunk มีหรือไม่ ถ้าไม่มีก็สร้าง
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    audio = AudioSegment.from_mp3(input_file)
    audio = audio.set_channels(1).set_frame_rate(16000)  # เปลี่ยนเป็น Mono และ 16kHz
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]  # แบ่งเสียงเป็นชิ้นๆ

    # สร้างไฟล์ .wav สำหรับแต่ละชิ้นและเก็บไว้ใน subfolder
    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_filename = os.path.join(output_folder, f"chunk_{i}.wav")
        chunk.export(chunk_filename, format="wav")
        chunk_files.append(chunk_filename)

    return chunk_files


# ฟังก์ชันสำหรับส่งไฟล์เสียงไปยัง Wit.ai
def send_to_wit(file_path):
    url = "https://api.wit.ai/speech"
    headers = {
        "Authorization": "Bearer FIFTUUEZJSN246KVJCQDTZDDXR4GIQ2V",
        "Content-Type": "audio/wav"
    }

    try:
        with open(file_path, "rb") as audio_file:
            response = requests.post(url, headers=headers, data=audio_file)
            return response
    except Exception as e:
        print(f"Error: {e}")
        return None


# ฟังก์ชันที่ใช้สร้างไฟล์ .txt ที่เก็บข้อความทั้งหมด
def save_transcription_to_file(text_data, filename="transcription.txt"):
    # สำหรับการสร้างไฟล์ .txt
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text_data)


# ฟังก์ชันหลักที่รวมทุกอย่างเข้าด้วยกัน
def process_audio(input_file):
    chunk_files = split_audio(input_file)
    full_transcription = ""

    # ส่งแต่ละไฟล์เสียงไปยัง Wit.ai ทีละไฟล์
    for chunk_file in chunk_files:
        print(f"Sending {chunk_file} to Wit.ai...")
        response = send_to_wit(chunk_file)

        if response:
            # ตรวจสอบว่าการตอบกลับเป็น JSON หรือไม่
            try:
                result = response.json()
                text = result.get("text", "")
                if text:
                    full_transcription += text + "\n"  # รวมข้อความทั้งหมด
            except ValueError as e:
                print(f"Error decoding JSON from response: {e}")
                print(f"Response Text: {response.text}")
        else:
            print(f"Error with {chunk_file}: No response from Wit.ai")

        os.remove(chunk_file)  # ลบไฟล์ชิ้นส่วนหลังจากการส่งเรียบร้อย

    # บันทึกข้อความทั้งหมดในไฟล์
    if full_transcription:
        save_transcription_to_file(full_transcription, "transcription.txt")


# เริ่มการประมวลผล
input_audio_file = "input.mp3"  # ชื่อไฟล์เสียงที่ต้องการแปลง
process_audio(input_audio_file)
