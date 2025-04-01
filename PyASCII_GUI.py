from PyASCII import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
from time import time

#### GUI ####
file_path = ""
def select_file():
    global file_path
    file_path = filedialog.askopenfilename(title="Select a File.")
    
    if file_path:
        try:
            path_label.config(text=file_path)
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing the file: {e}")

    else:
        messagebox.showwarning("Warning", "No file was selected.")

def validate_numeric_input(P):
    if P.isdigit() or P == "":
        return True
    else:
        return False
    
def on_go():
    start_time = time()

    resolution = int(entry_resolution.get())
    filt = selected_option.get()
    if filt == 'Default':
        filt = None
    contrast = float(contrast_spinbox.get())
    sharpness = float(sharpness_spinbox.get())
    threads = int(threads_slider.get())
    output_path =  None if entry_output.get() == "" else entry_output.get()

    try:
        sprite_sheet_image = Image.open("./sprite_sheet.png")
        global sprite_height, sprite_width
        sprite_height = 8
        sprite_width = 8
        sprites = load_sprites(sprite_sheet_image=sprite_sheet_image,
                            sprite_width=sprite_width,
                            sprite_height=sprite_height,
                            monochrome_filter=filt)
    except FileNotFoundError:
        messagebox.showerror("FileNotFoundError", "Sprite Sheet 'sprite_sheet.png' not found!")
        return

    try:
        if is_gif(file_path=file_path):
            gif_buffer = gif_processing(gif_path=file_path,
                        sprites=sprites,
                        contrast=contrast,
                        sharpness=sharpness,
                        resolution=resolution)
            output_file = output_path if output_path is not None else "PyASCII_Gif.gif"
            with open(output_file, "wb") as f:
                f.write(gif_buffer.getvalue())

        elif is_image(file_path=file_path):
            ascii_image = image_processing(image_path=file_path,
                        sprites=sprites,
                        contrast=contrast,
                        sharpness=sharpness,
                        resolution=resolution)
            output_file = output_path if output_path is not None else "PyASCII_Image.png"
            ascii_image.save(output_file)

        elif is_video(file_path=file_path):
            ascii_video = video_processing(video_path=file_path,
                        threads=threads,
                        sprites=sprites,
                        contrast=contrast,
                        sharpness=sharpness,
                        resolution=resolution)
            output_file = output_path if output_path is not None else "PyASCII_Video.mp4"
            ascii_video.write_videofile(output_file, codec="libx264")

        end_time = time() 
        execution_time = end_time - start_time  
        messagebox.showinfo("Success!", f"Processing time: {execution_time:.4f} seconds")
    
    except ValueError:
        messagebox.showerror("ValueError", "Input file does not have a valid format!")
        sys.exit(1)
            
    except FileNotFoundError:
        messagebox.showerror("FileNotFoundError", f"Input file {file_path} not found!")
        sys.exit(1)

    
    
if __name__ == "__main__":
    filters = load_filters()
    filters['Default'] = None

    root = tk.Tk()
    root.title("PyASCII")
    root.geometry("300x520")

    # Frame para alinhar os widgets à esquerda
    left_frame = tk.Frame(root)
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Botão de seleção de arquivo
    btn_media = tk.Button(left_frame, text="Select an Image/Video", command=select_file)
    btn_media.grid(row=0, column=0, padx=10, pady=10, sticky='w')

    # Caminho do arquivo selecionado
    path_label = tk.Label(left_frame, text="", wraplength=250)
    path_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

    # Resolução
    resolution_label = tk.Label(left_frame, text="Resolution", font=("Helvetica", 10, "bold"))
    resolution_label.grid(row=2, column=0, padx=10, pady=(5, 0), sticky='w')

    entry_resolution = tk.Entry(left_frame, validate='key', validatecommand=(root.register(validate_numeric_input), '%P'))
    entry_resolution.grid(row=3, column=0, padx=10, pady=5, sticky='w')

    # Filtros
    filters_label = tk.Label(left_frame, text="Filters", font=("Helvetica", 10, "bold"))
    filters_label.grid(row=4, column=0, padx=10, pady=(5, 0), sticky='w')

    options = list(filters.keys())
    selected_option = tk.StringVar(root)
    selected_option.set(options[10])

    option_menu = tk.OptionMenu(left_frame, selected_option, *options)
    option_menu.grid(row=5, column=0, padx=10, pady=5, sticky='w')

    # Contraste com Spinbox
    contrast_label = tk.Label(left_frame, text="Contrast (1.0 - 2.0)", font=("Helvetica", 10, "bold"))
    contrast_label.grid(row=6, column=0, padx=10, pady=(5, 0), sticky='w')

    contrast_spinbox = tk.Spinbox(left_frame, from_=1.0, to=2.0, increment=0.1)
    contrast_spinbox.grid(row=7, column=0, padx=10, pady=5, sticky='w')

    # Sharpness com Spinbox
    sharpness_label = tk.Label(left_frame, text="Sharpness (1.0 - 2.0)", font=("Helvetica", 10, "bold"))
    sharpness_label.grid(row=8, column=0, padx=10, pady=(5, 0), sticky='w')

    sharpness_spinbox = tk.Spinbox(left_frame, from_=1.0, to=2.0, increment=0.1)
    sharpness_spinbox.grid(row=9, column=0, padx=10, pady=5, sticky='w')

    # Threads com Slider
    threads_label = tk.Label(left_frame, text="Threads", font=("Helvetica", 10, "bold"))
    threads_label.grid(row=10, column=0, padx=10, pady=(5, 0), sticky='w')

    threads_slider = tk.Scale(left_frame, from_=1, to=os.cpu_count(), resolution=1, orient="horizontal")
    threads_slider.grid(row=11, column=0, padx=10, pady=5, sticky='w')

    # Saída
    output_label = tk.Label(left_frame, text="Output Path", font=("Helvetica", 10, "bold"))
    output_label.grid(row=12, column=0, padx=10, pady=(5, 0), sticky='w')

    entry_output = tk.Entry(left_frame)
    entry_output.grid(row=13, column=0, padx=10, pady=5, sticky='w')

    # Botão de execução
    btn_go = tk.Button(left_frame, text="Go!", command=on_go)
    btn_go.grid(row=14, column=0, padx=10, pady=20)

    left_frame.grid_rowconfigure(14, weight=1)
    left_frame.grid_columnconfigure(0, weight=1)

    root.mainloop()