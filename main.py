"""
Video Bot Script

This script monitors a directory for new video files, uploads them to a server, and creates a post for each uploaded video.

Modules:
    os: Provides a way of using operating system dependent functionality.
    aiohttp: Asynchronous HTTP client/server framework.
    asyncio: Provides support for asynchronous programming.
    aiofiles: Provides support for asynchronous file operations.
    watchdog.observers: Provides a way to monitor file system events.
    watchdog.events: Provides base classes for file system event handling.
    tqdm.asyncio: Provides a progress bar for asyncio tasks.
    logging: Provides a way to log messages.

Constants:
    FLIC_TOKEN (str): The token used for authentication with the server.
    HEADERS (dict): The headers used for HTTP requests.

Functions:
    get_upload_url(session): Asynchronously gets an upload URL from the server.
    upload_video(file_path, upload_url, progress_bar): Asynchronously uploads a video file to the server.
    create_post(session, video_title, video_hash, category_id): Asynchronously creates a post on the server.
    upload_process(video_path): Manages the entire upload process for a video file.
    monitor_videos(): Monitors a directory for new video files and triggers the upload process.

Classes:
    VideoHandler(FileSystemEventHandler): Handles file system events for video files.
"""

import os
import aiohttp
import asyncio
from aiofiles import open as aio_open
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tqdm.asyncio import tqdm_asyncio
import logging

FLIC_TOKEN = "flic_cc31c3b62fb1d38d9d1e5472c1076c5331e26b05b1c6b8f38829e76d9d6a2aae"
HEADERS = {
    "Flic-Token": FLIC_TOKEN,
    "Content-Type": "application/json"
}

# Set up logging
logging.basicConfig(level=logging.INFO)

async def get_upload_url(session):
    """
    Asynchronously gets an upload URL from the server.

    Args:
        session (aiohttp.ClientSession): The HTTP session to use for the request.

    Returns:
        dict: A dictionary containing the upload URL and hash, or None if the request failed.
    """
    endpoint = "https://api.socialverseapp.com/posts/generate-upload-url"
    try:
        async with session.get(endpoint, headers=HEADERS) as response:
            if response.status == 200:
                return await response.json()  # Returns a dictionary with 'url' and 'hash'
            else:
                logging.error(f"Failed to get upload URL: {await response.text()}")
    except Exception as e:
        logging.error(f"Error in get_upload_url: {e}")
    return None

async def upload_video(file_path, upload_url, progress_bar):
    """
    Asynchronously uploads a video file to the server.

    Args:
        file_path (str): The path to the video file.
        upload_url (str): The URL to upload the video to.
        progress_bar (tqdm_asyncio): The progress bar to update during the upload.
    """
    try:
        async with aio_open(file_path, 'rb') as video_file:
            data = await video_file.read()
            progress_bar.update(len(data))
            async with aiohttp.ClientSession() as session:
                async with session.put(upload_url, data=data) as response:
                    if response.status == 200:
                        logging.info("Video uploaded successfully.")
                        progress_bar.close()
                    else:
                        logging.error(f"Failed to upload video: {await response.text()}")
    except Exception as e:
        logging.error(f"Error in upload_video: {e}")

async def create_post(session, video_title, video_hash, category_id):
    """
    Asynchronously creates a post on the server.

    Args:
        session (aiohttp.ClientSession): The HTTP session to use for the request.
        video_title (str): The title of the video.
        video_hash (str): The hash of the uploaded video.
        category_id (int): The category ID for the post.
    """
    endpoint = "https://api.socialverseapp.com/posts"
    data = {
        "title": video_title,
        "hash": video_hash,
        "is_available_in_public_feed": True, 
        "category_id": category_id  
    }
    try:
        async with session.post(endpoint, headers=HEADERS, json=data) as response:
            if response.status == 200:
                logging.info(f"Post created successfully: {await response.json()}")
            else:
                logging.error(f"Failed to create post: {await response.text()}")
    except Exception as e:
        logging.error(f"Error in create_post: {e}")

async def upload_process(video_path):
    """
    Manages the entire upload process for a video file.

    Args:
        video_path (str): The path to the video file.
    """
    async with aiohttp.ClientSession() as session:
        # Step 1: Get Upload URL
        upload_info = await get_upload_url(session)
        if not upload_info:
            return
        upload_url = upload_info['url']
        video_hash = upload_info['hash']

        # Step 2: Upload Video with Progress Bar
        file_size = os.path.getsize(video_path)
        with tqdm_asyncio(total=file_size, unit="B", unit_scale=True, desc=f"Uploading {os.path.basename(video_path)}") as progress_bar:
            await upload_video(video_path, upload_url, progress_bar)

        # Step 3: Create Post
        video_title = os.path.basename(video_path)
        await create_post(session, video_title, video_hash, category_id=25)

        # Step 4: Delete Local File
        os.remove(video_path)
        logging.info(f"Deleted local file: {video_path}")

class VideoHandler(FileSystemEventHandler):
    """
    Handles file system events for video files.

    Args:
        loop (asyncio.AbstractEventLoop): The event loop to use for asynchronous tasks.
    """
    def __init__(self, loop):
        super().__init__()
        self.loop = loop

    def on_created(self, event):
        """
        Called when a file or directory is created.

        Args:
            event (watchdog.events.FileSystemEvent): The event representing the file system change.
        """
        if event.src_path.endswith('.mp4'):
            logging.info(f"New video detected: {event.src_path}")
            self.loop.create_task(upload_process(event.src_path))

async def monitor_videos():
    """
    Monitors a directory for new video files and triggers the upload process.
    """
    path = "./videos"
    if not os.path.exists(path):
        os.makedirs(path)
    loop = asyncio.get_event_loop()
    event_handler = VideoHandler(loop)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    logging.info("Monitoring /videos directory for new videos...")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    """
    Main entry point for the script.
    """
    asyncio.run(monitor_videos())

