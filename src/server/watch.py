from asyncio import Future
from os.path import abspath, dirname
from typing import AsyncIterable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


async def watch(path: str) -> AsyncIterable[str]:
    future = Future()

    full_path = abspath(path)
    directory = dirname(full_path)

    class Handler(FileSystemEventHandler):
        def on_any_event(self, event: FileSystemEvent) -> None:
            super().on_any_event(event)
            if event.src_path == full_path:
                future.set_result(event.src_path)

    obs = Observer()
    obs.schedule(Handler(), directory)
    obs.start()

    try:
        obs.join()
    except KeyboardInterrupt:
        obs.stop()

    while True:
        ret = await future
        print("AAAAAAAAAAAAAAAAAA")
        yield ret
        future = Future()
