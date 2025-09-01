import urllib.request
import json
import webbrowser
from downloader import Downloader

import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import threading

GITHUB_API_URL = "https://api.github.com/repos/w31c0/youtube_downloader/releases/latest"
LOCAL_VERSION = "0.0.2"

class YouTubeDownloaderUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader")
        self.root.geometry("450x280")
        import sys, os
        if getattr(sys, '_MEIPASS', False):
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        try:
            self.root.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Failed to set window icon: {e}")
        self.root.deiconify()
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
        
        # Progress bar
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(pady=5, fill='x', padx=20)
        
        self.progress_label = tk.Label(self.progress_frame, text="")
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=300, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        self.save_path = None
        self.downloading = False

    def check_for_update(self):
        try:
            req = urllib.request.Request(GITHUB_API_URL, headers={'User-Agent': 'YouTubeDownloader/0.0.1'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data["tag_name"].lstrip("v")
                if latest_version != LOCAL_VERSION:
                    release_url = data["html_url"]
                    msg = f"A new version is available: {latest_version}.\n\nYou can download it from:\n{release_url}"
                    if messagebox.askyesno("Update available", msg + "\n\nDo you want to open the page?"):
                        webbrowser.open(release_url)
        except urllib.error.URLError as e:
            print(f"Network error during update check: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding GitHub API response: {e}")
        except Exception as e:
            print(f"Unexpected error during update check: {e}")

    def choose_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path = path
            self.path_label.config(text=path)

    def update_progress(self, percentage):
        """Update progress bar from download thread"""
        self.root.after(0, self._update_progress_ui, percentage)
    
    def _update_progress_ui(self, percentage):
        """Update UI elements on main thread"""
        self.progress_bar['value'] = percentage
        self.progress_label.config(text=f"Downloading... {percentage:.1f}%")
        self.root.update_idletasks()
    
    def download_thread(self, url, fmt, path):
        """Download in separate thread to avoid UI freezing"""
        try:
            if fmt == "mp4":
                msg = Downloader.download_video(url, path, self.update_progress)
            else:
                msg = Downloader.download_audio(url, path, self.update_progress)
            
            # Update UI on completion
            self.root.after(0, self._download_complete, msg)
        except Exception as e:
            self.root.after(0, self._download_error, str(e))
    
    def _download_complete(self, msg):
        """Handle successful download completion"""
        self.downloading = False
        self.download_button.config(text="Download", state="normal")
        self.progress_label.config(text="Download completed!")
        messagebox.showinfo("Success", msg)
        # Reset progress bar after a delay
        self.root.after(3000, self._reset_progress)
    
    def _download_error(self, error_msg):
        """Handle download error"""
        self.downloading = False
        self.download_button.config(text="Download", state="normal")
        self.progress_label.config(text="Download failed!")
        self.progress_bar['value'] = 0
        messagebox.showerror("Error", f"Download failed: {error_msg}")
    
    def _reset_progress(self):
        """Reset progress bar and label"""
        self.progress_bar['value'] = 0
        self.progress_label.config(text="")
    
    def download(self):
        if self.downloading:
            return
        
        url = self.url_entry.get().strip()
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Error", "Please enter a valid YouTube link!")
            return
        
        fmt = self.format_var.get()
        path = self.save_path
        if not url or not path:
            messagebox.showerror("Error", "Please provide a link and choose a destination folder!")
            return
        
        # Start download in separate thread
        self.downloading = True
        self.download_button.config(text="Downloading...", state="disabled")
        self.progress_label.config(text="Starting download...")
        self.progress_bar['value'] = 0
        
        download_thread = threading.Thread(
            target=self.download_thread, 
            args=(url, fmt, path),
            daemon=True
        )
        download_thread.start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloaderUI()
    app.run()