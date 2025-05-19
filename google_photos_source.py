from typing import List, Dict, Any, Optional
from PIL import Image
import io
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pickle
from image_source import ImageSource

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/photoslibrary'  # For delete operations
]

class GooglePhotosImageSource(ImageSource):
    """Implementation of ImageSource for Google Photos"""
    
    def __init__(self, credentials_path: str = 'credentials.json'):
        self.credentials_path = credentials_path
        self.service = None
        self.authenticate()
        
    def authenticate(self):
        """Authenticate with Google Photos API"""
        creds = None
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('photoslibrary', 'v1', credentials=creds)
        
    def list_images(self) -> List[str]:
        """Return list of image IDs from Google Photos"""
        try:
            # Get the first page of media items
            results = self.service.mediaItems().list(
                pageSize=100,
                fields="mediaItems(id,filename)"
            ).execute()
            
            items = results.get('mediaItems', [])
            image_ids = []
            
            # Filter for images only
            for item in items:
                if item.get('mimeType', '').startswith('image/'):
                    image_ids.append(item['id'])
                    
            return image_ids
            
        except Exception as e:
            print(f"Failed to list images: {e}")
            return []
    
    def get_image(self, image_id: str) -> Optional[Image.Image]:
        """Get image from Google Photos by ID"""
        try:
            # Get the media item
            media_item = self.service.mediaItems().get(
                mediaItemId=image_id
            ).execute()
            
            # Get the base URL
            base_url = media_item['baseUrl']
            
            # Download the image
            response = self.service._http.request('GET', base_url)
            if response[0].status == 200:
                image_data = response[1]
                return Image.open(io.BytesIO(image_data))
            return None
            
        except Exception as e:
            print(f"Failed to get image {image_id}: {e}")
            return None
    
    def get_thumbnail(self, image_id: str, size: tuple = (100, 100)) -> Optional[Image.Image]:
        """Get thumbnail from Google Photos"""
        try:
            # Get the media item
            media_item = self.service.mediaItems().get(
                mediaItemId=image_id
            ).execute()
            
            # Get the thumbnail URL
            base_url = media_item['baseUrl']
            # Add size parameter to URL
            thumbnail_url = f"{base_url}=w{size[0]}-h{size[1]}-c"
            
            # Download the thumbnail
            response = self.service._http.request('GET', thumbnail_url)
            if response[0].status == 200:
                image_data = response[1]
                return Image.open(io.BytesIO(image_data))
            return None
            
        except Exception as e:
            print(f"Failed to get thumbnail for {image_id}: {e}")
            return None
    
    def delete_image(self, image_id: str) -> bool:
        """Delete image from Google Photos"""
        try:
            # Note: This requires additional scope: 'https://www.googleapis.com/auth/photoslibrary'
            self.service.mediaItems().delete(
                mediaItemId=image_id
            ).execute()
            return True
        except Exception as e:
            print(f"Failed to delete {image_id}: {e}")
            return False
    
    def get_image_metadata(self, image_id: str) -> Dict[str, Any]:
        """Get metadata about the image from Google Photos"""
        try:
            media_item = self.service.mediaItems().get(
                mediaItemId=image_id
            ).execute()
            
            return {
                'filename': media_item.get('filename', ''),
                'size': media_item.get('size', 0),
                'created': media_item.get('mediaMetadata', {}).get('creationTime', ''),
                'mimeType': media_item.get('mimeType', ''),
                'description': media_item.get('description', '')
            }
        except Exception as e:
            print(f"Failed to get metadata for {image_id}: {e}")
            return {'filename': image_id} 