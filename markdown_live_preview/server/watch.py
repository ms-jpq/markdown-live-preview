from asyncio import Queue, get_running_loop
from asyncio.locks import Event
from asyncio.tasks import (
    FIRST_COMPLETED,
    create_task,
    gather,
    run_coroutine_threadsafe,
    sleep,
    wait,
)
from collections.abc import AsyncIterable, ByteString
from os.path import normcase
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


async def watch(throttle: float, path: Path) -> AsyncIterable[str]:
    loop = get_running_loop()
    chan: Queue[None] = Queue(1)
    ev = Event()
    ev.set()

    async def notify() -> None:
        done, _ = await wait(
            (create_task(ev.wait()), create_task(sleep(throttle, False))),
            return_when=FIRST_COMPLETED,
        )
        go = done.pop().result()
        if go and ev.is_set():
            ev.clear()
            await gather(chan.put(None), create_task(sleep(throttle)))
            ev.set()

    def send(event: FileSystemEvent) -> None:
        src = (
            bytes(event.src_path).decode()
            if isinstance(event.src_path, ByteString)
            else event.src_path
        )
        if Path(src) == path:
            run_coroutine_threadsafe(notify(), loop=loop)

    class Handler(FileSystemEventHandler):
        def on_created(self, event: FileSystemEvent) -> None:
            send(event)

        def on_modified(self, event: FileSystemEvent) -> None:
            send(event)

    obs = Observer()
    obs.schedule(Handler(), path=normcase(path.parent))
    obs.start()

    while True:
        try:
            yield path.read_text("UTF-8")
        except GeneratorExit:
            obs.stop()
            break
        await chan.get()
