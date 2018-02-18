# -*- coding: UTF-8 -*-
# примеры разных пулов потоков

import sys
import asyncio
import queue

import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.core.var.vars as lr_vars


class MainThreadUpdater:
    '''выполнить из main потока(например если что-то нельзя(RuntimeError) выполнять в потоке)'''
    __slots__ = ('working', 'submit', 'queue_in', )

    def __init__(self):
        self.working = None
        self.queue_in = queue.Queue()
        self.submit = self.queue_in.put_nowait

    def __enter__(self):
        self.working = True

        mainThread_queue_listener(updater=self, get_callback=self.queue_in.get, check=self.queue_in.qsize,
                                  timeout=lr_vars.MainThreadUpdateTime.get())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.working = False

        if exc_type:
            lr_excepthook.excepthook(exc_type, exc_val, exc_tb)
        return exc_type, exc_val, exc_tb


def mainThread_queue_listener(updater: MainThreadUpdater, get_callback: callable, check: callable, timeout: int,
                              restart=lr_vars.Tk.after) -> None:
    '''выполнять из очереди, пока есть, затем перезапустить'''
    while check():
        try:
            get_callback()()  # получить и выполнить callback
        except Exception as ex:
            lr_excepthook.excepthook(ex)
            continue

    if updater.working:  # перезапуск
        restart(timeout, mainThread_queue_listener, updater, get_callback, check, timeout)


class NoPool:
    '''заглушка пула для однопоточного выполнения, для POOL_'''
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
    '''acync пул, для POOL_'''
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def map(self, fn: callable, args: list):
        return self.loop.run_until_complete(self.async_map(fn, args))

    @asyncio.coroutine
    def async_map(self, fn: callable, args: list):
        workers = [asyncio.ensure_future(async_worker(self.loop.run_in_executor, fn, a), loop=self.loop) for a in args]
        result = yield from asyncio.gather(*workers, loop=self.loop)
        return result
