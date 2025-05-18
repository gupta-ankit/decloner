# image_similarity_backend.py
# This is the backend module you can import anywhere

import os
from PIL import Image
import imagehash

class ImageSimilarityEngine:
    def __init__(self, hash_func=imagehash.phash):
        self.hash_func = hash_func
        self.image_data = []  # List of tuples: (filename, imagehash)

    def load_images(self, folder_path):
        self.image_data.clear()
        for filename in os.listdir(folder_path):
            path = os.path.join(folder_path, filename)
            if not os.path.isfile(path):
                continue
            try:
                with Image.open(path) as img:
                    img_hash = self.hash_func(img)
                    self.image_data.append((filename, img_hash))
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

    def find_similar_images(self, threshold=5):
        similar_pairs = []
        for i in range(len(self.image_data)):
            for j in range(i + 1, len(self.image_data)):
                hash1 = self.image_data[i][1]
                hash2 = self.image_data[j][1]
                distance = hash1 - hash2
                if distance <= threshold:
                    similar_pairs.append((self.image_data[i][0], self.image_data[j][0], distance))
        return similar_pairs


# image_similarity_ui.py
# A minimal UI using tkinter that uses the backend

import tkinter as tk
from tkinter import filedialog, messagebox
from image_similarity_backend import ImageSimilarityEngine

class ImageSimilarityApp:
    def __init__(self, root):
        self.engine = ImageSimilarityEngine()
        self.root = root
        self.root.title("Image Similarity Finder")

        self.select_button = tk.Button(root, text="Select Folder", command=self.select_folder)
        self.select_button.pack(pady=10)

        self.result_text = tk.Text(root, height=20, width=60)
        self.result_text.pack(padx=10, pady=10)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Loading images from: {folder_path}\n")
            self.engine.load_images(folder_path)
            self.result_text.insert(tk.END, f"Finding similar images...\n")
            pairs = self.engine.find_similar_images()
            if not pairs:
                self.result_text.insert(tk.END, "No similar images found.\n")
            else:
                for img1, img2, dist in pairs:
                    self.result_text.insert(tk.END, f"{img1} <--> {img2} (distance: {dist})\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSimilarityApp(root)
    root.mainloop()

