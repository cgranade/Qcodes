from typing import TypeVar, Awaitable, Generator
import asyncio
from contextlib import contextmanager

T = TypeVar('T')

def sync(task : Awaitable[T]) -> T:
    loop : asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop.is_running():
        # We can't run in the same event loop that's already
        # running, so spawn a new thread.
        raise RuntimeError(
            r"Cannot run synchronously when an event loop is already running. "
            r"Please make sure to use sync() only at the outermost level in your "
                 r"call stack. "
            r"If you are using IPython's %autoawait extension, please use await the "
                 r"async version of this function/method, or disable %autoawait."
        )
    else:
        return loop.run_until_complete(task)

@contextmanager
def cancelling(*tasks : asyncio.Future) -> Generator[None, None, None]:
    try:
        yield
    finally:
        exceptions = []
        for task in tasks:
            try:
                task.cancel()
            except Exception as ex:
                pass
        if exceptions:
            if len(exceptions) == 1:
                raise exceptions[0]
            else:
                raise RuntimeError(
                    "Multiple exceptions occurred cancelling tasks:\n" +
                    "\n".join(
                        f"- {ex}" for ex in exceptions
                    )
                )

