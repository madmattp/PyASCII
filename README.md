<p align="center">
  <img src="https://github.com/user-attachments/assets/000362a2-0bf2-45b9-a293-a957f3cd4590" alt="PyAscii_image" width="45%">
  <img src="https://github.com/user-attachments/assets/d178fe02-52b4-467f-9cec-67b40ecc3057" alt="image" width="45%">
</p>

# PyASCII
[![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/downloads/release/python-3119/)
[![image](https://img.shields.io/badge/OpenCV-27338e?style=for-the-badge&logo=OpenCV&logoColor=white)](https://pypi.org/project/opencv-python/)

PyASCII is a Python script that applies an ASCII art filter to both images and videos. The script allows for customization of resolution, contrast, and color filters, and processes videos by dividing them into subclips for efficient processing.

The Sprite Sheet used in the script was made by [@DanXimemes](https://x.com/DanXimemes)

## Features

- **Image Processing**: Convert images to ASCII art with adjustable resolution and optional contrast enhancement.
- **Video Processing**: Convert videos to ASCII art by processing video frames in chunks, optimizing disk space by periodically merging subclips.
- **Custom Filters**: Apply various monochrome filters to the output.
- **Multi-Processing**: Utilizes multiple CPU cores for faster video processing.

## Requirements
- Linux or Windows Operating System
- Python >= 3.11
- Required Python libraries:
  - `Pillow==10.4.0`
  - `moviepy==1.0.3`
  - `opencv_contrib_python==4.10.0.84`
  - `numpy==2.0.1`

Install the required libraries using pip:

```bash
pip install -r requirements.txt
```
## Usage
To run the script, use the following command:
```bash
python PyASCII.py -m <media_file> [options]
```

### Arguments
- m, --media MEDIA_FILE
  - Specifies the input image or video file (required).
- r, --resolution RES
  - Sets the resolution of the output (default is 720).
- f, --filter FILTER
  -  Applies a monochrome filter to the output. Available filters:
      - Orange, Capuccino, Brat, Fairy, Bloody, Lavender, Poiple, Cyan, Vapor
- c, --contrast
  - Increases the contrast of the output image or video.
- o, --output PATH
  - Specifies the output file path.

## Examples
### Convert an Image
```bash
python PyASCII.py -m cat_image.jfif -r 480 -c -f Orange -o output_image.png
```
<p align="center">
  <img src="https://github.com/user-attachments/assets/c2414558-f241-4c61-b203-00be3e6b0b91" alt="cat_input" width="45%">
  <img src="https://github.com/user-attachments/assets/d178fe02-52b4-467f-9cec-67b40ecc3057" alt="cat_output" width="45%">
</p>

### Convert a Video
```bash
python3.11 PyASCII.py -m cat_huh.mp4 -r 1080 -f Brat
```
<p align="center">
  <video src="https://github.com/user-attachments/assets/1d1abe14-625d-4bd7-87e6-00cb6b14da05" width="45%" controls></video>
  <video src="https://github.com/user-attachments/assets/57ac071c-2fd9-4c71-a300-cbcaa2e0da79" width="45%" controls></video>
</p>

## How it Works
### Image Processing:
1. The image is resized while maintaining its aspect ratio.
2. The pixel values are mapped to ASCII characters based on their brightness.
3. The resulting image is saved as a PNG file at `./PyASCII/output/PyAscii_image.png` or at a custom PATH defined by the `-o` flag.

### Video Processing:
1. The video is split into 5-second subclips.
2. Each subclip is processed into ASCII art frames.
3. Processed subclips are periodically merged to minimize the number of intermediate files.
4. The final video is generated by concatenating the processed subclips, with the original audio track added back.

## Project Structure
```bash
PyASCII.py          # Main script
sprite_sheet.png    # Sprite sheet used for ASCII art
PyASCII/
├── temp/           # Temporary directory for storing subclips
└── output/         # Directory for storing the final output
```

## Notes
- Make sure the sprite sheet ([sprite_sheet.png](./sprite_sheet.png)) is available in the script's directory.
- The script uses multi-processing to speed up video processing. By default, it executes `os.cpu_count() - 1` processes simultaneously. Adjust the number of parallel processes based on your CPU's capabilities.






