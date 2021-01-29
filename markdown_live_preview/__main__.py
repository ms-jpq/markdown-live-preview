from asyncio import run
from sys import stderr

from .server.main import main

if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        stderr.close()
