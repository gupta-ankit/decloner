from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
from PIL import Image
import io

class ImageSource(ABC):
    """Abstract base class for image sources (local files, Google Photos, etc.)"""
    
    @abstractmethod
    def list_images(self) -> List[str]:
        """Return a list of image identifiers that can be used to access the images"""
        pass
    
    @abstractmethod
    def get_image(self, image_id: str) -> Optional[Image.Image]:
        """Get an image by its identifier"""
        pass
    
    @abstractmethod
    def get_thumbnail(self, image_id: str, size: tuple = (100, 100)) -> Optional[Image.Image]:
        """Get a thumbnail of an image by its identifier"""
        pass
    
    @abstractmethod
    def delete_image(self, image_id: str) -> bool:
        """Delete an image by its identifier. Returns True if successful."""
        pass
    
    @abstractmethod
    def get_image_metadata(self, image_id: str) -> Dict[str, Any]:
        """Get metadata about the image (filename, size, etc.)"""
        pass

class LocalFileImageSource(ImageSource):
    """Implementation of ImageSource for local files"""
    
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
    
    def list_images(self) -> List[str]:
        """Return list of image filenames in the folder"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        return [
            f for f in os.listdir(self.folder_path)
            if os.path.splitext(f.lower())[1] in image_extensions
        ]
    
    def get_image(self, image_id: str) -> Optional[Image.Image]:
        """Get image from local file"""
        try:
            file_path = os.path.join(self.folder_path, image_id)
            return Image.open(file_path)
        except Exception as e:
            print(f"Failed to load image {image_id}: {e}")
            return None
    
    def get_thumbnail(self, image_id: str, size: tuple = (100, 100)) -> Optional[Image.Image]:
        """Get thumbnail from local file"""
        try:
            img = self.get_image(image_id)
            if img:
                img.thumbnail(size)
                return img
            return None
        except Exception as e:
            print(f"Failed to create thumbnail for {image_id}: {e}")
            return None
    
    def delete_image(self, image_id: str) -> bool:
        """Delete local file"""
        try:
            file_path = os.path.join(self.folder_path, image_id)
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Failed to delete {image_id}: {e}")
            return False
    
    def get_image_metadata(self, image_id: str) -> Dict[str, Any]:
        """Get metadata about the local file"""
        file_path = os.path.join(self.folder_path, image_id)
        try:
            stat = os.stat(file_path)
            return {
                'filename': image_id,
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime
            }
        except Exception as e:
            print(f"Failed to get metadata for {image_id}: {e}")
            return {'filename': image_id} 