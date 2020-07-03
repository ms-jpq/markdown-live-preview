from asyncio import Queue
from os.path import abspath, dirname
from typing import AsyncIterable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


def watch(path: str) -> AsyncIterable[FileSystemEvent]:
    queue: Queue[FileSystemEvent] = Queue()

    full_path = abspath(path)
    directory = dirname(full_path)

    class Handler(FileSystemEventHandler):
        def on_any_event(self, event: FileSystemEvent) -> None:
            super().on_any_event(event)
            queue.put_nowait(event.src_path)

    obs = Observer()
    obs.schedule(Handler(), directory)
    obs.start()

    async def gen() -> AsyncIterable[FileSystemEvent]:
        while True:
            event = await queue.get()
            yield event

    return gen()
