# Video Bot

## Description
A Python-based bot that monitors a directory for new video files, uploads them to a server, and creates a post for each uploaded video.

## Requirements
- Python 3.7+
- `aiohttp` for async HTTP requests
- `aiofiles` for async file operations
- `watchdog` for monitoring file system events
- `tqdm` for progress bars
- `logging` for logging messages

## Setup
1. Clone the repository:
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Set your Flic-Token in `main.py`:
    ```python
    FLIC_TOKEN = "your_flic_token_here"
    ```

## Usage
1. Create a directory named `videos` in the root of the project if it doesn't exist:
    ```sh
    mkdir videos
    ```

2. Run the bot:
    ```sh
    python main.py
    ```

3. Place your `.mp4` videos in the `videos` directory and the script will do the rest.

## How It Works
1. **Directory Monitoring**: The script monitors the `videos` directory for new `.mp4` files using the `watchdog` library.
2. **Upload Process**: When a new video file is detected, the script performs the following steps:
    - **Get Upload URL**: Asynchronously requests an upload URL from the server.
    - **Upload Video**: Asynchronously uploads the video file to the server with a progress bar.
    - **Create Post**: Asynchronously creates a post on the server using the uploaded video's hash.
    - **Delete Local File**: Deletes the local video file after successful upload and post creation.

## Detailed Explanation
### Modules and Libraries
- **os**: Provides a way of using operating system dependent functionality.
- **aiohttp**: Asynchronous HTTP client/server framework.
- **asyncio**: Provides support for asynchronous programming.
- **aiofiles**: Provides support for asynchronous file operations.
- **watchdog.observers**: Provides a way to monitor file system events.
- **watchdog.events**: Provides base classes for file system event handling.
- **tqdm.asyncio**: Provides a progress bar for asyncio tasks.
- **logging**: Provides a way to log messages.

### Constants
- **FLIC_TOKEN**: The token used for authentication with the server.
- **HEADERS**: The headers used for HTTP requests.

### Functions
- **get_upload_url(session)**: Asynchronously gets an upload URL from the server.
- **upload_video(file_path, upload_url, progress_bar)**: Asynchronously uploads a video file to the server.
- **create_post(session, video_title, video_hash, category_id)**: Asynchronously creates a post on the server.
- **upload_process(video_path)**: Manages the entire upload process for a video file.
- **monitor_videos()**: Monitors a directory for new video files and triggers the upload process.

### Classes
- **VideoHandler(FileSystemEventHandler)**: Handles file system events for video files.

### Main Entry Point
- The script starts by calling `asyncio.run(monitor_videos())`, which begins monitoring the `videos` directory for new video files.

## Logging
- The script uses the `logging` module to log messages at various points in the execution. This helps in debugging and understanding the flow of the script.

## Notes
- Ensure that your Flic-Token is valid and has the necessary permissions to upload videos and create posts.
- The script is designed to handle `.mp4` files. If you need to handle other file types, modify the `on_created` method in the `VideoHandler` class accordingly.