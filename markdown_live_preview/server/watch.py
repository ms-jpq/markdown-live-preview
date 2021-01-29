from asyncio import Queue, get_running_loop
from asyncio.events import TimerHandle
from pathlib import Path
from typing import AsyncIterable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


async def watch(path: Path) -> AsyncIterable[str]:
    loop = get_running_loop()
    chan: Queue[None] = Queue(1)

    notify = lambda: chan.put_nowait(None)
    handle: Optional[TimerHandle] = None

    def send(event: FileSystemEvent) -> None:
        nonlocal handle
        if Path(event.src_path) == path:
            if handle:
                handle.cancel()

            handle = loop.call_later(0.05, notify)

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
