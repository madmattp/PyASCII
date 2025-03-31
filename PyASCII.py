#!/usr/bin/env python3

from PIL import Image, Image, ImageEnhance
from moviepy.editor import VideoFileClip, ImageSequenceClip
import time
from multiprocessing import Process, Manager
import numpy as np
import cv2
import argparse
import tomllib
from pathlib import Path
from io import BytesIO
import sys


def load_filters() -> dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]]:
    default_filters = {
        "Orange": ((252, 176, 32), (10, 6, 3)),
        "Capuccino": ((200, 185, 150), (61, 49, 40)),
        "Brat": ((137, 205, 0), (0, 0, 0)),
        "Fairy": ((174, 255, 223), (90, 84, 117)),
        "Bloody": ((255, 42, 0), (43, 12, 0)),
        "Lavender": ((196, 167, 231), (35, 33, 54)),
        "Cyan": ((0, 204, 255), (0, 34, 43)),
        "Vapor": ((250, 185, 253), (75, 123, 222)),
        "Matrix": ((0, 255, 0), (0, 39, 6)),
        "ObraDinn": ((229, 255, 254), (51, 51, 25))
    }

    try:
        with open('filters.toml', 'rb') as file:
            filters = tomllib.load(file)
        return filters
    
    except FileNotFoundError:
        print("[FileNotFoundError] The 'filters.toml' file not found. Using default filter pack...")
        return default_filters
    
    except tomllib.TOMLDecodeError as e:
        print(f"[TOMLDecodeError] Error parsing the TOML file: {e}\n Using default filter pack...")
        return default_filters
    
def load_sprites(sprite_sheet_image: Image, sprite_width: int, sprite_height: int, monochrome_filter: tuple) -> list:
    # Função para obter um sprite individual
    def get_sprite(x: int, y: int):
        sprite = sprite_sheet_image.crop((x, y, x + sprite_width, y + sprite_height))
        return sprite
    
    sheet_width, sheet_height = sprite_sheet_image.size
    filters = load_filters()
    
    if monochrome_filter != None:
        if monochrome_filter not in filters:
            print(f"[ KeyError ] '{monochrome_filter}' is not recognized as a filter!")
            exit()

        for y in range(0, sheet_height):
            for x in range(0, sheet_width):
                pixel_value = sprite_sheet_image.getpixel((x, y))
                if pixel_value == (255, 255, 255, 255):
                    sprite_sheet_image.putpixel((x, y), tuple(filters[monochrome_filter][0]))
                else:
                    sprite_sheet_image.putpixel((x, y), tuple(filters[monochrome_filter][1]))
    
    sprites = []
    for y in range(0, sprite_sheet_image.height, sprite_height):
        for x in range(0, sprite_sheet_image.width, sprite_width):
            sprite = get_sprite(x, y)
            sprites.append(sprite)

    return sprites

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.description = f"{parser.prog}. An ASCII filter for images and videos."

    parser.add_argument('-i', '--input', metavar='PATH', required=True, help='Specifies the image/video to be used as input.')
    parser.add_argument('-f', '--filter', metavar='FILTER', default=None, choices=list(load_filters().keys()), help='Applies a color filter to the output image.')
    parser.add_argument('-s', '--sharpness', metavar='FACTOR', type=float, default=1, help="Adjusts the sharpness of the image. Default is 1.")
    parser.add_argument('-c', '--contrast', metavar='FACTOR', type=float, default=1, help='Adjusts the contrast of the image. Default is 1.')
    parser.add_argument('-r', '--resolution', metavar='RES', default=720, type=int, help='Sets the resolution of the output image.')
    parser.add_argument('-o', '--output', metavar='PATH', default=None, help='Specifies the output file path. If not set, a default name will be used.')
    parser.add_argument('-t', '--threads', metavar='INTEGER', type=int, default=1, help='Specifies the number of threads to use for parallel processing. Default is 1.')

    args = parser.parse_args()
    return args


