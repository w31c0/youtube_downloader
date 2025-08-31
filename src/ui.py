

import urllib.request
import json
import webbrowser
from downloader import Downloader

import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog

# Ustaw swój login/repozytorium oraz wersję programu
GITHUB_API_URL = "https://api.github.com/repos/pplwi/youtube_downloader/releases/latest"
LOCAL_VERSION = "1.0.0"  # Zmień na aktualną wersję programu

class YouTubeDownloaderUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader")
        self.root.geometry("400x200")
    self.check_for_update()
    def check_for_update(self):
        try:
            with urllib.request.urlopen(GITHUB_API_URL, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data["tag_name"].lstrip("v")
                if latest_version != LOCAL_VERSION:
                    release_url = data["html_url"]
                    msg = f"Dostępna jest nowa wersja: {latest_version}.\n\nMożesz pobrać ją z:\n{release_url}"
                    if messagebox.askyesno("Aktualizacja dostępna", msg + "\n\nCzy chcesz otworzyć stronę?"):
                        webbrowser.open(release_url)
        except Exception:
            pass  # Brak internetu lub błąd API, ignorujemy

        self.url_label = tk.Label(self.root, text="Wklej link do YouTube:")
        self.url_label.pack(pady=5)
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)

        self.format_var = tk.StringVar(value="mp4")
        self.mp4_radio = tk.Radiobutton(self.root, text="MP4 (Wideo)", variable=self.format_var, value="mp4")
        self.mp3_radio = tk.Radiobutton(self.root, text="MP3 (Audio)", variable=self.format_var, value="mp3")
        self.mp4_radio.pack()
        self.mp3_radio.pack()

        self.path_button = tk.Button(self.root, text="Wybierz folder docelowy", command=self.choose_path)
        self.path_button.pack(pady=5)
        self.path_label = tk.Label(self.root, text="Nie wybrano folderu")
        self.path_label.pack(pady=5)
        self.download_button = tk.Button(self.root, text="Pobierz", command=self.download)
        self.download_button.pack(pady=10)
        self.save_path = None

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
            messagebox.showerror("Błąd", "Podaj link i wybierz folder docelowy!")
            return
        try:
            if fmt == "mp4":
                msg = Downloader.download_video(url, path)
            else:
                msg = Downloader.download_audio(url, path)
            messagebox.showinfo("Sukces", msg)
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def run(self):
        self.root.mainloop()
