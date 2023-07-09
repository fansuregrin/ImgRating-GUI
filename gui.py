import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox

from utils import is_image_file
from config import Config


class ImageRatingGUI:
    def __init__(self, config: Config):
        self.root = tk.Tk()
        self.root.title("Image Rating")

        self.original_folder = config.ORIGINAL_FOLDER
        self.enhanced_folder = config.ENHANCED_FOLDER

        self.process_imgs_data()
        self.scores = pd.DataFrame(
            data = [[None] * self.enhance_method_num for _ in range(self.imgs_num)],
            index = self.imgs_names,
            columns = self.enhanced_methods
        )

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.info_frame = tk.Frame(self.root, bd=2, relief="solid")
        self.info_frame.pack(side=tk.TOP)
        self.total_img_num_label = tk.Label(self.info_frame, text=f"Total images number: {self.imgs_num}")
        self.total_img_num_label.pack(side=tk.TOP)
        self.total_method_num_label = tk.Label(self.info_frame, text=f"Total methods number: {self.enhance_method_num}")
        self.total_method_num_label.pack(side=tk.TOP)
        self.current_progress_label = tk.Label(self.info_frame)
        self.current_progress_label.pack(side=tk.TOP)
        
        self.img_frame = tk.Frame(self.root)
        self.img_frame.pack()
        self.img_frame_left = tk.Frame(self.img_frame)
        self.img_frame_left.pack(pady=10, side=tk.LEFT)
        self.img_frame_right = tk.Frame(self.img_frame)
        self.img_frame_right.pack(pady=10, side=tk.RIGHT)

        self.left_img_label = tk.Label(self.img_frame_left, text="Original Image")
        self.left_img_label.pack(side=tk.TOP, pady=10)
        self.left_img_name = tk.Label(self.img_frame_left)
        self.left_img_name.pack(side=tk.TOP)
        self.left_img_widget = tk.Label(self.img_frame_left)
        self.left_img_widget.pack(side=tk.LEFT)
        self.right_img_label = tk.Label(self.img_frame_right, text="Enhanced Image")
        self.right_img_label.pack(side=tk.TOP, pady=10)
        self.right_img_name = tk.Label(self.img_frame_right)
        self.right_img_name.pack(side=tk.TOP)
        self.right_img_widget = tk.Label(self.img_frame_right)
        self.right_img_widget.pack(side=tk.LEFT)

        self.score_frame = tk.Frame(self.root)
        self.score_frame.pack(pady=(5, 10), side=tk.BOTTOM)
        
        self.score_label = tk.Label(self.score_frame, text="Score:")
        self.score_label.grid(row=0, column=0)
        
        scores_values = [i+1 for i in range(config.RATING_LEVELS)]
        self.score_combo = Combobox(self.score_frame, values=scores_values)
        self.score_combo.current(0)
        self.score_combo.bind("<<ComboboxSelected>>", self.save_score)
        self.score_combo.grid(row=0, column=1, columnspan=5)

        self.score_info = tk.Label(self.score_frame, text=config.RATING_INFO)
        self.score_info.grid(row=1, column=0, columnspan=5)
        
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10, side=tk.BOTTOM)
        
        self.save_button = tk.Button(self.button_frame, text='Save to file', command=self.save_scores_to_file)
        self.save_button.pack(side=tk.LEFT)
        
        self.prev_button = tk.Button(self.button_frame, text="Previous", command=self.show_previous)
        self.prev_button.pack(side=tk.LEFT, padx=(40, 5))
        
        self.next_button = tk.Button(self.button_frame, text="Next", command=self.show_next)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.current_img_idx = 0
        self.current_pair_idx = 0
    
    def run(self):
        self.show_image()
        self.root.mainloop()

    def on_closing(self):
        if messagebox.askyesno("Saving Notice", "Whether to save the current scores data?"):
            if not self.save_scores_to_file():
                return
        self.root.destroy()

    def process_imgs_data(self):
        enhanced_folder_list = []
        enhanced_methods = []
        for itemname in os.listdir(self.enhanced_folder):
            itempath = os.path.join(self.enhanced_folder, itemname)
            if os.path.isdir(itempath):
                enhanced_folder_list.append(itempath)
                enhanced_methods.append(itemname)
        enhanced_folder_list.sort()
        enhanced_methods.sort()

        original_paths = self.get_imgs_paths(self.original_folder)
        enhanced_paths_group = [self.get_imgs_paths(folder) for folder in enhanced_folder_list]
        assert all( len(original_paths) == len(enhanced) for enhanced in enhanced_paths_group)
        assert len(original_paths) != 0
        self.original_paths = original_paths
        self.enhanced_paths_group = enhanced_paths_group
        self.enhanced_methods = enhanced_methods
        self.enhance_method_num = len(self.enhanced_methods)
        self.imgs_names = [os.path.basename(p) for p in self.original_paths]
        self.imgs_num = len(self.imgs_names)

    def get_imgs_paths(self, folder):
        imgs_paths = []
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if is_image_file(filepath):
                imgs_paths.append(filepath)
        imgs_paths.sort()
        return imgs_paths
    
    def show_image(self):
        original_img_path = self.original_paths[self.current_img_idx]
        original_img_name = self.imgs_names[self.current_img_idx]
        enhanced_img_path = self.enhanced_paths_group[self.current_pair_idx][self.current_img_idx]
        enhanced_img_name = "{} ({})".format(self.imgs_names[self.current_img_idx], self.enhanced_methods[self.current_pair_idx])
        
        left_img = tk.PhotoImage(file=original_img_path)
        self.left_img_widget.configure(image=left_img)
        self.left_img_widget.image = left_img
        self.left_img_name.configure(text=original_img_name)

        right_img = tk.PhotoImage(file=enhanced_img_path)
        self.right_img_widget.configure(image=right_img)
        self.right_img_widget.image = right_img
        self.right_img_name.configure(text=enhanced_img_name)

        self.current_progress_label.configure(text="Current progress: {:d}/{:d}".format(
            self.get_current_progress(),
            self.imgs_num * self.enhance_method_num
        ))
    
    def get_current_progress(self):
        return self.current_img_idx * self.enhance_method_num + self.current_pair_idx + 1
    
    def show_next(self):
        self.save_score()
        
        if self.current_pair_idx < self.enhance_method_num - 1:
            self.current_pair_idx += 1
            self.score_combo.set(1)
            self.show_image()
        else:
            if self.current_img_idx < self.imgs_num - 1:
                self.current_pair_idx = 0
                self.current_img_idx += 1
                self.score_combo.set(1)
                self.show_image()
            else:
                self.save_scores_to_file()
    
    def show_previous(self):
        self.save_score()
        
        if self.current_pair_idx > 0:
            self.current_pair_idx -= 1
            self.score_combo.set(self.scores.iloc[self.current_img_idx, self.current_pair_idx])
            self.show_image()
        else:
            if self.current_img_idx > 0:
                self.current_pair_idx = self.enhance_method_num-1
                self.current_img_idx -= 1
                self.score_combo.set(self.scores.iloc[self.current_img_idx, self.current_pair_idx])
                self.show_image()
            else:
                msg = 'Reached first image pair!!!!'
                messagebox.showinfo('Notice', msg)
    
    def save_score(self, event=None):
        score = int(self.score_combo.get())
        self.scores.iloc[self.current_img_idx, self.current_pair_idx] = score
    
    def save_scores_to_file(self):
        self.save_score()
        if self.get_current_progress() < self.imgs_num * self.enhance_method_num:
            result = messagebox.askyesno('Warnning', 
                                            "Looks like you haven't finished rating all images! Do you want to save scores data to file?")
            if not result:
                return
        try:
            file_path = filedialog.asksaveasfilename(defaultextension='.pkl', 
                                                     filetypes=[('Python pickle file', '*.pkl')],
                                                     initialfile='scores_data.pkl',
                                                     initialdir=os.path.dirname(__file__))
            pd.to_pickle(self.scores, file_path)
            messagebox.showinfo('Notice', 'Scores saved successfully.')
            return True
        except FileNotFoundError:
            messagebox.showwarning('Warnning', 'Please choose a proper file to save scores data!!!')
            return False
