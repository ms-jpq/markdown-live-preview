from typing import AsyncIterator, Awaitable, TypeVar

T = TypeVar("T")


def anext(aiter: AsyncIterator[T]) -> Awaitable[T]:
    return aiter.__anext__()
