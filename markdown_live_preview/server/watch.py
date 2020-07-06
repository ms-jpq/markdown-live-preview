from asyncio import Queue, run_coroutine_threadsafe, get_running_loop
from os.path import abspath, dirname
from typing import AsyncIterable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


async def watch(path: str) -> AsyncIterable[str]:
    loop = get_running_loop()
    chan: Queue[None] = Queue(1)

    full_path = abspath(path)
    directory = dirname(full_path)

    def slurp() -> str:
        with open(full_path) as fd:
            return fd.read()

    def send(event: FileSystemEvent) -> None:
        if event.src_path == full_path:
            fut = run_coroutine_threadsafe(chan.put(None), loop=loop)
            fut.result()

    class Handler(FileSystemEventHandler):
        def on_created(self, event: FileSystemEvent) -> None:
            send(event)

        def on_modified(self, event: FileSystemEvent) -> None:
            send(event)

    obs = Observer()
    obs.schedule(Handler(), directory)
    obs.start()

    while True:
        try:
            yield slurp()
        except GeneratorExit:
            obs.stop()
            break
        await chan.get()
