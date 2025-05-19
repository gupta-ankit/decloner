# Image Similarity Finder

A tool to find and manage similar images from local folders or Google Photos.

## Features

- Find similar images using image comparison
- Support for both local files and Google Photos
- Group similar images together
- Delete selected images
- Modern and intuitive user interface

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. For Google Photos integration:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Photos Library API
   - Create OAuth 2.0 credentials
   - Download the credentials and save them as `credentials.json` in the project directory

## Usage

1. Run the application:
```bash
python app.py
```

2. Choose your image source:
   - Local Files: Select a folder containing images
   - Google Photos: Connect to your Google Photos account

3. The application will:
   - Load images from the selected source
   - Find similar images
   - Display them in groups
   - Allow you to select and delete similar images

## Notes

- For Google Photos, the first time you connect, you'll need to authenticate through your browser
- The application will save the authentication token for future use
- Image deletion is permanent and cannot be undone
- The application uses image comparison to find similar images, which may take some time for large collections 