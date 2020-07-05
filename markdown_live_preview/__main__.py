from asyncio import run

from .server.main import main

if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        exit()
