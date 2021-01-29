from asyncio import Queue, get_running_loop, run_coroutine_threadsafe
from pathlib import Path
from typing import AsyncIterable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


async def watch(path: Path) -> AsyncIterable[str]:
    loop = get_running_loop()
    chan: Queue[None] = Queue(1)

    def send(event: FileSystemEvent) -> None:
        if event.src_path == path.parent:
            fut = run_coroutine_threadsafe(chan.put(None), loop=loop)
            fut.result()

    class Handler(FileSystemEventHandler):
        def on_created(self, event: FileSystemEvent) -> None:
            send(event)

        def on_modified(self, event: FileSystemEvent) -> None:
            send(event)

    obs = Observer()
    obs.schedule(Handler(), path=path.parent)
    obs.start()

    while True:
        try:
            yield path.read_text("UTF-8")
        except GeneratorExit:
            obs.stop()
            break
        await chan.get()
