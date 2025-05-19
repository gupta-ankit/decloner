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

    def group_similar_images(self):
        similar_pairs = self.find_similar_images()
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
                    
