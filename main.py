import json
import shutil, glob, os, subprocess
import tkinter as tk
import ttkbootstrap as ttk

from tkinter import filedialog, messagebox
from logger import get_logger
from ttkbootstrap.constants import *


log = get_logger(__name__)

with open("config.json", "r") as config_file:
    config = json.load(config_file)

class App(ttk.Window):
    def __init__(self):
        super().__init__()
        self.title("SB2WAV")
        self.geometry("600x350")
        self.resizable(False, False)
        
        # Create a menu bar
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # Create a file menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Import", command=self.import_files)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)


        # Create theme menu
        # Dark themes
        self.theme_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.theme_menu.add_command(label="Dark", command=lambda: self.change_theme("darkly"))
        self.theme_menu.add_command(label="Solar", command=lambda: self.change_theme("solar"))
        self.theme_menu.add_command(label="Superhero", command=lambda: self.change_theme("superhero"))
        self.theme_menu.add_command(label="Cyborg", command=lambda: self.change_theme("cyborg"))
        self.theme_menu.add_command(label="Vapor", command=lambda: self.change_theme("vapor"))

        # Light themes
        self.menu_bar.add_cascade(label="Theme", menu=self.theme_menu)

        
        # Set style
        ttk.Style(config.get("theme", "darkly"))

        # Initiate a Listbox
        self.listbox = tk.Listbox(self)
        self.listbox.pack(expand=True, fill="both", padx=10, pady=10)

        #
        self.files = []

        # Initiate progress bar
        self.progress_bar = ttk.Progressbar(self,orient="horizontal", length=250, mode="determinate", bootstyle=SUCCESS)
        self.progress_bar.pack(side="bottom", pady=10)

        #
        self.create_widgets()



    def create_widgets(self):
        self.extract_button = ttk.Button(text="WEM to WAV", bootstyle=DARK,command=self.extract)
        self.extract_button.pack(side="bottom", pady=10)

        self.wem_button = ttk.Button(text="WAV to WEM", bootstyle=DARK,command=self.wav_to_wem)
        self.wem_button.pack(side="bottom", pady=10)

        self.scrollbar = ttk.Scrollbar(self.listbox, orient="vertical", bootstyle="light-round")
        self.scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)



    def change_theme(self, theme):
        ttk.Style(theme)
        config["theme"] = theme
        with open("config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)

    def update_listbox(self, item_index, file_name):
        self.listbox.delete(item_index)
        self.listbox.insert(item_index, f"{item_index}. {file_name} <---")

    def import_files(self):
        self.file_selected = filedialog.askopenfilenames()
        files = self.file_selected

        # Check if file doesnt have a .soundbank extension
        # for file in files:
        #     if not file.endswith(".soundbank"):
        #         messagebox.showerror("Error", "Please select a .soundbank file")
        #         return

        for count, value in enumerate(files):
            text = f"{count + 1}. {value.split('/')[-1]}"
            self.listbox.insert("end", text)

        self.files.append(files)


    def wav_to_wem(self):
        if len(self.files) == 0:
            messagebox.showerror("SB2WAV", "Please import a file")
            return

        progress = 0
        progress_max = len(self.files[0])
        self.progress_bar["maximum"] = progress_max
        for file in self.files:
            for f in file:
                if f.endswith(".wav"):
                    file_name = f.split("/")[-1]
                    log.info(f"Converting {file_name} to .wem")
                    subprocess.Popen(["bin/WemCompilerTool.exe", f], creationflags=(subprocess.CREATE_NO_WINDOW)).wait()
                    log.info(f"Converted {file_name} to .wem successfully")
                    
                    self.progress_bar["value"] = progress
                    self.progress_bar.update()
                    progress += 1

                else:
                    messagebox.showerror("SB2WAV", "Please select a .wav file")
                    return

        self.progress_bar["value"] = 0

        self.listbox.delete(0, "end")
        self.files.clear() 
        



    def extract(self):
        if len(self.files) == 0:
            messagebox.showerror("SB2WAV", "Please import a file")
            return

        progress = 0
        progress_max = len(self.files[0])
        self.progress_bar["maximum"] = progress_max
        for file in self.files:
            for f in file:
                if f.endswith(".wav"):
                    self.wav_to_wem(file)
                    return
                else:
                    self.update_listbox(file.index(f), f.split("/")[-1])
                    subprocess.Popen(["bin/riffext.exe", f], creationflags=(subprocess.CREATE_NO_WINDOW)).wait()
                    log.debug(f"Extracted {f}")


                    wem_files = glob.glob(f"{os.path.dirname(f)}/*.wem")
                    
                    for wem in wem_files:
                        subprocess.Popen(["bin/vgmstream/test.exe", wem], creationflags=(subprocess.CREATE_NO_WINDOW)).wait()
                        log.debug(f"Converted {wem} to .wav")

                        os.remove(wem)
                        log.debug(f"Deleted {wem}")

                    self.progress_bar["value"] = progress
                    self.progress_bar.update()
                    progress += 1
                    

            parent_directory = os.path.dirname(self.files[0][0])

            new_folder = parent_directory + "/extracted"

            if os.path.exists(new_folder):
                shutil.rmtree(new_folder)
            os.mkdir(new_folder)

        for file in glob.glob(f"{parent_directory}/*.wav"):
            shutil.move(file, new_folder)
            log.debug(f"Moved {file} to {new_folder}")


        self.progress_bar["value"] = 0

        self.listbox.delete(0, "end")
        self.files.clear()
        
        messagebox.showinfo("SB2WAV", "Conversion done")



        


if __name__ == "__main__":
    app = App()
    
    try:
        app.mainloop()
    except Exception as e:
        log.error(e)