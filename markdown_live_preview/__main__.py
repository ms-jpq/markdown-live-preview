from asyncio import run
from sys import stderr

from .server.main import main

try:
    run(main())
except KeyboardInterrupt:
    stderr.close()
