import os
import requests
import threading
import queue
from uuid import uuid4
import youtube_dl
from models import ConversationInfo

PHOTO_DOWNLOADERS = 10
VIDEO_DOWNLOADERS = 10
PARSER_WORKERS = 5

class MediaPipeline:
    def __init__(self, vk_controller):
        self.vk_controller = vk_controller
        self.conversation_queue = queue.Queue()
        self.photo_queue = queue.Queue()
        self.video_queue = queue.Queue()
        self.progress = {
            'conversations_total': 0,
            'conversations_done': 0,
            'photos_total': 0,
            'photos_done': 0,
            'videos_total': 0,
            'videos_done': 0,
        }
        self.lock = threading.Lock()

    def start(self):
        threading.Thread(target=self.fetch_conversations).start()

        for _ in range(PARSER_WORKERS):
            threading.Thread(target=self.process_conversation).start()

        for _ in range(PHOTO_DOWNLOADERS):
            threading.Thread(target=self.download_photo).start()

        for _ in range(VIDEO_DOWNLOADERS):
            threading.Thread(target=self.download_video).start()

    def fetch_conversations(self):
        conversations = self.vk_controller.get_conversations()
        with self.lock:
            self.progress['conversations_total'] = len(conversations)

        for conv in conversations:
            self.conversation_queue.put(conv)

    def process_conversation(self):
        while True:
            conv = self.conversation_queue.get()
            try:
                user_name = self.vk_controller.get_user_name(conv)
                photos, videos = self.vk_controller.get_conversation_photos_and_videos(conv)

                with self.lock:
                    self.progress['photos_total'] += len(photos)
                    self.progress['videos_total'] += len(videos)

                for url in photos:
                    self.photo_queue.put((user_name, url))
                for url in videos:
                    self.video_queue.put((user_name, url))

            finally:
                with self.lock:
                    self.progress['conversations_done'] += 1
                self.conversation_queue.task_done()

    def download_photo(self):
        while True:
            user_name, url = self.photo_queue.get()
            folder = f'media-files/{user_name}'
            os.makedirs(folder, exist_ok=True)
            try:
                data = requests.get(url).content
                with open(f'{folder}/{uuid4()}.jpg', 'wb') as f:
                    f.write(data)
            except Exception:
                pass
            with self.lock:
                self.progress['photos_done'] += 1
            self.photo_queue.task_done()

    def download_video(self):
        while True:
            user_name, url = self.video_queue.get()
            folder = f'media-files/{user_name}'
            os.makedirs(folder, exist_ok=True)
            try:
                ydl_opts = {
                    'outtmpl': f'{folder}/{uuid4()}.mp4',
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'quiet': True
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception:
                pass
            with self.lock:
                self.progress['videos_done'] += 1
            self.video_queue.task_done()

    def get_progress(self):
        with self.lock:
            return self.progress
