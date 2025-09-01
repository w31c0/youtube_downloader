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
LOCAL_VERSION = "1.0.0"

class YouTubeDownloaderUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = max(700, int(screen_width * 0.35))
        window_height = max(850, int(screen_height * 0.9))
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(True, True)
        self.root.minsize(700, 850)
        self.colors = {
            'bg': '#0a0a0a',
            'card_bg': '#1a1a1a',
            'card_border': '#333333',
            'accent': '#ff3366',
            'accent_hover': '#ff1a4d',
            'accent_light': '#ff6b8a',
            'text': '#ffffff',
            'text_secondary': '#a0a0a0',
            'text_muted': '#666666',
            'input_bg': '#2a2a2a',
            'input_focus': '#333333',
            'success': '#00ff88',
            'shadow': '#000000',
            'glass': '#ffffff10'
        }
        self.root.configure(bg=self.colors['bg'])
        
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
        self.create_modern_ui()
        
        self.save_path = None
        self.downloading = False
    
    def create_modern_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        hero_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        hero_frame.pack(fill='x', pady=(0, 20))
        title_label = tk.Label(
            hero_frame, 
            text="YouTube", 
            font=('Segoe UI', 32, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['bg']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            hero_frame, 
            text="DOWNLOADER", 
            font=('Segoe UI', 18, 'normal'),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg']
        )
        subtitle_label.pack(pady=(0, 10))
        
        tagline_label = tk.Label(
            hero_frame, 
            text="Made by Weico", 
            font=('Segoe UI', 11),
            fg=self.colors['text_muted'],
            bg=self.colors['bg']
        )
        tagline_label.pack()
        url_container = tk.Frame(main_frame, bg=self.colors['bg'])
        url_container.pack(fill='x', pady=(0, 15))
        
        url_frame = tk.Frame(
            url_container, 
            bg=self.colors['card_bg'], 
            relief='solid', 
            bd=1,
            highlightbackground=self.colors['card_border'],
            highlightthickness=1
        )
        url_frame.pack(fill='x', padx=5, pady=5)
        
        self.url_label = tk.Label(
            url_frame, 
            text="🔗 PASTE YOUR YOUTUBE LINK", 
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['accent_light'],
            bg=self.colors['card_bg']
        )
        self.url_label.pack(anchor='w', padx=25, pady=(20, 8))
        self.url_entry = tk.Entry(
            url_frame, 
            font=('Segoe UI', 14),
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent'],
            relief='flat',
            bd=0,
            highlightthickness=2,
            highlightcolor=self.colors['accent'],
            highlightbackground=self.colors['input_bg']
        )
        self.url_entry.pack(fill='x', padx=25, pady=(0, 25), ipady=15)
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=...")
        self.url_entry.config(fg=self.colors['text_muted'])
        self.url_entry.bind('<FocusIn>', self.on_url_focus_in)
        self.url_entry.bind('<FocusOut>', self.on_url_focus_out)
        format_container = tk.Frame(main_frame, bg=self.colors['bg'])
        format_container.pack(fill='x', pady=(0, 15))
        
        format_frame = tk.Frame(
            format_container, 
            bg=self.colors['card_bg'], 
            relief='solid', 
            bd=1,
            highlightbackground=self.colors['card_border'],
            highlightthickness=1
        )
        format_frame.pack(fill='x', padx=5, pady=5)
        
        format_title = tk.Label(
            format_frame, 
            text="🎯 CHOOSE FORMAT", 
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['accent_light'],
            bg=self.colors['card_bg']
        )
        format_title.pack(anchor='w', padx=25, pady=(20, 15))
        radio_container = tk.Frame(format_frame, bg=self.colors['card_bg'])
        radio_container.pack(fill='x', padx=25, pady=(0, 25))
        
        self.format_var = tk.StringVar(value="mp4")
        mp4_frame = tk.Frame(radio_container, bg=self.colors['input_bg'], relief='flat')
        mp4_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.mp4_radio = tk.Radiobutton(
            mp4_frame, 
            text="🎬 MP4 Video", 
            variable=self.format_var, 
            value="mp4",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['input_bg'],
            selectcolor=self.colors['accent'],
            activebackground=self.colors['input_focus'],
            activeforeground=self.colors['text'],
            relief='flat',
            bd=0,
            padx=20,
            pady=15
        )
        self.mp4_radio.pack(fill='both', expand=True)
        
        mp3_frame = tk.Frame(radio_container, bg=self.colors['input_bg'], relief='flat')
        mp3_frame.pack(side='left', fill='x', expand=True, padx=(10, 0))
        
        self.mp3_radio = tk.Radiobutton(
            mp3_frame, 
            text="🎵 MP3 Audio", 
            variable=self.format_var, 
            value="mp3",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['input_bg'],
            selectcolor=self.colors['accent'],
            activebackground=self.colors['input_focus'],
            activeforeground=self.colors['text'],
            relief='flat',
            bd=0,
            padx=20,
            pady=15
        )
        self.mp3_radio.pack(fill='both', expand=True)
        path_container = tk.Frame(main_frame, bg=self.colors['bg'])
        path_container.pack(fill='x', pady=(0, 15))
        
        path_frame = tk.Frame(
            path_container, 
            bg=self.colors['card_bg'], 
            relief='solid', 
            bd=1,
            highlightbackground=self.colors['card_border'],
            highlightthickness=1
        )
        path_frame.pack(fill='x', padx=5, pady=5)
        
        path_title = tk.Label(
            path_frame, 
            text="📁 DESTINATION FOLDER", 
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['accent_light'],
            bg=self.colors['card_bg']
        )
        path_title.pack(anchor='w', padx=25, pady=(20, 15))
        self.path_button = tk.Button(
            path_frame, 
            text="🗂️  SELECT FOLDER", 
            command=self.choose_path,
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            relief='flat',
            bd=0,
            padx=30,
            pady=15,
            cursor='hand2',
            activebackground=self.colors['input_focus'],
            activeforeground=self.colors['text']
        )
        self.path_button.pack(fill='x', padx=25, pady=(0, 15))
        
        self.path_label = tk.Label(
            path_frame, 
            text="No folder selected yet", 
            font=('Segoe UI', 10),
            fg=self.colors['text_muted'],
            bg=self.colors['card_bg']
        )
        self.path_label.pack(anchor='w', padx=25, pady=(0, 20))
        download_container = tk.Frame(main_frame, bg=self.colors['bg'])
        download_container.pack(fill='x', pady=(5, 15))
        glow_frame = tk.Frame(download_container, bg=self.colors['accent'], relief='flat')
        glow_frame.pack(padx=2, pady=2)
        
        self.download_button = tk.Button(
            glow_frame, 
            text="⚡ DOWNLOAD NOW", 
            command=self.download,
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            bd=0,
            padx=80,
            pady=25,
            cursor='hand2',
            activebackground=self.colors['accent_hover'],
            activeforeground='white'
        )
        self.download_button.pack(fill='x')
        self.progress_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        self.progress_frame.pack(fill='x', pady=(0, 20))
        
        self.progress_label = tk.Label(
            self.progress_frame, 
            text="", 
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['accent_light'],
            bg=self.colors['bg']
        )
        self.progress_label.pack(pady=(0, 15))
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Premium.Horizontal.TProgressbar",
            background=self.colors['accent'],
            troughcolor=self.colors['input_bg'],
            borderwidth=0,
            lightcolor=self.colors['accent_light'],
            darkcolor=self.colors['accent'],
            thickness=8
        )
        progress_container = tk.Frame(self.progress_frame, bg=self.colors['input_bg'], relief='flat')
        progress_container.pack(fill='x', padx=30, pady=5)
        
        self.progress_bar = ttk.Progressbar(
            progress_container, 
            mode='determinate',
            style="Premium.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill='x', padx=3, pady=3)
        self.bind_hover_effects()
    
    def on_url_focus_in(self, event):
        if self.url_entry.get() == "https://www.youtube.com/watch?v=...":
            self.url_entry.delete(0, tk.END)
            self.url_entry.config(fg=self.colors['text'])
    
    def on_url_focus_out(self, event):
        if not self.url_entry.get():
            self.url_entry.insert(0, "https://www.youtube.com/watch?v=...")
            self.url_entry.config(fg=self.colors['text_muted'])
    
    def bind_hover_effects(self):
        def on_enter_download(e):
            if not self.downloading:
                self.download_button.config(bg=self.colors['accent_hover'])
        
        def on_leave_download(e):
            if not self.downloading:
                self.download_button.config(bg=self.colors['accent'])
        
        def on_enter_path(e):
            self.path_button.config(bg=self.colors['input_focus'])
        
        def on_leave_path(e):
            self.path_button.config(bg=self.colors['input_bg'])
        
        self.download_button.bind("<Enter>", on_enter_download)
        self.download_button.bind("<Leave>", on_leave_download)
        self.path_button.bind("<Enter>", on_enter_path)
        self.path_button.bind("<Leave>", on_leave_path)

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
        self.root.after(0, self._update_progress_ui, percentage)
    
    def _update_progress_ui(self, percentage):
        self.progress_bar['value'] = percentage
        self.progress_label.config(text=f"Downloading... {percentage:.1f}%")
        self.root.update_idletasks()
    
    def download_thread(self, url, fmt, path):
        try:
            if fmt == "mp4":
                msg = Downloader.download_video(url, path, self.update_progress)
            else:
                msg = Downloader.download_audio(url, path, self.update_progress)
            
            self.root.after(0, self._download_complete, msg)
        except Exception as e:
            self.root.after(0, self._download_error, str(e))
    
    def _download_complete(self, msg):
        self.downloading = False
        self.download_button.config(text="Download", state="normal")
        self.progress_label.config(text="Download completed!")
        messagebox.showinfo("Success", msg)
        self.root.after(3000, self._reset_progress)
    
    def _download_error(self, error_msg):
        self.downloading = False
        self.download_button.config(text="Download", state="normal")
        self.progress_label.config(text="Download failed!")
        self.progress_bar['value'] = 0
        messagebox.showerror("Error", f"Download failed: {error_msg}")
    
    def _reset_progress(self):
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