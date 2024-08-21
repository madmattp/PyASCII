#!/usr/bin/env python3

from PIL import Image, ImageOps
from moviepy.editor import VideoFileClip, concatenate_videoclips
from time import time
from multiprocessing import Process
from threading import Thread
import numpy as np
import cv2
import os
import re
import argparse
import tomllib

if (not os.path.exists('PyASCII/output')):
    os.makedirs('PyASCII/output')
if (not os.path.exists('PyASCII/temp')):
    os.makedirs('PyASCII/temp')
else:
    for file in os.listdir("PyASCII/temp"):
        file_path = os.path.join("PyASCII/temp", file)
        if os.path.isfile(file_path):
            os.remove(file_path)

def load_filters():
    with open('filters.toml', 'rb') as file:
        filters = tomllib.load(file)
    return filters

#### Image Tools ####

# Muda a resolução da imagem sem perder a proporção
def resize_image(image, ref_size):
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

# Transformar o valor do pixel de 0 a 255 em 0 a 16
def pixel_value_to_index(pixel_value):
    return int((pixel_value / 255) * 16)

def image_processing(image_name, resolution, high_contrast, sprites, output_file):
    image = Image.open(image_name).convert("L")
    image = resize_image(image, resolution)
    if high_contrast:
        image = ImageOps.equalize(image)
    output_width, output_height = image.size

    output_image = Image.new("RGB", (output_width, output_height))
    for y in range(0, output_height, sprite_height):
        for x in range(0, output_width, sprite_width):
            pixel_value = image.getpixel((x, y))
            index = pixel_value_to_index(pixel_value)
            sprite = sprites[index]
            output_image.paste(sprite, (x, y))

    # Salva a imagem final como png
    if output_file != None:
        output_image.save(f"{output_file}")
    else:
        output_image.save("./PyASCII/output/PyAscii_image.png")

##### GIF Tools #####

def gif_processing(gif_name, resolution, high_contrast, sprites, output_file):
    gif = Image.open(gif_name)
    frames = []
    durations = []

    for frame in range(0, gif.n_frames):
        gif.seek(frame)
        image = gif.convert("L")
        image = resize_image(image, resolution)
        if high_contrast:
            image = ImageOps.equalize(image)

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

    if output_file != None:
        frames[0].save(output_file, save_all=True, append_images=frames[1:], duration=durations, loop=0)
    else:
        frames[0].save("./PyASCII/output/PyAscii_gif.gif", save_all=True, append_images=frames[1:], duration=durations, loop=0)


##### Video Tools #####

def extrair_frames(input_video_path):
    cap = cv2.VideoCapture(input_video_path)
    frames = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    
    cap.release()
    return frames

# Função para salvar frames como um novo vídeo
def salvar_frames(frames, output_path, fps):
    height, width, layers = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # ou 'XVID' para .avi
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame in frames:
        video.write(frame)
    
    video.release()

def load_sprites(sprite_sheet_image, sprite_width, sprite_height, monochrome_filter):
    # Função para obter um sprite individual
    def get_sprite(x, y):
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

# Função para processar cada subclipe
def process_subclip(sprites, subclip, ct, ref, high_contrast):
    frames = extrair_frames(subclip)
    fps = cv2.VideoCapture(subclip).get(cv2.CAP_PROP_FPS)

    for i in range(len(frames)):
        # Carregar a imagem em escala de cinza
        image = Image.fromarray(cv2.cvtColor(frames[i], cv2.COLOR_BGR2RGB)).convert("L")
        image = resize_image(image, ref)
        if high_contrast:
            image = ImageOps.equalize(image) # Equaliza a imagem (aumenta contraste)
        output_width, output_height = image.size

        output_image = Image.new("RGB", (output_width, output_height))
        for y in range(0, output_height, sprite_height):
            for x in range(0, output_width, sprite_width):
                pixel_value = image.getpixel((x, y))
                index = pixel_value_to_index(pixel_value)
                sprite = sprites[index]
                output_image.paste(sprite, (x, y))

        frames[i] = cv2.cvtColor(np.array(output_image), cv2.COLOR_RGB2BGR)

    os.remove(f"./PyASCII/temp/subclip_{ct}.mp4") # Deleta subclipe antigo

    height, width, layers = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # ou 'XVID' para .avi
    video = cv2.VideoWriter(f"./PyASCII/temp/processed_subclip{ct}.mp4", fourcc, fps, (width, height))
    
    for frame in frames:
        video.write(frame)
    
    video.release()

def get_numeric_part(filename):
    # Extrai a parte numérica do nome do arquivo
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')

