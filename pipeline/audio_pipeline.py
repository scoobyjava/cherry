import os
import asyncio
import tempfile
import requests
import sounddevice as sd
import wavio
import whisper
from cherry.agents.planning_agent import PlanningAgent

# Eleven Labs configuration (ensure ELEVEN_API_KEY is set in your environment)
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
ELEVEN_VOICE_ID = "your_voice_id"  # Replace with a valid voice id
ELEVEN_ENDPOINT = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"

def record_audio(duration=5, fs=44100):
    print("Recording audio...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wavio.write(temp_wav.name, recording, fs, sampwidth=2)
    print(f"Audio recorded to {temp_wav.name}")
    return temp_wav.name

async def transcribe_audio(audio_file):
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    transcription = result['text'].strip()
    print(f"Transcription: {transcription}")
    return transcription

async def process_instructions(transcription):
    # Process transcribed text as a planning requirement
    agent = PlanningAgent(name="PlanningAgent", description="Processes planning tasks")
    task_data = {
        "task_type": "breakdown",
        "requirements": [transcription]
    }
    result = await agent.process(task_data)
    print(f"Processing result: {result}")
    narrated_text = f"Processed task result: {result.get('task_breakdown', 'No breakdown available')}"
    return narrated_text

def narrate_output(text):
    print("Sending text to Eleven Labs for narration...")
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            # ...optional settings...
        }
    }
    response = requests.post(ELEVEN_ENDPOINT, json=payload, headers=headers)
    if response.status_code == 200:
        temp_audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        with open(temp_audio.name, "wb") as f:
            f.write(response.content)
        print(f"Narration saved to {temp_audio.name}, playing audio...")
        os.system(f"mpg123 {temp_audio.name}")
    else:
        print(f"Failed to synthesize narration: {response.status_code} {response.text}")

async def run_pipeline():
    audio_file = record_audio()
    transcription = await transcribe_audio(audio_file)
    narrated_text = await process_instructions(transcription)
    narrate_output(narrated_text)

if __name__ == '__main__':
    asyncio.run(run_pipeline())
