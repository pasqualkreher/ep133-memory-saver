# ep133-memory-saver
A simple tool to convert audio files to save memory for the EP-133
![screenshot](https://github.com/eamiralian/ep133-memory-saver/blob/main/screenshot.png "screenshot")

# Use
1. Download and run the exe file from releases, or build it yourself
2. Use `Select WAV Directory` to select a folder with WAV files, or use `Add WAV Files` to add individual files
3. Use `Select Output Directory` to select a folder to save the converted files to
4. Use `Convert` to start processing files, the converted files will be saved in the output folder

# Building
1. Clone repo
2. Create venv
3. Install requirements from requirements.txt
4. Run in terminal: python -m PyInstaller gui.py --onefile --windowed
You will find a dist folder in cloned repo from there you can execute the gui file to convert audio data