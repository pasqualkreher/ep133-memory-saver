import tkinter as tk
from tkinter import ttk, filedialog as fd, Listbox, messagebox
from modules.converter import convert
import os
import threading

# Root window
root = tk.Tk()
root.title('EP-133 Memory Saver')
root.resizable(True, True)
root.minsize(width=715, height=270)  


FILE_PATHS = []
output_folder = tk.StringVar()
use_prefix = tk.BooleanVar()
filename_prefix = tk.StringVar(value="converted_")
use_directory_structure = tk.BooleanVar()
base_directory = None  # Track the base directory for folder structure

def toggle_prefix_entry():
    """Enable/disable prefix entry based on checkbox state"""
    if use_prefix.get():
        prefix_entry.config(state='normal')
    else:
        prefix_entry.config(state='disabled')

def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def open_directory():
    global base_directory
    directory = fd.askdirectory(title="Select directory containing WAV files")
    
    if directory:
        # Clear existing files and set base directory
        FILE_PATHS.clear()
        files.delete(0, tk.END)
        base_directory = directory
        
        # Recursively find all WAV files
        for root_dir, dirs, file_list in os.walk(directory):
            for file in file_list:
                if file.lower().endswith('.wav'):
                    file_path = os.path.join(root_dir, file)
                    FILE_PATHS.append(file_path)
                    # Show relative path for better readability
                    relative_path = os.path.relpath(file_path, directory)
                    files.insert(tk.END, relative_path)

def open_individual_files():
    global base_directory
    filetypes = (('WAV files', '*.wav'),)
    selected_files = fd.askopenfiles(filetypes=filetypes)
    
    if selected_files:
        # When adding individual files, clear base directory (folder structure won't work well)
        if not FILE_PATHS:  # Only clear if this is the first selection
            base_directory = None
        
        # Don't clear existing files - allow adding to current selection
        for file in selected_files:
            file_path = file.name
            if file_path not in FILE_PATHS:  # Avoid duplicates
                FILE_PATHS.append(file_path)
                files.insert(tk.END, os.path.basename(file_path))
            file.close() 

def select_output_folder():
    folder = fd.askdirectory()
    if folder:
        output_folder.set(folder)
        output_label.config(text=f"Output: {folder}")

def progress_callback(current, total, filename):
    """Callback function to update progress from the conversion thread"""
    def update_ui():
        progress_percent = int((current / total) * 100)
        progress_bar['value'] = progress_percent
        progress_status_label.config(text=f"Processing {current}/{total}: {filename}")
        root.update_idletasks()
    
    # Use root.after to safely update UI from thread
    root.after(0, update_ui)

def run_conversion_threaded():
    """Run the conversion in a separate thread to prevent UI freezing"""
    try:
        channel_value = 1 if channel_dropdown.get() == 'Mono' else 2
        bit_value = 1 if bit_dropdown.get() == '8bit' else 2  # sample_width: 1 = 8-bit, 2 = 16-bit
        sample_rate = int(sample_rate_dropdown.get())
        
        # Get prefix settings
        prefix = filename_prefix.get() if use_prefix.get() else ""
        
        converted_files, original_size, converted_size = convert(
            FILE_PATHS, 
            channels=channel_value, 
            target_sample_rate=sample_rate, 
            sample_width=bit_value, 
            output_dir=output_folder.get(), 
            filename_prefix=prefix,
            use_folder_structure=use_directory_structure.get(),
            base_directory=base_directory,
            progress_callback=progress_callback
        )
        
        # Use root.after to safely update UI from thread
        root.after(0, conversion_complete, converted_files, original_size, converted_size)
    
    except Exception as e:
        # Use root.after to safely show error from thread
        root.after(0, conversion_error, str(e))

