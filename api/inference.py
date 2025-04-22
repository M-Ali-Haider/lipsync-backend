from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import soundfile as sf
# from moviepy.editor import VideoFileClip
import torch
import torchaudio
import numpy as np
import soundfile as sf
from tqdm import tqdm
from pydub import AudioSegment
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

device = "cuda:0" if torch.cuda.is_available() else "cpu"


# extract .wav audio file from original video file

# def mp4_to_wav(mp4_path, wav_path):
#     try:
#         video = VideoFileClip(mp4_path)
#         audio = video.audio
#         audio.write_audiofile(wav_path)
#         print(f"Conversion complete: {wav_path}")
#     except Exception as e:
#         print(f"Error: {e}")

# mp4_file = r"..\..\API Scripts\content\fyp_storage\video.mp4"
# wav_file = r"..\..\API Scripts\content\fyp_storage\original_audio.wav"
# mp4_to_wav(mp4_file, wav_file)


# Load model, config and vocab files

# Model paths
xtts_checkpoint = "model.pth"
xtts_config = "config.json"
xtts_vocab = "vocab.json"

# Load model
config = XttsConfig()
config.load_json(xtts_config)
XTTS_MODEL = Xtts.init_from_config(config)
XTTS_MODEL.load_checkpoint(config, checkpoint_path=xtts_checkpoint, vocab_path=xtts_vocab, use_deepspeed=False)
XTTS_MODEL.to(device)

print("Model loaded successfully!")

audio = AudioSegment.from_file(r"..\..\API Scripts\content\fyp_storage\original_audio.wav",
                               format="wav")
audio.export(r"..\..\API Scripts\content\fyp_storage\original_audio.wav",
             format="wav")
print("Speaker reference audio converted to output_audio.wav")

gpt_cond_latent, speaker_embedding = XTTS_MODEL.get_conditioning_latents(
    audio_path=[r"..\..\API Scripts\content\fyp_storage\original_audio.wav"],
    gpt_cond_len=XTTS_MODEL.config.gpt_cond_len,
    max_ref_length=XTTS_MODEL.config.max_ref_len,
    sound_norm_refs=XTTS_MODEL.config.sound_norm_refs,
)

# Function to split text into ≤150-character chunks without breaking words
def split_text(text, max_length=150):
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += (" " if current_chunk else "") + word
        else:
            chunks.append(current_chunk)
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

# Load and split input text
with open(r"..\..\API Scripts\content\fyp_storage\transcript_urdu.txt", "r", encoding="utf-8") as file:
    full_text = file.read().strip()

text_chunks = split_text(full_text)
print(f"Total chunks: {len(text_chunks)}")

# Generate and collect audio chunks
audio_outputs = []

for i, chunk in enumerate(tqdm(text_chunks, desc="Synthesizing")):
    print(f"Chunk {i+1}: {chunk}")
    wav_chunk = XTTS_MODEL.inference(
        text=chunk,
        language="ur",
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
        temperature=0.1,
        length_penalty=0.1,
        repetition_penalty=10.0,
        top_k=10,
        top_p=0.3,
    )
    audio_outputs.append(wav_chunk["wav"])

# Combine all audio chunks
final_audio = np.concatenate(audio_outputs)

# Save final audio
output_path = r"..\..\API Scripts\content\fyp_storage\final_audio.wav"
sf.write(output_path, final_audio, samplerate=24000)
print(f"Final TTS output saved as: {output_path}")