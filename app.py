# A minimal UI using tkinter that uses the backend

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from image_similarity_backend import ImageSimilarityEngine
from image_source import ImageSource, LocalFileImageSource
from google_photos_source import GooglePhotosImageSource
from collections import defaultdict
from typing import Optional

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
        self.image_source = None

        # Create main layout
        self.create_widgets()

    def create_widgets(self):
        # Top frame for controls
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=5, pady=5)

        # Source selection
        source_frame = ttk.LabelFrame(control_frame, text="Image Source")
        source_frame.pack(side="left", padx=5)

        self.source_var = tk.StringVar(value="local")
        ttk.Radiobutton(source_frame, text="Local Files", variable=self.source_var, 
                       value="local", command=self.on_source_change).pack(side="left", padx=5)
        ttk.Radiobutton(source_frame, text="Google Photos", variable=self.source_var,
                       value="google", command=self.on_source_change).pack(side="left", padx=5)

        # Select button
        self.select_button = ttk.Button(control_frame, text="Select Source", command=self.select_source)
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

    def on_source_change(self):
        """Handle source type change"""
        self.clear_results()
        self.image_source = None
        self.select_button.config(text="Select Source")

    def select_source(self):
        """Select the image source based on the selected type"""
        source_type = self.source_var.get()
        
        if source_type == "local":
            folder_path = filedialog.askdirectory()
            if not folder_path:
                return
            self.image_source = LocalFileImageSource(folder_path)
        else:  # google
            try:
                self.image_source = GooglePhotosImageSource()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to connect to Google Photos: {str(e)}")
                return

        self.process_images()

    def process_images(self):
        """Process images from the selected source"""
        if not self.image_source:
            return

        self.clear_results()
        self.status_label.config(text="Processing images...")
        self.root.update()

        # Load images and find similar groups
        image_ids = self.image_source.list_images()
        self.engine.load_images_from_source(self.image_source, image_ids)
        groups = self.engine.group_similar_images()
        
        # Display groups
        self.display_image_groups(groups)
        
        self.status_label.config(text=f"Found {len(groups)} groups of similar images")
        self.delete_button.config(state="normal")

    def create_thumbnail(self, image_id: str, size=(100, 100)) -> Optional[ImageTk.PhotoImage]:
        try:
            thumbnail = self.image_source.get_thumbnail(image_id, size)
            if thumbnail:
                photo = ImageTk.PhotoImage(thumbnail)
                self.thumbnail_refs.append(photo)
                return photo
            return None
        except Exception as e:
            print(f"Failed to create thumbnail for {image_id}: {e}")
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
            self.display_image_groups(self.current_groups)
            self.delete_button.config(state="normal")
        else:
            self.status_label.config(text="No similar images found")
            self.delete_button.config(state="disabled")

    def display_image_groups(self, groups):
        for i, group in enumerate(groups):
            # Create a frame for each group
            group_frame = ttk.LabelFrame(self.scroll_frame.scrollable_frame, text=f"Similar Group {i+1}")
            group_frame.pack(fill="x", padx=5, pady=5)

            # Create a frame for thumbnails
            thumbs_frame = ttk.Frame(group_frame)
            thumbs_frame.pack(padx=5, pady=5)

            # Display thumbnails for each image in the group
            for image_id in group:
                thumb = self.create_thumbnail(image_id)
                
                if thumb:
                    # Create frame for each image
                    img_frame = ttk.Frame(thumbs_frame)
                    img_frame.pack(side="left", padx=5)
                    
                    # Add checkbox for selection
                    var = tk.BooleanVar()
                    checkbox = ttk.Checkbutton(img_frame, variable=var)
                    checkbox.pack()
                    self.checkboxes[image_id] = var
                    
                    # Display thumbnail
                    label = ttk.Label(img_frame, image=thumb)
                    label.pack()
                    
                    # Display filename
                    metadata = self.image_source.get_image_metadata(image_id)
                    name_label = ttk.Label(img_frame, text=metadata['filename'], wraplength=100)
                    name_label.pack()

    def delete_selected(self):
        selected_images = [image_id for image_id, var in self.checkboxes.items() if var.get()]
        
        if not selected_images:
            messagebox.showwarning("No Selection", "Please select at least one image to delete.")
            return

        if messagebox.askyesno("Confirm Deletion", 
                             f"Are you sure you want to delete {len(selected_images)} selected images?\n"
                             "This action cannot be undone."):
            deleted_count = 0
            for image_id in selected_images:
                if self.image_source.delete_image(image_id):
                    # Remove the image from its group
                    for group in self.current_groups:
                        if image_id in group:
                            group.remove(image_id)
                    deleted_count += 1

            # Refresh the display without reopening folder dialog
            if deleted_count > 0:
                messagebox.showinfo("Success", f"Successfully deleted {deleted_count} images.")
                self.refresh_display()
            
            self.status_label.config(text=f"Deleted {deleted_count} images")

if __name__ == "__main__":
    root = tk.Tk()
    app = DeclonerApp(root)
    root.mainloop()

