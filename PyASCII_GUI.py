from PyASCII.PyASCII import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os

#### GUI ####
file_path = ""
def select_file():
    global file_path
    # Abrindo a janela para selecionar o arquivo
    file_path = filedialog.askopenfilename(title="Selecione um arquivo")
    
    if file_path:
        try:
            # Atualiza o Label com o caminho do arquivo selecionado
            path_label.config(text=file_path)
        
        except Exception as e:
            # Exibindo uma mensagem de erro
            messagebox.showerror("Erro", f"Ocorreu um erro ao processar o arquivo: {e}")
    else:
        messagebox.showwarning("Aviso", "Nenhum arquivo foi selecionado.")

def validate_numeric_input(P):
    # Verifica se a entrada é vazia ou se é um número inteiro
    if P.isdigit() or P == "":
        return True
    else:
        return False
    
def on_go():
    start_time = time()

    resolution = int(entry.get())
    filt = selected_option.get()
    contrast = contrast_var.get()

    try:
        sprite_sheet_image = Image.open("./sprite_sheet.png")
        sprite_height = 8
        sprite_width = 8
        sprites = load_sprites(sprite_sheet_image, sprite_width, sprite_height, filt)
    except FileNotFoundError:
        print("[ FileNotFoundError ] Sprite Sheet not found!")

    if is_gif(file_path):
        gif_processing(gif_name=file_path,
                       resolution=resolution,
                       high_contrast=contrast,
                       sprites=sprites,
                       output_file=None)
    elif is_image(file_path):
        image_processing(image_name=file_path,
                        resolution=resolution,
                        high_contrast=contrast,
                        sprites=sprites,
                        output_file=None)
    elif is_video(file_path):
        video_processing(video_name=file_path,
                        resolution=resolution,
                        high_contrast=contrast,
                        sprites=sprites,
                        output_file=None)
    else:
        print("Invalid media format!")
        exit()

    end_time = time()
    execution_time = end_time - start_time
    messagebox.showinfo(
        "Success!",
        f"The processed file is at {os.path.join(os.getcwd(), os.path.normpath('PyASCII/output/'))}\n"
        f"Execution time: {round(execution_time, ndigits=2)} seconds"
    )
    
if __name__ == "__main__":
    root = tk.Tk()
    root.title("PyASCII")
    root.geometry("261x361")

    # Frame para alinhar os widgets à esquerda
    left_frame = tk.Frame(root)
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

    # Configurando as linhas e colunas do grid para expandir com a janela
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    btn_media = tk.Button(left_frame, text="Select an Image/Video", command=select_file)
    btn_media.grid(row=0, column=0, padx=10, pady=10, sticky='w')

    path_label = tk.Label(left_frame, text="", wraplength=250)  # wraplength ajusta o texto para não sair da janela
    path_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

    resolution_label = tk.Label(left_frame, text="Resolution", font=("Helvetica", 10, "bold"))
    resolution_label.grid(row=2, column=0, padx=10, pady=(5, 0), sticky='w')

    entry = tk.Entry(left_frame, validate='key', validatecommand=(root.register(validate_numeric_input), '%P'))
    entry.grid(row=3, column=0, padx=10, pady=5, sticky='w')

    filters_label = tk.Label(left_frame, text="Filters", font=("Helvetica", 10, "bold"))
    filters_label.grid(row=4, column=0, padx=10, pady=(5, 0), sticky='w')

    options = list(load_filters().keys())
    selected_option = tk.StringVar(root)
    selected_option.set(options[0])  # Definindo a primeira opção como padrão

    option_menu = tk.OptionMenu(left_frame, selected_option, *options)
    option_menu.grid(row=5, column=0, padx=10, pady=5, sticky='w')

    contrast_var = tk.BooleanVar()
    contrast_check = tk.Checkbutton(left_frame, text="High Contrast", variable=contrast_var)
    contrast_check.grid(row=6, column=0, padx=10, pady=5, sticky='w')

    btn_go = tk.Button(left_frame, text="Go!", command=on_go)
    btn_go.grid(row=7, column=0, padx=10, pady=20)

    left_frame.grid_rowconfigure(7, weight=1)  # Permite que a linha do botão expanda
    left_frame.grid_columnconfigure(0, weight=1)  # Permite que a coluna do botão expanda

    root.mainloop()