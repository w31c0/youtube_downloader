import subprocess
import os
import sys

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
    @staticmethod
    def download_video(url, path):
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
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            if "Unable to download webpage" in error_msg:
                raise Exception("Invalid or inaccessible YouTube URL.")
            raise Exception(f"Download failed: {error_msg}")
        return 'Video downloaded to folder: ' + path

    @staticmethod
    def download_audio(url, path):
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
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            if "Unable to download webpage" in error_msg:
                raise Exception("Invalid or inaccessible YouTube URL.")
            raise Exception(f"Download failed: {error_msg}")
        return 'Audio downloaded to folder: ' + path