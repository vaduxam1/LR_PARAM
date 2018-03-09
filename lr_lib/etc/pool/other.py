# -*- coding: UTF-8 -*-
# примеры разных пулов потоков + (запуск подсветки линий tk_text в MainThreadUpdater)

import contextlib
import asyncio
import queue
import sys

import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.core.var.vars as lr_vars


class MainThreadUpdater:
    """выполнить из main потока(например если что-то нельзя(RuntimeError) выполнять в потоке)
    + HighlightLines """
    __slots__ = ('working', 'queue_in', )

    def __init__(self):
        self.working = None
        self.queue_in = queue.Queue()  # очередь выполнения callback

    def submit(self, callback: callable) -> None:
        """добавить в очередь выполнения"""
        self.queue_in.put(callback)

    @contextlib.contextmanager
    def init(self) -> iter:
        """вызов _queue_listener"""
        self.working = True  # разрешить перезапуск _queue_listener
        try:
            self._queue_listener()
            yield self
        finally:  # запретить перезапуск _queue_listener
            self.working = False

    def _queue_listener(self, timeout=lr_vars.MainThreadUpdateTime.get()) -> None:
        """выполнять из очереди, пока есть, затем перезапустить"""
        while self.queue_in.qsize():
            try:  # получить и выполнить callback
                callback = self.queue_in.get()
                callback()
            except Exception:
                lr_excepthook.excepthook(*sys.exc_info())
                continue

        ob = self.working  # bool или lr_highlight.HighlightLines()
        if ob:
            lr_vars.Tk.after(timeout, self._queue_listener)  # перезапуск

            try:  # подсветка линий текста на экране
                highlight_need = ob.highlight_need
            except AttributeError:
                return
            else:
                if highlight_need:
                    lr_vars.Tk.after(ob.HighlightAfter1, ob._highlight_top_bottom_lines, ob.on_srean_line_nums)


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
