from asyncio import run
from sys import exit, stderr

from .server.main import main

try:
    code = run(main())
except KeyboardInterrupt:
    stderr.close()
    exit(130)
else:
    exit(code)
