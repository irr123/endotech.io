import asyncio as _asyncio
import functools as _functools
import logging as _logging
import os as _os
import signal as _signal
import typing as _t


class _Hidden:
    exclude_logging = (
        "asyncio",
        "httpcore.connection",
        "httpcore.http11",
        "httpx",
        "openai._base_client",
    )
    default_conf = {
        "OPENAI_MODEL": "gpt-4o-mini",
    }

    class Gather:
        def __init__(self) -> None:
            self.coro = []
            self.index = {}

        def append(self, name, func) -> None:
            self.coro.append(func)
            self.index[len(self.coro) - 1] = name

        async def run(self) -> dict[_t.Any, _t.Any]:
            res, tmp = {}, await _asyncio.gather(*self.coro)
            for i, r in enumerate(tmp):
                res[self.index[i]] = r

            self.coro = []
            self.index = {}

            return res

    @staticmethod
    def once_decorator(func):
        value = None

        @_functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal value
            if value is None:
                value = func(*args, **kwargs)
            return value

        return wrapper

    class Config:
        def __init__(self, initial: None | dict = None) -> None:
            self._cache = initial or {}

        def __getattr__(self, name: str) -> str:
            if name in self._cache:
                return self._cache[name]

            value = _os.getenv(name)
            if value is None:
                raise AttributeError(f"Environment variable '{name}' not found.")

            self._cache[name] = value
            return value


class Bootstrap:
    @staticmethod
    def gather():
        return _Hidden.Gather()

    def __init__(self) -> None:
        self.__loop: _asyncio.AbstractEventLoop | None = None

    @property
    def log(self) -> _logging.Logger:
        return self.__setup_logger(_logging.NOTSET)

    @property
    def conf(self) -> _Hidden.Config:
        return self.__setup_conf(_Hidden.default_conf)

    @property
    def loop(self) -> _asyncio.AbstractEventLoop:
        if self.__loop is None:
            self.__loop = _asyncio.new_event_loop()
            self.__loop.set_exception_handler(self._error_handler)
            for sig in (_signal.SIGINT, _signal.SIGTERM):
                self.__loop.add_signal_handler(sig, self._shutdown_handler, sig)
            _asyncio.set_event_loop(self.__loop)
        return self.__loop

    def _error_handler(self, _: _asyncio.AbstractEventLoop, context: dict):
        self.__loop.default_exception_handler(context)
        exc = context.get("exception")
        if exc is not None:
            self._shutdown_handler(_signal.SIGUSR1)
            raise exc

    def _shutdown_handler(self, sig) -> None:
        async def shutdown():
            tasks: list[_asyncio.Task] = [
                t
                for t in _asyncio.all_tasks(loop=self.loop)
                if t is not _asyncio.current_task(loop=self.loop)
            ]
            _ = [task.cancel(f"shutdown {sig}") for task in tasks]
            await _asyncio.gather(*tasks, return_exceptions=True)
            self.loop.stop()

        self.loop.create_task(shutdown())

    @_Hidden.once_decorator
    def __setup_logger(self, level: int) -> _logging.Logger:
        logger = _logging.root
        logger.setLevel(level)
        handler = _logging.StreamHandler()
        handler.setLevel(level)
        formatter = _logging.Formatter(
            "[%(asctime)s] %(name)s(%(levelno)s): %(message)s",
            "%d-%m-%Y %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        for target in _Hidden.exclude_logging:
            _logging.getLogger(target).setLevel(_logging.WARNING)

        return logger

    @_Hidden.once_decorator
    def __setup_conf(self, initial: None | dict = None) -> _Hidden.Config:
        return _Hidden.Config(initial)
