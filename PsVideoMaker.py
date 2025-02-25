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
        
        # Crop parameters
        self.crop_x = self.crop_y = 0
        self.crop_w = self.crop_h = 0
        self.crop_rect = None
        
        # Original dimensions of the video
        self.original_width = 0
        self.original_height = 0
        
        # Scaling for the preview
        self.scale = 1.0
        self.x_offset = 0
        self.y_offset = 0
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame with padding
        mainframe = ttk.Frame(self.root, padding="10 10 10 10")
        mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        # Input and output fields
        ttk.Label(mainframe, text="Input file (MP4/MKV):").grid(column=0, row=0, sticky=tk.W)
        self.input_entry = ttk.Entry(mainframe, width=40)
        self.input_entry.grid(column=1, row=0, sticky=(tk.W, tk.E))
        ttk.Button(mainframe, text="Browse...", command=self.select_input).grid(column=2, row=0)
        
        ttk.Label(mainframe, text="Output file (MP4):").grid(column=0, row=1, sticky=tk.W)
        self.output_entry = ttk.Entry(mainframe, width=40)
        self.output_entry.grid(column=1, row=1, sticky=(tk.W, tk.E))
        ttk.Button(mainframe, text="Save as...", command=self.select_output).grid(column=2, row=1)
        
        # Preview canvas
        self.preview_canvas = tk.Canvas(self.root, width=480, height=272, bg="black")
        self.preview_canvas.grid(column=0, row=1, padx=10, pady=10)
        
        # Frame for control buttons
        buttons_frame = ttk.Frame(self.root, padding="10 10 10 10")
        buttons_frame.grid(column=0, row=2)
        ttk.Button(buttons_frame, text="Show random frame", command=self.select_random_frame)\
            .grid(column=0, row=0, padx=5, pady=5)
        ttk.Button(buttons_frame, text="Auto crop", command=self.auto_crop)\
            .grid(column=1, row=0, padx=5, pady=5)
        ttk.Button(buttons_frame, text="Convert", command=self.convert_video)\
            .grid(column=2, row=0, padx=5, pady=5)
        
        # Set padding for all children in mainframe
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
        # Mouse events for manual cropping
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
            title="Select input file",
            filetypes=[("Video Files", "*.mp4 *.mkv")]
        )
        if self.video_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.video_path)
            self.select_random_frame()  # Automatically load a preview frame
    
    def select_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Save output file",
            defaultextension=".mp4",
            filetypes=[("MP4 Files", "*.mp4")]
        )
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)
    
    def select_random_frame(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video file first!")
            return
        
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open the video!")
            return
        
        self.original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            messagebox.showerror("Error", "This video seems to have no frames!")
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
            messagebox.showerror("Error", "Could not extract a frame!")
    
    def auto_crop(self):
        """
        Automatically calculates a crop area maintaining the PSP target aspect ratio (480:272).
        """
        if not self.video_path:
            messagebox.showerror("Error", "Please load a video first!")
            return
        
        target_aspect = 480 / 272
        original_aspect = self.original_width / self.original_height
        
        if original_aspect > target_aspect:
            # If the original is wider, we crop the width
            new_width = int(self.original_height * target_aspect)
            self.crop_x = int((self.original_width - new_width) / 2)
            self.crop_y = 0
            self.crop_w = new_width
            self.crop_h = self.original_height
        else:
            # If the original is taller, we crop the height
            new_height = int(self.original_width / target_aspect)
            self.crop_x = 0
            self.crop_y = int((self.original_height - new_height) / 2)
            self.crop_w = self.original_width
            self.crop_h = new_height
        
        # Scale the crop area to the preview canvas
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
        # Start of a manual crop selection
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        if self.crop_rect:
            self.preview_canvas.delete(self.crop_rect)
        self.crop_rect = self.preview_canvas.create_rectangle(
            self.crop_start_x, self.crop_start_y,
            self.crop_start_x, self.crop_start_y,
            outline="red"
        )
    
    def update_crop(self, event):
        # Update the rectangle while dragging
        self.preview_canvas.coords(
            self.crop_rect,
            self.crop_start_x,
            self.crop_start_y,
            event.x,
            event.y
        )
    
    def end_crop(self, event):
        # Finalize the crop area
        self.crop_x = min(self.crop_start_x, event.x)
        self.crop_y = min(self.crop_start_y, event.y)
        self.crop_w = abs(event.x - self.crop_start_x)
        self.crop_h = abs(event.y - self.crop_start_y)
        print(f"Manual Crop (Canvas): x={self.crop_x}, y={self.crop_y}, w={self.crop_w}, h={self.crop_h}")
    
    def convert_video(self):
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        
        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select both an input and an output file!")
            return
        
        command = [
            "ffmpeg",
            "-i", input_file,
            "-c:v", "h264_nvenc",
            "-profile:v", "baseline",
            "-level:v", "3.0",
            "-b:v", "1500k",
            "-vf", f"crop={self.crop_w}:{self.crop_h}:{self.crop_x}:{self.crop_y},scale=480:272,fps=30",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ac", "2",       # Stereo
            "-ar", "44100",   # 44.1 kHz Sample Rate
            output_file
        ]
        
        try:
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", "Video conversion was successful!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred during conversion:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    PSPVideoConverter(root)
    root.mainloop()
