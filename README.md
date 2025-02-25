# PsVideoMaker
PSP Video Converter (NVIDIA Accelerated)  This project is a simple Tkinter tool to convert videos to a format running on a Sony PlayStation Portable (PSP) using FFmpeg and NVIDIA hardware acceleration (h264-nvenc). The tool also allows you to trim the video automatically or manually in preview mode.
# PSP Video Converter (NVIDIA Accelerated)

This project is a simple Tkinter tool to convert videos for playback on the Sony PlayStation Portable (PSP) using [FFmpeg](https://ffmpeg.org/) with NVIDIA GPU acceleration (`h264_nvenc`). It also allows you to automatically or manually crop the video in a preview mode.

## Table of Contents
1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Detailed Features](#detailed-features)
6. [Known Limitations](#known-limitations)
7. [License](#license)
8. [Contributors](#contributors)

---

## Features

- **Input Selection**: Load MP4 or MKV files.  
- **Output Selection**: Specify a path to save the converted file in MP4 format.  
- **Preview (Canvas)**: Displays a random frame from the video (random timestamp).  
- **Automatic Cropping**: Calculates a crop area matching the PSP's aspect ratio (480×272).  
- **Manual Cropping**: Allows drawing a crop rectangle on the preview canvas.  
- **FFmpeg Conversion**: Uses NVIDIA GPU acceleration (`h264_nvenc`), including downscaling, cropping, and audio adjustments.  
- **Simple GUI**: Built in Python with the Tkinter framework.

---

## Requirements

1. **Python 3.x**: [Download and install](https://www.python.org/downloads/).
2. **FFmpeg**:  
   - Must be installed for the script to work.  
   - On Windows, make sure `ffmpeg.exe` is in your `PATH` or provide the full path to it.
3. **NVIDIA Graphics Card with NVENC support** (for `h264_nvenc`):
   - Properly installed drivers so that FFmpeg can use GPU acceleration.
4. **Python Dependencies**:
   - `opencv-python` (cv2)
   - `Pillow`
   - `tkinter` (usually included with most standard Python installations)
   - `random` (part of the Python standard library)
   - `subprocess` (part of the Python standard library)

Install any missing packages via pip:
```bash
pip install opencv-python Pillow
```

---

## Installation

1. **Clone or download the repository**  
   ```bash
   git clone https://github.com/<USER>/<REPO>.git
   cd <REPO>
   ```
2. **Install dependencies** (see [Requirements](#requirements)).
3. **Install FFmpeg**  
   - Ensure that `ffmpeg` (and `ffprobe`) are in your system path.
   - [Windows builds](https://www.gyan.dev/ffmpeg/builds/)
   - [macOS (Homebrew)](https://formulae.brew.sh/formula/ffmpeg)
   - [Linux (APT/RPM/Pacman, etc.)] – e.g., `sudo apt-get install ffmpeg` (Debian/Ubuntu).

---

## Usage

1. **Run the script**  
   ```bash
   python PSPVideoConverter.py
   ```
   This will open the Tkinter GUI window.

2. **Select Input File**  
   - Click the “Browse…” button next to “Input file (MP4/MKV)” 
   - Choose your video file.
3. **Select Output File**  
   - Click the “Save as…” button next to “Output file (MP4)”  
   - Specify the output path (filename with `.mp4`).
4. **Random Frame**  
   - Click “Show random timestamp” to see a preview frame from your video.
5. **Automatic Crop**  
   - Click “Auto crop” to generate a crop area according to the PSP aspect ratio (480×272).
6. **Manual Crop** (optional)  
   - Click and drag in the preview canvas to draw a red rectangle.  
   - Release the mouse to finalize the crop area.  
7. **Convert**  
   - Click the “Convert” button.  
   - The script will call FFmpeg with the respective parameters (crop, scale, NVENC, etc.).  
   - When done, you’ll have your PSP-compatible MP4 file.

---

## Detailed Features

### 1. Random Frame Selection
- The preview displays a random frame from the video so you can see a representative scene for cropping.

### 2. Automatic Crop
- Calculates the appropriate crop to match the PSP resolution (480×272).
- It checks the original aspect ratio vs. the PSP’s ratio (`480/272 ≈ 1.7647`).

### 3. Manual Crop
- Draw a custom rectangle on the canvas to define the crop area.  
- When you click and drag, a red rectangle is created; its coordinates are then applied to the FFmpeg crop filter.

### 4. NVIDIA Acceleration
- Uses `-c:v h264_nvenc` in FFmpeg for accelerated encoding on supported NVIDIA GPUs.  
- On systems without NVIDIA GPUs, you’d need to adjust the encoder (e.g., `libx264`).

---

## Known Limitations

- Requires an NVIDIA GPU that supports `h264_nvenc`.  
- PSP video compatibility might depend on the specific firmware version. Typical recommended settings are `baseline` profile, `level=3.0`, `fps=30`. These can vary based on firmware.  
- Manual cropping can be slightly imprecise if the original video is very large, but typically it works well.

---

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE) for details (if available).  
**Disclaimer**: The use of FFmpeg and NVIDIA encoders is subject to their respective licenses and terms.

---

## Contributors

- **Author**: [zaepfchenman](https://github.com/zaepfchenman)  



Feel free to submit issues, pull requests, or any improvements. We welcome all contributions and feedback!
