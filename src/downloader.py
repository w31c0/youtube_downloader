import subprocess
import os
import sys
import re
import threading

def get_ffmpeg_path():
    base = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    exe_names = ['ffmpeg.exe']
    for name in exe_names:
        exe_path = os.path.join(base, name)
        if os.path.exists(exe_path):
            return exe_path
    for name in exe_names:
        exe_path = os.path.join(os.path.dirname(base), name)
        if os.path.exists(exe_path):
            return exe_path
    return None

def get_ytdlp_path():
    base = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    exe_names = ['yt-dlp.exe', 'yt-dlp_x86.exe']
    for name in exe_names:
        exe_path = os.path.join(base, name)
        if os.path.exists(exe_path):
            return exe_path
    for name in exe_names:
        exe_path = os.path.join(os.path.dirname(base), name)
        if os.path.exists(exe_path):
            return exe_path
    return None

class Downloader:
    _current_process = None
    _cancel_requested = False
    
    @staticmethod
    def cancel_download():
        Downloader._cancel_requested = True
        if Downloader._current_process:
            try:
                Downloader._current_process.terminate()
            except:
                pass
    
    @staticmethod
    def _run_with_progress(cmd, progress_callback=None):
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        
        Downloader._cancel_requested = False
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            universal_newlines=True,
            bufsize=1,
            startupinfo=startupinfo
        )
        Downloader._current_process = process
        
        output_lines = []
        
        for line in iter(process.stdout.readline, ''):
            if Downloader._cancel_requested:
                process.terminate()
                break
                
            output_lines.append(line)
            
            if progress_callback:
                if '[download]' in line and '%' in line:
                    match = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)
                    if match:
                        percentage = float(match.group(1))
                        progress_callback(percentage)
                elif 'Merging formats into' in line:
                    progress_callback(95)
                elif 'Deleting original file' in line:
                    progress_callback(98)
        
        process.wait()
        Downloader._current_process = None
        
        if Downloader._cancel_requested:
            raise Exception("Download cancelled by user.")
        
        if process.returncode != 0:
            error_output = ''.join(output_lines)
            if "Unable to download webpage" in error_output:
                raise Exception("Invalid or inaccessible YouTube URL.")
            raise Exception(f"Download failed: {error_output}")
        
        if progress_callback:
            progress_callback(100)
        
        return ''.join(output_lines)

    @staticmethod
    def download_video(url, path, progress_callback=None):
        if not os.path.isdir(path):
            raise Exception("Invalid destination folder.")
        ytdlp = get_ytdlp_path()
        if not ytdlp:
            raise Exception("yt-dlp executable not found. Please include yt-dlp.exe in the application directory.")
        ffmpeg = get_ffmpeg_path()
        cmd = [
            ytdlp,
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            '-o', os.path.join(path, '%(title)s.%(ext)s'),
            url
        ]
        if ffmpeg:
            cmd += ['--ffmpeg-location', os.path.dirname(ffmpeg)]
        
        Downloader._run_with_progress(cmd, progress_callback)
        return 'Video downloaded to folder: ' + path

    @staticmethod
    def download_audio(url, path, progress_callback=None):
        if not os.path.isdir(path):
            raise Exception("Invalid destination folder.")
        ytdlp = get_ytdlp_path()
        if not ytdlp:
            raise Exception("yt-dlp executable not found. Please include yt-dlp.exe in the application directory.")
        ffmpeg = get_ffmpeg_path()
        cmd = [
            ytdlp,
            '-f', 'bestaudio',
            '--extract-audio',
            '--audio-format', 'mp3',
            '-o', os.path.join(path, '%(title)s.%(ext)s'),
            url
        ]
        if ffmpeg:
            cmd += ['--ffmpeg-location', os.path.dirname(ffmpeg)]
        
        Downloader._run_with_progress(cmd, progress_callback)
        return 'Audio downloaded to folder: ' + path