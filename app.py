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

class DeclonerApp:
    def __init__(self, root):
        self.engine = ImageSimilarityEngine()
        self.root = root
        self.root.title("Image Similarity Finder")
        self.root.geometry("800x600")
        
        # Store thumbnails to prevent garbage collection
        self.thumbnail_refs = []
        
        # Store checkboxes and their variables
        self.checkboxes = {}
        self.current_folder = None

        # Create main layout
        self.create_widgets()

    def create_widgets(self):
        # Top frame for controls
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=5, pady=5)

        self.select_button = ttk.Button(control_frame, text="Select Folder", command=self.select_folder)
        self.select_button.pack(side="left", padx=5)

        # Delete button
        self.delete_button = ttk.Button(control_frame, text="Delete Selected", command=self.delete_selected)
        self.delete_button.pack(side="left", padx=5)
        self.delete_button.config(state="disabled")

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
        self.checkboxes.clear()
        self.delete_button.config(state="disabled")

    def refresh_display(self):
        # Clear current display
        for widget in self.scroll_frame.scrollable_frame.winfo_children():
            widget.destroy()
        self.thumbnail_refs.clear()
        self.checkboxes.clear()

        # Only display groups that still have 2 or more images
        valid_groups = [group for group in self.current_groups if len(group) >= 2]
        self.current_groups = valid_groups

        if self.current_groups:
            self.display_image_groups(self.current_folder, self.current_groups)
            self.delete_button.config(state="normal")
        else:
            self.status_label.config(text="No similar images found")
            self.delete_button.config(state="disabled")

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        self.current_folder = folder_path
        self.clear_results()
        self.status_label.config(text="Processing images...")
        self.root.update()

        # Load images and find similar ones
        self.engine.load_images(folder_path)
        groups = self.engine.group_similar_images()
        # Display groups
        self.display_image_groups(folder_path, groups)
        
        self.status_label.config(text=f"Found {len(groups)} groups of similar images")
        self.delete_button.config(state="normal")


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
                    
                    # Add checkbox for selection
                    var = tk.BooleanVar()
                    checkbox = ttk.Checkbutton(img_frame, variable=var)
                    checkbox.pack()
                    self.checkboxes[img_path] = var
                    
                    # Display thumbnail
                    label = ttk.Label(img_frame, image=thumb)
                    label.pack()
                    
                    # Display filename
                    name_label = ttk.Label(img_frame, text=img_name, wraplength=100)
                    name_label.pack()

    def delete_selected(self):
        selected_files = [path for path, var in self.checkboxes.items() if var.get()]
        
        if not selected_files:
            messagebox.showwarning("No Selection", "Please select at least one image to delete.")
            return

        if messagebox.askyesno("Confirm Deletion", 
                             f"Are you sure you want to delete {len(selected_files)} selected images?\n"
                             "This action cannot be undone."):
            deleted_count = 0
            for file_path in selected_files:
                try:
                    os.remove(file_path)
                    # Remove the file from its group
                    filename = os.path.basename(file_path)
                    for group in self.current_groups:
                        if filename in group:
                            group.remove(filename)
                    deleted_count += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete {os.path.basename(file_path)}: {str(e)}")

            # Refresh the display without reopening folder dialog
            if deleted_count > 0:
                messagebox.showinfo("Success", f"Successfully deleted {deleted_count} images.")
                self.refresh_display()
            
            self.status_label.config(text=f"Deleted {deleted_count} images")

if __name__ == "__main__":
    root = tk.Tk()
    app = DeclonerApp(root)
    root.mainloop()

