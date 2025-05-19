# image_similarity_backend.py
# This is the backend module you can import anywhere

import os
from PIL import Image
import imagehash
import numpy as np
from typing import List, Dict, Any
from image_source import ImageSource

class ImageSimilarityEngine:
    def __init__(self):
        self.images = {}  # Dictionary to store image data
        self.image_source = None

    def load_images_from_source(self, image_source: ImageSource, image_ids: List[str]):
        """Load images from the given image source"""
        self.image_source = image_source
        self.images.clear()
        
        for image_id in image_ids:
            try:
                img = image_source.get_image(image_id)
                if img:
                    # Convert image to RGB if it's not
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    # Resize to a standard size for comparison
                    img = img.resize((100, 100))
                    # Convert to numpy array
                    self.images[image_id] = np.array(img)
            except Exception as e:
                print(f"Failed to load image {image_id}: {e}")

    def compute_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Compute similarity between two images using mean squared error"""
        return np.mean((img1 - img2) ** 2)

    def group_similar_images(self, threshold: float = 1000.0) -> List[List[str]]:
        """Group similar images together"""
        if not self.images:
            return []

        groups = []
        processed = set()

        for img1_id, img1_data in self.images.items():
            if img1_id in processed:
                continue

            current_group = [img1_id]
            processed.add(img1_id)

            for img2_id, img2_data in self.images.items():
                if img2_id in processed:
                    continue

                similarity = self.compute_similarity(img1_data, img2_data)
                if similarity < threshold:
                    current_group.append(img2_id)
                    processed.add(img2_id)

            if len(current_group) > 1:  # Only add groups with more than one image
                groups.append(current_group)

        return groups

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
                    