def video_processing(video_name, resolution, high_contrast, sprites, output_file):
    video = VideoFileClip(filename=video_name, audio=False)
    ref = resolution

    time_frag = 5  # Tempo em segundos de cada subclipe

    index = 0
    start = 0
    qtd_procs = 0    # Variável utilizada para mensurar a quantidade de processos simultâneos, Não deve ultrapassar os.cpu_count()!!!
    ct = 0           # Contador de subclipe
    frag_counter = 0 # Variável para representar o frag{}.mp4 (conjunto de subclipes)
    while(True):
        while(qtd_procs < (os.cpu_count() - 1)):
            if start + time_frag >= video.duration:
                end = video.duration
                clip = video.subclip(start, end)
                clip.write_videofile(f"./PyASCII/temp/subclip_{index}.mp4")
                break
            else:
                end = start + time_frag
                clip = video.subclip(start, end)
                clip.write_videofile(f"./PyASCII/temp/subclip_{index}.mp4")
                start += time_frag
            index += 1
            qtd_procs += 1
        
        files = sorted([os.path.join("PyASCII/temp", f) for f in os.listdir("PyASCII/temp") if f.startswith('subclip')], key=get_numeric_part)
        procs = []
        
        for subclip in files:
            if os.name == "nt": # Windows (Existe um bug envolvendo a leitura dos arquivos temporários quando Process() é utilizado no Windows, então foi necessário o uso de Thread())
                proc = Thread(target=process_subclip, args=(sprites, subclip, ct, ref, high_contrast))
            elif os.name == "posix": # Linux
                proc = Process(target=process_subclip, args=(sprites, subclip, ct, ref, high_contrast))
            procs.append(proc)
            proc.start()
            ct += 1

        for proc in procs:
            proc.join()  

        files = [os.path.join("PyASCII/temp", f) for f in os.listdir("PyASCII/temp") if f.startswith('processed_subclip')]
        clips = [VideoFileClip(f) for f in sorted(files, key=get_numeric_part)]
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(f'./PyASCII/temp/frag{frag_counter}.mp4', codec='libx264')
        frag_counter += 1

        for file in files:
            os.remove(file) # Remove os subclipes temporários

        if end == video.duration:
            break

        qtd_procs = 0
    video.close()

    # Une subclipes em um único clipe (sem áudio)
    files = [os.path.join("PyASCII/temp", f) for f in os.listdir("PyASCII/temp") if f.startswith('frag')]
    clips = [VideoFileClip(f) for f in sorted(files, key=get_numeric_part)]
    final_clip = concatenate_videoclips(clips)
    if output_file == None:
        output_video_path = './PyASCII/output/PyASCII_noaudio.mp4'
    else:
        output_video_path = f"{output_file}_NoAudio.mp4"
    final_clip.write_videofile(output_video_path, codec='libx264')

    files = [os.path.join("PyASCII/temp", f) for f in os.listdir("PyASCII/temp") if os.path.isfile(os.path.join("PyASCII/temp", f))]
    for file in files:
        os.remove(file) # Remove os subclipes temporários

    input_video_path = video_name
    video_clip = VideoFileClip(input_video_path)
    audio_clip = video_clip.audio
    final_video = VideoFileClip(output_video_path)
    final_video_with_audio = final_video.set_audio(audio_clip)
    if output_file == None:
        final_output_path = './PyASCII/output/PyASCII.mp4'
    else:
        final_output_path = output_file
    final_video_with_audio.write_videofile(final_output_path, codec='libx264', audio_codec='aac')

# Argument Parsing... 
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.description = f"{parser.prog}. An ASCII filter for images and videos."

    parser.add_argument('-r', '--resolution', metavar='RES', default=720, type=int, help='Sets the resolution of the output image.')
    parser.add_argument('-f', '--filter', metavar='FILTER', default=None,
                        choices=list(load_filters().keys()), help='Applies a filter to the output.')
    parser.add_argument('-m', '--media', metavar='MEDIA', required=True, help='Specifies the image/video to be used as input.')
    parser.add_argument("-c", "--contrast", action='store_true', help='Increases image contrast.')
    parser.add_argument("-o", "--output", metavar="PATH", default=None, help='Changes the output path.')

    args = parser.parse_args()
    return args

def is_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except (IOError, SyntaxError):
        return False

def is_video(file_path):
    try:
        video = cv2.VideoCapture(file_path)
        if video.isOpened():
            return True
        return False
    except Exception as e:
        return False
    finally:
        video.release()

def is_gif(file_path):
    try:
        with Image.open(file_path) as img:
            if img.format == 'GIF':
                return True
        return False
    except (IOError, SyntaxError):
        return False


if __name__ == "__main__":
    start_time = time()

    args = parse_arguments()

    try:
        resolution = int(args.resolution)
        sprite_sheet_image = Image.open("./sprite_sheet.png")
        sprite_height = 8
        sprite_width = 8
        sprites = load_sprites(sprite_sheet_image, sprite_width, sprite_height, args.filter)
    except FileNotFoundError:
        print("[ FileNotFoundError ] Sprite Sheet not found!")


    if is_gif(args.media):
        gif_processing(gif_name=args.media,
                       resolution=resolution,
                       high_contrast=args.contrast,
                       sprites=sprites,
                       output_file=args.output)
    elif is_image(args.media):
        image_processing(image_name=args.media,
                         resolution=resolution,
                         high_contrast=args.contrast,
                         sprites=sprites,
                         output_file=args.output)
    elif is_video(args.media):
        video_processing(video_name=args.media,
                         resolution=resolution,
                         high_contrast=args.contrast,
                         sprites=sprites,
                         output_file=args.output)
    else:
        print("Invalid media format!")
        exit()

    end_time = time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")
