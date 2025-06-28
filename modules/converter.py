import os
from pydub import AudioSegment

def convert(file_paths: list, channels: int, target_sample_rate: int, sample_width: int, output_dir: str):
    if not file_paths:
        return
    for file_path in file_paths:
        file_path = os.path.abspath(file_path)
        if file_path.endswith(".wav"):
            audio = AudioSegment.from_wav(file_path)
            audio = audio.set_frame_rate(target_sample_rate)
            audio = audio.set_sample_width(sample_width)
            audio = audio.set_channels(channels)

            filename = os.path.basename(file_path)
            output_path = os.path.join(output_dir, f"converted_{filename}")
            audio.export(output_path, format="wav")
            print(f"Converted: {filename} -> {output_path}")
