import sys
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class Watcher:
    DIRECTORY_TO_WATCH = "."

    def __init__(self):
        self.observer = Observer()
        self.bot_process = None

    def run(self):
        event_handler = Handler(self)
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        self.start_bot()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            self.stop_bot()
        self.observer.join()
    
    def start_bot(self):
        bot_path = os.path.join(os.path.dirname(__file__), 'bot.py')
        self.bot_process = subprocess.Popen([sys.executable, bot_path])

    def stop_bot(self):
        if self.bot_process:
            self.bot_process.terminate()
            self.bot_process.wait()
            self.bot_process = None

class Handler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher

    def on_any_event(self,event):
        if event.is_directory:
            return None
        
        if any(excluded in event.src_path for excluded in ['venv', '__pycache__', '.git', '.tmp', '.lock']):
            return None
        
        if event.event_type == 'modified':
            print(f'Файл змінено: {event.src_path}. Перезапуск бота...')
            self.watcher.stop_bot()
            self.watcher.start_bot()

if __name__ == '__main__':
    w = Watcher()
    w.run()