# Muda a resolução da imagem sem perder a proporção
def resize_image(image: Image, ref_size: int) -> Image:
    rows, cols = image.size
    if rows < cols:
        cols = int((cols / rows) * ref_size)
        rows = ref_size
    elif rows == cols:
        cols = ref_size
        rows = ref_size
    else:
        rows = int((rows / cols) * ref_size)
        cols = ref_size
    return image.resize((rows, cols), Image.LANCZOS)

def sharpen(image: Image, factor: float) -> Image:
    if factor > 1:
        enhancer = ImageEnhance.Sharpness(image)
        sharp_image = enhancer.enhance(factor)
        return sharp_image
    return image

# Transformar o valor do pixel de 0 a 255 em 0 a 16
def pixel_value_to_index(pixel_value) -> int:
    return int((pixel_value / 255) * 16)

def image_processing(image_path: Path, sprites: list, contrast: float, sharpness: float, resolution: int) -> Image:
    with Image.open(image_path).convert('L') as image:
        image = resize_image(image, resolution)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(factor=contrast)
        sharp_image = sharpen(image=image, factor=sharpness)
        
    image = sharp_image
    
    output_width, output_height = image.size
    with Image.new("RGB", (output_width, output_height)) as output_image:
        for y in range(0, output_height, sprite_height):
            for x in range(0, output_width, sprite_width):
                pixel_value = image.getpixel((x, y))
                index = pixel_value_to_index(pixel_value)
                sprite = sprites[index]
                output_image.paste(sprite, (x, y))   

    return output_image

def video_processing(video_path: Path, threads: int, sprites: list, contrast: float, sharpness: float, resolution: int) -> VideoFileClip:
    def frame_processing(image: Image, sprites: list, contrast: float, sharpness: float, resolution: int) -> np.array:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(factor=contrast)
        sharp_image = sharpen(image=image, factor=sharpness)
        downscaled_image = resize_image(sharp_image, resolution)
        image = downscaled_image.convert("L")

        output_width, output_height = downscaled_image.size
        with Image.new("RGB", (output_width, output_height)) as output_image:
            for y in range(0, output_height, sprite_height):
                for x in range(0, output_width, sprite_width):
                    pixel_value = image.getpixel((x, y))
                    index = pixel_value_to_index(pixel_value)
                    sprite = sprites[index]
                    output_image.paste(sprite, (x, y))   

            return np.array(output_image)

    def process_clip(index, sprites, all_processed_frames, frames, contrast, sharpness, downscale_pot) -> None:
        processed_frames = []
        for frame in frames:
            frame = Image.fromarray(frame)
            processed_frame = frame_processing(frame, sprites, contrast, sharpness, downscale_pot)
            processed_frames.append(processed_frame)

        all_processed_frames[index] = processed_frames

    video = VideoFileClip(filename=video_path, audio=False)
    audio_clip = video.audio
    fps = video.fps

    duration_per_process = video.duration / threads
    manager = Manager()
    all_processed_frames = manager.dict()
    procs = []

    for i in range(threads):
        start = i * duration_per_process
        end = min((i + 1) * duration_per_process, video.duration)

        subclip = video.subclip(start, end)
        frames = [frame for frame in subclip.iter_frames()]
        proc = Process(target=process_clip, args=(i, sprites, all_processed_frames, frames, contrast, sharpness, resolution))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

    all_processed_frames = dict(sorted(all_processed_frames.items()))
    all_processed_frames = [frame for sublist in all_processed_frames.values() for frame in sublist]
    final_clip = ImageSequenceClip(all_processed_frames, fps=fps)
    final_clip = final_clip.set_audio(audio_clip)
    
    return final_clip

def gif_processing(gif_path: Path, sprites: list, contrast: float, sharpness: float, resolution: int) -> BytesIO:
    gif = Image.open(gif_path)
    frames = []
    durations = []

    for frame in range(0, gif.n_frames):
        gif.seek(frame)
        image = gif.convert("L")
        image = resize_image(image, resolution)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
        image = sharpen(image=image, factor=sharpness)
        
        output_width, output_height = image.size
        output_image = Image.new("RGB", (output_width, output_height))
        for y in range(0, output_height, sprite_height):
            for x in range(0, output_width, sprite_width):
                pixel_value = image.getpixel((x, y))
                index = pixel_value_to_index(pixel_value)
                sprite = sprites[index]
                output_image.paste(sprite, (x, y))

        frames.append(output_image)
        durations.append(gif.info['duration'])

    gif_buffer = BytesIO()
    frames[0].save(gif_buffer ,format="GIF", save_all=True, append_images=frames[1:], loop=0, duration=durations)
    gif_buffer.seek(0)

    return gif_buffer
    
