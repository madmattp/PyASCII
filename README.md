# PyASCII

PyASCII is a Python script that applies an ASCII art filter to both images and videos. The script allows for customization of resolution, contrast, and color filters, and processes videos by dividing them into subclips for efficient processing.

## Features

- **Image Processing**: Convert images to ASCII art with adjustable resolution and optional contrast enhancement.
- **Video Processing**: Convert videos to ASCII art by processing video frames in chunks, optimizing disk space by periodically merging subclips.
- **Custom Filters**: Apply various monochrome filters to the output.
- **Multi-Processing**: Utilizes multiple CPU cores for faster video processing.

## Requirements
- A Linux Machine (A Windows version is in development)
- Python >= 3.11
- Required Python libraries:
  - `Pillow==10.4.0`
  - `moviepy==1.0.3`
  - `opencv_contrib_python==4.10.0.84`
  - `numpy==2.0.1`

Install the required libraries using pip:

```bash
pip install -r requirements.txt
