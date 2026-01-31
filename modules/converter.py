import os
import sys
from pydub import AudioSegment

# Simple solution to hide console windows on Windows
if sys.platform == "win32":
    import subprocess
    
    # Store original and create silent version
    original_popen = subprocess.Popen
    
    def silent_popen(*args, **kwargs):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        kwargs['startupinfo'] = startupinfo
        kwargs['stdout'] = subprocess.DEVNULL
        kwargs['stderr'] = subprocess.DEVNULL
        return original_popen(*args, **kwargs)
    
    # Override subprocess.Popen (this is what pydub uses)
    subprocess.Popen = silent_popen

def get_folder_structure_prefix(file_path, base_directory=None):
    """Generate a folder structure prefix from the file path"""
    if base_directory:
        # Use relative path from base directory
        try:
            relative_path = os.path.relpath(os.path.dirname(file_path), base_directory)
            if relative_path == '.':
                return ""  # File is in root directory
            # Replace path separators with dashes and clean up
            folder_prefix = relative_path.replace(os.sep, '-').replace('/', '-').replace('\\', '-')
            return folder_prefix + '-'
        except ValueError:
            # Fallback if relative path calculation fails
            pass
    
    # Fallback: use just the immediate parent directory
    parent_dir = os.path.basename(os.path.dirname(file_path))
    if parent_dir:
        return parent_dir + '-'
    return ""

def get_unique_filename(output_dir, filename):
    """Generate a unique filename if conflicts exist"""
    base_path = os.path.join(output_dir, filename)
    if not os.path.exists(base_path):
        return filename
    
    # Split filename and extension
    name, ext = os.path.splitext(filename)
    counter = 1
    
    # Keep incrementing until we find an available name
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = os.path.join(output_dir, new_filename)
        if not os.path.exists(new_path):
            return new_filename
        counter += 1

def convert(file_paths: list, channels: int, target_sample_rate: int, sample_width: int, output_dir: str, filename_prefix: str = "", use_folder_structure: bool = False, base_directory: str = None, progress_callback=None):
    if not file_paths:
        return [], 0, 0  # Return empty list and zero sizes
    
    converted_files = []
    processed_filenames = set()  # Track filenames we're planning to create
    total_files = len(file_paths)
    total_original_size = 0
    total_converted_size = 0
    
    for index, file_path in enumerate(file_paths):
        file_path = os.path.abspath(file_path)
        if file_path.endswith(".wav"):
            try:
                # Get original file size
                original_size = os.path.getsize(file_path)
                # Notify progress
                if progress_callback:
                    filename = os.path.basename(file_path)
                    progress_callback(index + 1, total_files, filename)
                
                audio = AudioSegment.from_wav(file_path)
                audio = audio.set_frame_rate(target_sample_rate)
                audio = audio.set_sample_width(sample_width)
                audio = audio.set_channels(channels)

                filename = os.path.basename(file_path)
                
                # Build the output filename
                output_filename = filename
                
                # Add folder structure prefix if enabled
                if use_folder_structure:
                    folder_prefix = get_folder_structure_prefix(file_path, base_directory)
                    if folder_prefix:
                        output_filename = folder_prefix + output_filename
                
                # Add custom prefix if provided
                if filename_prefix:
                    output_filename = filename_prefix + output_filename
                
                # Only apply conflict resolution if there's actually a conflict
                final_filename = output_filename
                if final_filename in processed_filenames or os.path.exists(os.path.join(output_dir, final_filename)):
                    final_filename = get_unique_filename(output_dir, output_filename)
                
                # Track this filename to prevent future conflicts in this batch
                processed_filenames.add(final_filename)
                
                output_path = os.path.join(output_dir, final_filename)
                
                audio.export(output_path, format="wav")
                
                # Get converted file size
                converted_size = os.path.getsize(output_path)
                
                # Track sizes
                total_original_size += original_size
                total_converted_size += converted_size
                
                converted_files.append(final_filename)
                # Removed print statement to avoid console output
            except Exception as e:
                # Handle errors silently or log them appropriately
                continue
    
    return converted_files, total_original_size, total_converted_size
