# A minimal UI using tkinter that uses the backend

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from image_similarity_backend import ImageSimilarityEngine
import os
from collections import defaultdict

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class ImageSimilarityApp:
    def __init__(self, root):
        self.engine = ImageSimilarityEngine()
        self.root = root
        self.root.title("Image Similarity Finder")
        self.root.geometry("800x600")
        
        # Store thumbnails to prevent garbage collection
        self.thumbnail_refs = []
        
        # Create main layout
        self.create_widgets()

    def create_widgets(self):
        # Top frame for controls
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=5, pady=5)

        self.select_button = ttk.Button(control_frame, text="Select Folder", command=self.select_folder)
        self.select_button.pack(side="left", padx=5)

        # Status label
        self.status_label = ttk.Label(control_frame, text="")
        self.status_label.pack(side="left", padx=5)

        # Create scrollable frame for images
        self.scroll_frame = ScrollableFrame(self.root)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def create_thumbnail(self, image_path, size=(100, 100)):
        try:
            with Image.open(image_path) as img:
                img.thumbnail(size)
                photo = ImageTk.PhotoImage(img)
                self.thumbnail_refs.append(photo)
                return photo
        except Exception as e:
            print(f"Failed to create thumbnail for {image_path}: {e}")
            return None

    def clear_results(self):
        # Clear previous results
        for widget in self.scroll_frame.scrollable_frame.winfo_children():
            widget.destroy()
        self.thumbnail_refs.clear()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        self.clear_results()
        self.status_label.config(text="Processing images...")
        self.root.update()

        # Load images and find similar ones
        self.engine.load_images(folder_path)
        similar_pairs = self.engine.find_similar_images()

        # Group similar images
        groups = self.group_similar_images(similar_pairs)
        
        # Display groups
        self.display_image_groups(folder_path, groups)
        
        self.status_label.config(text=f"Found {len(groups)} groups of similar images")

    def group_similar_images(self, similar_pairs):
        # Create groups of similar images
        groups = []
        used_images = set()

        for img1, img2, distance in similar_pairs:
            # Find if any of the images are in existing groups
            found_group = False
            for group in groups:
                if img1 in group or img2 in group:
                    group.add(img1)
                    group.add(img2)
                    found_group = True
                    break
            
            if not found_group:
                # Create new group
                groups.append({img1, img2})
            
            used_images.add(img1)
            used_images.add(img2)

        return groups

    def display_image_groups(self, folder_path, groups):
        for i, group in enumerate(groups):
            # Create a frame for each group
            group_frame = ttk.LabelFrame(self.scroll_frame.scrollable_frame, text=f"Similar Group {i+1}")
            group_frame.pack(fill="x", padx=5, pady=5)

            # Create a frame for thumbnails
            thumbs_frame = ttk.Frame(group_frame)
            thumbs_frame.pack(padx=5, pady=5)

            # Display thumbnails for each image in the group
            for img_name in group:
                img_path = os.path.join(folder_path, img_name)
                thumb = self.create_thumbnail(img_path)
                
                if thumb:
                    # Create frame for each image
                    img_frame = ttk.Frame(thumbs_frame)
                    img_frame.pack(side="left", padx=5)
                    
                    # Display thumbnail
                    label = ttk.Label(img_frame, image=thumb)
                    label.pack()
                    
                    # Display filename
                    name_label = ttk.Label(img_frame, text=img_name, wraplength=100)
                    name_label.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSimilarityApp(root)
    root.mainloop()

