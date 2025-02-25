import cv2
import random
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess

class PSPVideoConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("PSP Video Converter (NVIDIA Accelerated)")
        self.video_path = ""
        self.preview_image = None
        self.crop_x = self.crop_y = self.crop_w = self.crop_h = 0
        self.crop_rect = None
        self.original_width = self.original_height = 0
        self.scale = 1.0
        self.x_offset = self.y_offset = 0
        self.create_widgets()
    
    def create_widgets(self):
        # Hauptframe mit Padding
        mainframe = ttk.Frame(self.root, padding="10 10 10 10")
        mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        # Eingabe- und Ausgabefelder
        ttk.Label(mainframe, text="Eingabedatei (MP4/MKV):").grid(column=0, row=0, sticky=tk.W)
        self.input_entry = ttk.Entry(mainframe, width=40)
        self.input_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))
        ttk.Button(mainframe, text="Durchsuchen...", command=self.select_input).grid(column=2, row=0)
        
        ttk.Label(mainframe, text="Ausgabedatei (MP4):").grid(column=0, row=1, sticky=tk.W)
        self.output_entry = ttk.Entry(mainframe, width=40)
        self.output_entry.grid(column=1, row=1, sticky=(tk.W, tk.E))
        ttk.Button(mainframe, text="Speichern unter...", command=self.select_output).grid(column=2, row=1)
        
        # Vorschau-Canvas
        self.preview_canvas = tk.Canvas(self.root, width=480, height=272, bg="black")
        self.preview_canvas.grid(column=0, row=1, padx=10, pady=10)
        
        # Steuerungsbuttons in eigenem Frame
        buttons_frame = ttk.Frame(self.root, padding="10 10 10 10")
        buttons_frame.grid(column=0, row=2)
        ttk.Button(buttons_frame, text="Zufällige Filmstelle anzeigen", command=self.select_random_frame)\
            .grid(column=0, row=0, padx=5, pady=5)
        ttk.Button(buttons_frame, text="Automatisch zuschneiden", command=self.auto_crop)\
            .grid(column=1, row=0, padx=5, pady=5)
        ttk.Button(buttons_frame, text="Konvertieren", command=self.convert_video)\
            .grid(column=2, row=0, padx=5, pady=5)
        
        # Padding für alle Kinder im mainframe
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
        # Maus-Events für manuelles Cropping
        self.preview_canvas.bind("<ButtonPress-1>", self.start_crop)
        self.preview_canvas.bind("<B1-Motion>", self.update_crop)
        self.preview_canvas.bind("<ButtonRelease-1>", self.end_crop)
    
    def resize_with_aspect_ratio(self, image, target_width, target_height):
        original_w, original_h = image.size
        ratio = min(target_width / original_w, target_height / original_h)
        new_width = int(original_w * ratio)
        new_height = int(original_h * ratio)
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized, ratio
    
    def pad_image_to_canvas(self, image, canvas_width, canvas_height):
        new_image = Image.new("RGB", (canvas_width, canvas_height), (0, 0, 0))
        x_off = (canvas_width - image.width) // 2
        y_off = (canvas_height - image.height) // 2
        new_image.paste(image, (x_off, y_off))
        return new_image, x_off, y_off
    
    def select_input(self):
        self.video_path = filedialog.askopenfilename(
            title="Eingabedatei auswählen",
            filetypes=[("Video-Dateien", "*.mp4 *.mkv")]
        )
        if self.video_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.video_path)
            self.select_random_frame()  # Lade automatisch eine Vorschau
    
    def select_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Ausgabedatei speichern unter",
            defaultextension=".mp4",
            filetypes=[("MP4-Dateien", "*.mp4")]
        )
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)
    
    def select_random_frame(self):
        if not self.video_path:
            messagebox.showerror("Fehler", "Bitte zuerst eine Videodatei auswählen!")
            return
        
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            messagebox.showerror("Fehler", "Konnte das Video nicht öffnen!")
            return
        
        self.original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            messagebox.showerror("Fehler", "Das Video scheint keine Frames zu enthalten!")
            return
        
        random_frame = random.randint(0, total_frames - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            resized, self.scale = self.resize_with_aspect_ratio(image, 480, 272)
            padded, self.x_offset, self.y_offset = self.pad_image_to_canvas(resized, 480, 272)
            self.preview_image = ImageTk.PhotoImage(padded)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_image)
        else:
            messagebox.showerror("Fehler", "Konnte keinen Frame extrahieren!")
    
    def auto_crop(self):
        """Berechnet automatisch einen Crop-Bereich, der das Ziel-Seitenverhältnis 480:272 erhält."""
        if not self.video_path:
            messagebox.showerror("Fehler", "Bitte zuerst ein Video laden!")
            return
        
        target_aspect = 480 / 272
        original_aspect = self.original_width / self.original_height
        
        if original_aspect > target_aspect:
            new_width = int(self.original_height * target_aspect)
            self.crop_x = int((self.original_width - new_width) / 2)
            self.crop_y = 0
            self.crop_w = new_width
            self.crop_h = self.original_height
        else:
            new_height = int(self.original_width / target_aspect)
            self.crop_x = 0
            self.crop_y = int((self.original_height - new_height) / 2)
            self.crop_w = self.original_width
            self.crop_h = new_height
        
        canvas_crop_x = int(self.crop_x * self.scale) + self.x_offset
        canvas_crop_y = int(self.crop_y * self.scale) + self.y_offset
        canvas_crop_w = int(self.crop_w * self.scale)
        canvas_crop_h = int(self.crop_h * self.scale)
        
        if self.crop_rect:
            self.preview_canvas.delete(self.crop_rect)
        self.crop_rect = self.preview_canvas.create_rectangle(
            canvas_crop_x, canvas_crop_y,
            canvas_crop_x + canvas_crop_w, canvas_crop_y + canvas_crop_h,
            outline="blue", width=2
        )
        print(f"Auto Crop (Original): x={self.crop_x}, y={self.crop_y}, w={self.crop_w}, h={self.crop_h}")
    
    def start_crop(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        if self.crop_rect:
            self.preview_canvas.delete(self.crop_rect)
        self.crop_rect = self.preview_canvas.create_rectangle(self.crop_start_x, self.crop_start_y, 
                                                               self.crop_start_x, self.crop_start_y, outline="red")
    
    def update_crop(self, event):
        self.preview_canvas.coords(self.crop_rect, self.crop_start_x, self.crop_start_y, event.x, event.y)
    
    def end_crop(self, event):
        self.crop_x = min(self.crop_start_x, event.x)
        self.crop_y = min(self.crop_start_y, event.y)
        self.crop_w = abs(event.x - self.crop_start_x)
        self.crop_h = abs(event.y - self.crop_start_y)
        print(f"Manueller Crop (Canvas): x={self.crop_x}, y={self.crop_y}, w={self.crop_w}, h={self.crop_h}")
    
    def convert_video(self):
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        if not input_file or not output_file:
            messagebox.showerror("Fehler", "Bitte wähle sowohl eine Eingabe- als auch eine Ausgabedatei aus!")
            return
        
        command = [
    "ffmpeg",
    "-i", input_file,
    "-c:v", "libx264",
    "-profile:v", "baseline",
    "-level:v", "3.0",
    "-b:v", "1500k",
    "-vf", f"crop={self.crop_w}:{self.crop_h}:{self.crop_x}:{self.crop_y},scale=480:272,fps=30",
    "-c:a", "aac",
    "-b:a", "128k",
    "-ac", "2",         # Stereo
    "-ar", "44100",     # 44,100 Hz Sample Rate
    output_file
        ]
        
        try:
            subprocess.run(command, check=True)
            messagebox.showinfo("Erfolg", "Video wurde erfolgreich konvertiert!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Fehler", f"Fehler bei der Konvertierung:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    PSPVideoConverter(root)
    root.mainloop()
