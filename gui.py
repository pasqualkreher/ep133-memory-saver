import tkinter as tk
from tkinter import ttk, filedialog as fd, Listbox
from modules.converter import convert
import os

# Root window
root = tk.Tk()
root.title('EP-133 Memory Saver')
root.resizable(True, True)
root.minsize(width=715, height=270)  


FILE_PATHS = []
output_folder = tk.StringVar()

def open_text_file():
    filetypes = (('WAV files', '*.wav'),)
    selected_files = fd.askopenfiles(filetypes=filetypes)
    
    for file in selected_files:
        file_path = file.name
        FILE_PATHS.append(file_path)
        files.insert(tk.END, os.path.basename(file_path))
        file.close() 

def select_output_folder():
    folder = fd.askdirectory()
    if folder:
        output_folder.set(folder)
        output_label.config(text=f"Output: {folder}")

def run_conversion():
    if not FILE_PATHS:
        print("No files selected.")
        return
    if not output_folder.get():
        print("No output folder selected.")
        return

    channel_value = 1 if channel_dropdown.get() == 'Mono' else 2
    bit_value = 1 if bit_dropdown.get() == '8bit' else 2  # sample_width: 1 = 8-bit, 2 = 16-bit
    sample_rate = int(sample_rate_dropdown.get())

    convert(FILE_PATHS, channels=channel_value, target_sample_rate=sample_rate, sample_width=bit_value, output_dir=output_folder.get())

def clear_files():
    FILE_PATHS.clear()
    files.delete(0, tk.END)


# UI Elements
# Frame to hold listbox and scrollbar together
file_frame = ttk.Frame(root)
file_frame.grid(column=0, row=0, rowspan=5, padx=10, pady=10, sticky='nsew')

# Scrollbar
file_scrollbar = ttk.Scrollbar(file_frame, orient='vertical')
file_scrollbar.pack(side='right', fill='y')

# Listbox with scrollbar
files = Listbox(file_frame, width=40, yscrollcommand=file_scrollbar.set)
files.pack(side='left', fill='both', expand=True)
file_scrollbar.config(command=files.yview)

open_button = ttk.Button(root, text='Open WAV Files', command=open_text_file)
open_button.grid(column=0, row=5, sticky='w', padx=(10, 5), pady=5)

clear_button = ttk.Button(root, text='Clear Files', command=clear_files)
clear_button.grid(column=0, row=5, sticky='e', padx=(5, 10), pady=5)

ttk.Label(root, text="Channels:").grid(column=1, row=0, sticky='w')
channel_dropdown = ttk.Combobox(root, values=['Mono', 'Stereo'], state='readonly')
channel_dropdown.current(0)
channel_dropdown.grid(column=2, row=0, padx=10, pady=5)

ttk.Label(root, text="Bit Depth:").grid(column=1, row=1, sticky='w')
bit_dropdown = ttk.Combobox(root, values=['8bit', '16bit'], state='readonly')
bit_dropdown.current(1)
bit_dropdown.grid(column=2, row=1, padx=10, pady=5)

ttk.Label(root, text="Sample Rate:").grid(column=1, row=2, sticky='w')
sample_rate_dropdown = ttk.Combobox(root, values=[
    '44100', '32000', '22050'
], state='readonly')
sample_rate_dropdown.current(0)
sample_rate_dropdown.grid(column=2, row=2, padx=10, pady=5)

output_label = ttk.Label(root, text="Output: (Not selected)", wraplength=200)
output_label.grid(column=1, row=3, columnspan=2, sticky='w', padx=10)

output_button = ttk.Button(root, text="Select Output Folder", command=select_output_folder)
output_button.grid(column=2, row=4, sticky='e', padx=10, pady=5)

convert_button = ttk.Button(root, text="Convert", command=run_conversion)
convert_button.grid(column=2, row=5, sticky='e', padx=10, pady=10)

root.mainloop()
