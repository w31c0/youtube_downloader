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
    # Spróbuj w folderze nadrzędnym
    for name in exe_names:
        exe_path = os.path.join(os.path.dirname(base), name)
        if os.path.exists(exe_path):
            return exe_path
    return None

def get_ytdlp_path():
    # Szukaj yt-dlp.exe lub yt-dlp_x86.exe w folderze aplikacji (działa też po spakowaniu do .exe)
    base = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    exe_names = ['yt-dlp.exe', 'yt-dlp_x86.exe']
    for name in exe_names:
        exe_path = os.path.join(base, name)
        if os.path.exists(exe_path):
            return exe_path
    # Spróbuj w folderze nadrzędnym
    for name in exe_names:
        exe_path = os.path.join(os.path.dirname(base), name)
        if os.path.exists(exe_path):
            return exe_path
    raise FileNotFoundError('yt-dlp.exe or yt-dlp_x86.exe not found!')

class Downloader:
    @staticmethod
    def download_video(url, path):
        ytdlp = get_ytdlp_path()
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
            raise Exception(result.stderr)
        return 'Downloaded to folder: ' + path

    @staticmethod
    def download_audio(url, path):
        ytdlp = get_ytdlp_path()
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
            raise Exception(result.stderr)
        return 'Downloaded to folder: ' + path
