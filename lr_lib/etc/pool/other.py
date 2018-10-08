# -*- coding: UTF-8 -*-
# примеры разных пулов потоков + (запуск подсветки линий tk_text в MainThreadUpdater)

import contextlib
# import asyncio
import queue
import sys

import lr_lib
import lr_lib.core.var.vars as lr_vars


class MainThreadUpdater:
    """выполнить из main потока(например если что-то нельзя(RuntimeError) выполнять в потоке)"""
    def __init__(self):
        self.working = None
        self.queue_in = queue.Queue()  # очередь выполнения callback
        return

    def submit(self, callback: callable) -> None:
        """добавить в очередь выполнения"""
        self.queue_in.put(callback)
        return

    @contextlib.contextmanager
    def init(self) -> iter:
        """вызов _queue_listener"""
        self.working = True  # разрешить перезапуск _queue_listener
        try:
            self._queue_listener()
            yield self
        finally:  # запретить перезапуск _queue_listener
            self.working = False
        return

    def _queue_listener(self) -> None:
        """выполнять из очереди, пока есть, затем перезапустить"""
        while self.queue_in.qsize():
            try:  # получить и выполнить callback
                callback = self.queue_in.get()
                callback()
            except Exception as ex:
                lr_lib.etc.excepthook.excepthook(ex)
            continue

        if self.working:
            lr_vars.Tk.after(lr_vars.MainThreadUpdateTime.get(), self._queue_listener)  # перезапуск
        return


class NoPool:
    """заглушка пула для однопоточного выполнения, для POOL_"""
    @staticmethod
    def map(fn: callable, args: tuple) -> iter:
        yield from map(fn, args)
        return

    def submit(self, func: callable, *args, **kwargs):
        return func(*args, **kwargs)


# @asyncio.coroutine
# def async_worker(executor: callable, fn: callable, args: tuple, e=None):
#     result = yield from executor(e, fn, args)
#     return result
#
#
# class AsyncPool:
#     """acync пул, для POOL_"""
#     def __init__(self):
#         self.loop = asyncio.get_event_loop()
#         return
#
#     def map(self, fn: callable, args: list):
#         return self.loop.run_until_complete(self.async_map(fn, args))
#
#     def submit(self, fn: callable, *args, **kwargs) -> None:
#         def callback(*_, a=args, kw=kwargs):
#             return fn(*a, **kw)
#         f = self.async_map(callback, [None])
#         return self.loop.run_until_complete(f)
#
#     @asyncio.coroutine
#     def async_map(self, fn: callable, args: list):
#         workers = [asyncio.ensure_future(async_worker(self.loop.run_in_executor, fn, a), loop=self.loop) for a in args]
#         result = yield from asyncio.gather(*workers, loop=self.loop)
#         return result