def conversion_complete(converted_files, original_size, converted_size):
    """Called when conversion completes successfully"""
    progress_bar.grid_remove()
    progress_status_label.grid_remove()
    convert_button.config(text="Convert", state="normal")
    
    if converted_files:
        # Calculate size change
        size_change = converted_size - original_size
        size_change_percent = ((converted_size - original_size) / original_size * 100) if original_size > 0 else 0
        
        # Format the message with size information
        original_size_str = format_file_size(original_size)
        converted_size_str = format_file_size(converted_size)
        
        if size_change >= 0:
            size_change_str = f"+{format_file_size(size_change)} (+{size_change_percent:.1f}%)"
            change_word = "increased"
        else:
            size_change_str = f"-{format_file_size(abs(size_change))} ({size_change_percent:.1f}%)"
            change_word = "reduced"
        
        message = (f"Successfully converted {len(converted_files)} files!\n\n"
                  f"Original size: {original_size_str}\n"
                  f"New size: {converted_size_str}\n"
                  f"Size {change_word}: {size_change_str}")
        
        messagebox.showinfo("Conversion Complete", message)
    else:
        messagebox.showwarning("Conversion Failed", "No files were converted. Please check your files and try again.")

def conversion_error(error_message):
    """Called when conversion encounters an error"""
    progress_bar.grid_remove()
    progress_status_label.grid_remove()
    convert_button.config(text="Convert", state="normal")
    messagebox.showerror("Conversion Error", f"An error occurred during conversion:\n{error_message}")

def run_conversion():
    if not FILE_PATHS:
        messagebox.showwarning("No Files", "No files selected.")
        return
    if not output_folder.get():
        messagebox.showwarning("No Output Directory", "No output directory selected.")
        return

    # Show progress and disable convert button
    convert_button.config(text="Converting...", state="disabled")
    progress_status_label.config(text="Starting conversion...")
    progress_status_label.grid()  # Show progress status
    progress_bar['value'] = 0  # Reset progress bar
    progress_bar.grid()  # Show progress bar
    
    # Start conversion in a separate thread
    conversion_thread = threading.Thread(target=run_conversion_threaded, daemon=True)
    conversion_thread.start()

def clear_files():
    global base_directory
    FILE_PATHS.clear()
    files.delete(0, tk.END)
    base_directory = None


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

open_button = ttk.Button(root, text='Select WAV Directory', command=open_directory)
open_button.grid(column=0, row=8, sticky='w', padx=(10, 5), pady=5)

# Add individual file selection button
open_files_button = ttk.Button(root, text='Add WAV Files', command=open_individual_files)
open_files_button.grid(column=0, row=9, sticky='w', padx=(10, 5), pady=5)

clear_button = ttk.Button(root, text='Clear Files', command=clear_files)
clear_button.grid(column=0, row=9, sticky='e', padx=(5, 10), pady=5)

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

# Filename prefix controls
prefix_checkbox = ttk.Checkbutton(root, text="Use filename prefix:", variable=use_prefix, command=toggle_prefix_entry)
prefix_checkbox.grid(column=1, row=3, sticky='w', padx=10, pady=5)

prefix_entry = ttk.Entry(root, textvariable=filename_prefix, width=15, state='disabled')
prefix_entry.grid(column=2, row=3, sticky='w', padx=10, pady=5)

# Folder structure preservation checkbox
folder_structure_checkbox = ttk.Checkbutton(root, text="Include directory structure in filename", variable=use_directory_structure)
folder_structure_checkbox.grid(column=1, row=4, columnspan=2, sticky='w', padx=10, pady=5)

output_label = ttk.Label(root, text="Output: (Not selected)", wraplength=200)
output_label.grid(column=1, row=5, columnspan=2, sticky='w', padx=10)

output_button = ttk.Button(root, text="Select Output Directory", command=select_output_folder)
output_button.grid(column=2, row=6, sticky='e', padx=10, pady=5)

# Progress status label (initially hidden)
progress_status_label = ttk.Label(root, text="", wraplength=300)
progress_status_label.grid(column=1, row=7, columnspan=2, sticky='w', padx=10, pady=2)
progress_status_label.grid_remove()  # Hide initially

# Progress bar (initially hidden)
progress_bar = ttk.Progressbar(root, mode='determinate', length=200)
progress_bar.grid(column=1, row=8, columnspan=2, sticky='ew', padx=10, pady=5)
progress_bar.grid_remove()  # Hide initially

convert_button = ttk.Button(root, text="Convert", command=run_conversion)
convert_button.grid(column=2, row=9, sticky='e', padx=10, pady=10)

root.mainloop()
