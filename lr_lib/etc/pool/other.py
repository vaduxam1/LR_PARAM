# -*- coding: UTF-8 -*-
# примеры разных пулов потоков

import asyncio
import queue

import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.core.var.vars as lr_vars


class MainThreadUpdater:
    """выполнить из main потока(например если что-то нельзя(RuntimeError) выполнять в потоке)"""
    __slots__ = ('working', 'queue_in', )

    def __init__(self):
        self.working = None
        self.queue_in = queue.Queue()  # очередь выполнения callback

    def submit(self, callback: callable) -> None:
        """добавить в очередь выполнения"""
        self.queue_in.put(callback)

    def __enter__(self):
        self.working = True
        self._queue_listener()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.working = False
        if exc_type:
            lr_excepthook.excepthook(exc_type, exc_val, exc_tb)

        return exc_type, exc_val, exc_tb

    def _queue_listener(self, timeout=lr_vars.MainThreadUpdateTime.get()) -> None:
        """выполнять из очереди, пока есть, затем перезапустить"""
        while self.queue_in.qsize():
            try:  # получить и выполнить callback
                callback = self.queue_in.get()
                callback()
            except Exception as ex:
                lr_excepthook.excepthook(ex)
                continue

        if self.working:  # перезапуск
            lr_vars.Tk.after(timeout, self._queue_listener)


class NoPool:
    """заглушка пула для однопоточного выполнения, для POOL_"""
    @staticmethod
    def map(fn: callable, args: tuple) -> iter:
        yield from map(fn, args)

    def submit(self, func: callable, *args, **kwargs):
        return func(*args, **kwargs)


@asyncio.coroutine
def async_worker(executor: callable, fn: callable, args: tuple, e=None):
    result = yield from executor(e, fn, args)
    return result


class AsyncPool:
    """acync пул, для POOL_"""
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def map(self, fn: callable, args: list):
        return self.loop.run_until_complete(self.async_map(fn, args))

    def submit(self, fn: callable, *args, **kwargs) -> None:
        callback = lambda *_, a=args, kw=kwargs: fn(*a, **kw)
        return self.loop.run_until_complete(self.async_map(callback, [None]))

    @asyncio.coroutine
    def async_map(self, fn: callable, args: list):
        workers = [asyncio.ensure_future(async_worker(self.loop.run_in_executor, fn, a), loop=self.loop) for a in args]
        result = yield from asyncio.gather(*workers, loop=self.loop)
        return result
