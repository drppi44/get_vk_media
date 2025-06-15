import threading
from vk_controller import VKController
from pipeline import MediaPipeline
from progress import show_progress


VK_LOGIN = '***'
VK_PASSWORD = '***'


vk_controller = VKController(VK_LOGIN, VK_PASSWORD)
pipeline = MediaPipeline(vk_controller)

# Запуск прогресу в окремому потоці
progress_thread = threading.Thread(target=show_progress, args=(pipeline.get_progress,), daemon=True)
progress_thread.start()

if __name__ == "__main__":
    pipeline.start()
