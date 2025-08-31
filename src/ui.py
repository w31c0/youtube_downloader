

import urllib.request
import json
import webbrowser
from downloader import Downloader

import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog

GITHUB_API_URL = "https://api.github.com/repos/w31c0/youtube_downloader/releases/latest"
LOCAL_VERSION = "0.0.1"

class YouTubeDownloaderUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader")
        self.root.geometry("400x200")
        import sys, os
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        try:
            self.root.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Failed to set window icon: {e}")
        self.root.deiconify()  # Show window after setting icon
        self.check_for_update()
        self.url_label = tk.Label(self.root, text="Paste YouTube link:")
        self.url_label.pack(pady=5)
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)
        self.format_var = tk.StringVar(value="mp4")
        self.mp4_radio = tk.Radiobutton(self.root, text="MP4 (Video)", variable=self.format_var, value="mp4")
        self.mp3_radio = tk.Radiobutton(self.root, text="MP3 (Audio)", variable=self.format_var, value="mp3")
        self.mp4_radio.pack()
        self.mp3_radio.pack()
        self.path_button = tk.Button(self.root, text="Choose destination folder", command=self.choose_path)
        self.path_button.pack(pady=5)
        self.path_label = tk.Label(self.root, text="No folder selected")
        self.path_label.pack(pady=5)
        self.download_button = tk.Button(self.root, text="Download", command=self.download)
        self.download_button.pack(pady=10)
        self.save_path = None

    def check_for_update(self):
        try:
            with urllib.request.urlopen(GITHUB_API_URL, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data["tag_name"].lstrip("v")
                if latest_version != LOCAL_VERSION:
                    release_url = data["html_url"]
                    msg = f"A new version is available: {latest_version}.\n\nYou can download it from:\n{release_url}"
                    if messagebox.askyesno("Update available", msg + "\n\nDo you want to open the page?"):
                        webbrowser.open(release_url)
        except Exception:
            pass

    def choose_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path = path
            self.path_label.config(text=path)
    def download(self):
        url = self.url_entry.get()
        fmt = self.format_var.get()
        path = self.save_path
        if not url or not path:
            messagebox.showerror("Error", "Please provide a link and choose a destination folder!")
            return
        try:
            if fmt == "mp4":
                msg = Downloader.download_video(url, path)
            else:
                msg = Downloader.download_audio(url, path)
            messagebox.showinfo("Success", msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run(self):
        self.root.mainloop()

