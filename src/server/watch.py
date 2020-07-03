from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


def watch(path: str) -> Callable[[], None]:
    class Handler(FileSystemEventHandler):
        def on_any_event(self, event: FileSystemEvent) -> None:
            print(event)

    obs = Observer()
    obs.schedule(Handler(), path)

    def join() -> None:
        obs.start()
        try:
            obs.join()
        except KeyboardInterrupt:
            exit()

    return join
