from asyncio import Queue, get_running_loop
from os.path import abspath, dirname
from typing import AsyncIterable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


async def watch(path: str) -> AsyncIterable[FileSystemEvent]:
    loop = get_running_loop()
    queue: Queue[FileSystemEvent] = Queue()

    full_path = abspath(path)
    directory = dirname(full_path)

    class Handler(FileSystemEventHandler):
        def on_any_event(self, event: FileSystemEvent) -> None:
            super().on_any_event(event)
            if event.src_path == full_path:
                loop.call_soon_threadsafe(queue.put_nowait, event)

    obs = Observer()
    obs.schedule(Handler(), directory)
    obs.start()

    while True:
        event = await queue.get()
        try:
            yield event
        except GeneratorExit:
            obs.stop()
            break
