from asyncio import get_running_loop
from asyncio.locks import Event
from asyncio.tasks import run_coroutine_threadsafe
from pathlib import Path
from typing import AsyncIterable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


async def watch(path: Path) -> AsyncIterable[None]:
    loop = get_running_loop()
    ev = Event()

    async def notify() -> None:
        ev.set()

    def send(event: FileSystemEvent) -> None:
        if Path(event.src_path) == path:
            run_coroutine_threadsafe(notify(), loop=loop)

    class Handler(FileSystemEventHandler):
        def on_created(self, event: FileSystemEvent) -> None:
            send(event)

        def on_modified(self, event: FileSystemEvent) -> None:
            send(event)

    obs = Observer()
    obs.schedule(Handler(), path=path.parent)
    obs.start()

    ev.set()
    while True:
        await ev.wait()
        ev.clear()

        try:
            yield None
        except GeneratorExit:
            obs.stop()
            break