def is_image(file_path: Path) -> bool:
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except (IOError, SyntaxError):
        return False

def is_video(file_path: Path) -> bool:
    try:
        video = cv2.VideoCapture(file_path)
        if video.isOpened():
            return True
        return False
    except Exception as e:
        return False
    finally:
        video.release()

def is_gif(file_path: Path) -> bool: 
    try:
        with Image.open(file_path) as img:
            print(img.format)
            if img.format == 'GIF':
                return True
        return False
    except (IOError, SyntaxError):
        return False


# Argument Parsing... 
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.description = f"{parser.prog}. An ASCII filter for images and videos."

    parser.add_argument('-i', '--input', metavar='PATH', required=True, help='Specifies the image/video to be used as input.')
    parser.add_argument('-f', '--filter', metavar='FILTER', default=None, choices=list(load_filters().keys()), help='Applies a color filter to the output image.')
    parser.add_argument('-s', '--sharpness', metavar='FACTOR', type=float, default=1, help="Adjusts the sharpness of the image.")
    parser.add_argument('-c', '--contrast', metavar='FACTOR', type=float, default=1, help='Adjusts the contrast of the image.')
    parser.add_argument('-r', '--resolution', metavar='RES', default=720, type=int, help='Sets the resolution of the output image.')
    parser.add_argument('-o', '--output', metavar='PATH', default=None, help='Specifies the output file path. If not set, a default name will be used.')
    parser.add_argument('-t', '--threads', metavar='INTEGER', type=int, default=1, help='Specifies the number of threads to use for parallel processing.')

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    start_time = time.time()
    
    args = parse_arguments()

    filters = load_filters()
    filter_chosen = filters[args.filter] if args.filter is not None else None

    try:
        sprite_sheet_image = Image.open("./sprite_sheet.png")
        sprite_height = 8
        sprite_width = 8
        sprites = load_sprites(sprite_sheet_image=sprite_sheet_image,
                            sprite_width=sprite_width,
                            sprite_height=sprite_height,
                            monochrome_filter=filter_chosen)
    except FileNotFoundError:
        print("[ FileNotFoundError ] Sprite Sheet not found!")


    try:
        if is_gif(file_path=args.input):
            gif_buffer = gif_processing(gif_path=args.input,
                        sprites=sprites,
                        contrast=args.contrast,
                        sharpness=args.sharpness,
                        resolution=args.resolution)
            with open("PyASCII_Gif.gif", "wb") as f:
                f.write(gif_buffer.getvalue())

        elif is_image(file_path=args.input):
            ascii_image = image_processing(image_path=args.input,
                        sprites=sprites,
                        contrast=args.contrast,
                        sharpness=args.sharpness,
                        resolution=args.resolution)
            output_file = args.output if args.output is not None else "PyASCII_Image.png"
            ascii_image.save(output_file)

        elif is_video(file_path=args.input):
            ascii_video = video_processing(video_path=args.input,
                        threads=args.threads,
                        sprites=sprites,
                        contrast=args.contrast,
                        sharpness=args.sharpness,
                        resolution=args.resolution)
            output_file = args.output if args.output is not None else "PyASCII_Video.mp4"
            ascii_video.write_videofile(output_file, codec="libx264")
    
    except ValueError:
        print(f"[ ValueError ] Input file does not have a valid format!")
        sys.exit(1)
            
    except FileNotFoundError:
        print(f"[ FileNotFoundError ] Input file {args.input} not found!")
        sys.exit(1)

    end_time = time.time() 
    execution_time = end_time - start_time  
    print(f"Processing time: {execution_time:.4f} seconds")