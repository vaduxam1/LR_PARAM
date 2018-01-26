# -*- coding: UTF-8 -*-
# пулы потоков

import sys
import contextlib
import concurrent.futures
import multiprocessing.pool
import multiprocessing.dummy
import asyncio
import queue
import threading
import tkinter

from lr_lib import (
    defaults,
    other as lr_other,
)


class MainThreadUpdater:
    '''выполнить из main потока(например если что-то нельзя(RuntimeError) выполнять в потоке)'''
    def __init__(self):
        self.queue_in = queue.Queue()
        self.working = None
        defaults.MainThreadUpdater = self

    def __enter__(self):
        self.working = True
        defaults.Tk.after(0, self.queue_listener)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.working = False
        if exc_type:
            lr_other.excepthook(exc_type, exc_val, exc_tb)
        return exc_type, exc_val, exc_tb

    def submit(self, callback: callable) -> None:
        '''выполнить callback, из main потока'''
        self.queue_in.put_nowait(callback)

    def queue_listener(self) -> None:
        '''выполнять из очереди, пока есть, затем перезапустить'''
        while not self.queue_in.empty():
            try:  # выполнить
                callback = self.queue_in.get()
                callback()
            except Exception:
                lr_other.excepthook(*sys.exc_info())
                continue

        if defaults.Window:  # отображение всякого инфо
            defaults.Window.auto_update_action_pool_lab()

        if self.working:  # перезапуск
            defaults.Tk.after(defaults.MainThreadUpdateTime.get(), self.queue_listener)


class SThreadIOQueue:
    '''priority_DeQueue_in -> queue_out'''
    count = 0  # count -= 1 для de-queue для sort в PriorityQueue

    def __init__(self, queue_in: queue.PriorityQueue, queue_out: queue.Queue):
        self.queue_in = queue_in
        self.queue_out = queue_out

    def submit(self, target: callable, *args, **kwargs) -> None:
        '''выполнить target, последняя зашедшая, выполнится первой'''
        SThreadIOQueue.count -= 1  # отрицательные - как dequeue при sort PriorityQueue
        self.queue_in.put_nowait((SThreadIOQueue.count, dict(target=target, args=args, kwargs=kwargs)))

    def map(self, fn: callable, args: tuple) -> iter:
        '''выполнить target's и получить результаты'''
        e = 0
        for e, a in enumerate(args, start=1):
            self.submit(fn, a)

        for _ in range(e):
            yield self.queue_out.get()  # результат


class SThread(threading.Thread, SThreadIOQueue):
    '''worker поток Thread пула'''
    def __init__(self, queue_in: queue.PriorityQueue, queue_out: queue.Queue, pool=None):
        threading.Thread.__init__(self)
        SThreadIOQueue.__init__(self, queue_in, queue_out)
        self.setDaemon(True)

        self.task = {}  # текущая задача
        self.pool = pool
        # тут, тк RuntimeError: main thread is not in main loop
        self._timeout = defaults.SThreadExitTimeout.get()
        self._size_min = defaults.SThreadPoolSizeMin.get()

        self.start()

    def run(self) -> None:
        '''поток'''
        try:
            while self.pool.working:
                out = None
                try:  # получить задачу
                    _num, self.task = self.queue_in.get(timeout=self._timeout)
                    try:  # выполнить задачу
                        out = self.task['target'](*self.task['args'], **self.task['kwargs'])
                    except Exception:  # выход
                        return '' if (self.task is None) else lr_other.excepthook(*sys.exc_info())
                    finally:  # вернуть результат
                        self.queue_out.put_nowait(out)
                        self.queue_in.task_done()
                        self.task = {}
                except queue.Empty:  # таймаут
                    if len(self.pool.threads) > self._size_min:
                        return
        finally:  # выход потока
            self.pool.remove_thread(self)
            self.task = {}


class SThreadPool(SThreadIOQueue):
    '''threading.Thread пул'''
    def __init__(self, size=defaults.cpu_count, parent=None):
        SThreadIOQueue.__init__(self, queue_in=queue.PriorityQueue(), queue_out=queue.Queue())
        self.parent = parent
        self.working = True

        self.threads = []
        self.size = size

        for _ in range(self.size):
            self.add_thread()

        auto_size_SThreadPool(self)

    def new_thread(self) -> SThread:
        '''создать новый поток'''
        return SThread(self.queue_in, self.queue_out, pool=self)

    def add_thread(self) -> None:
        '''сохранить поток'''
        self.threads.append(self.new_thread())
        self.parent._size = self.size = len(self.threads)

    def remove_thread(self, th: SThread) -> None:
        '''удалить поток'''
        with contextlib.suppress(ValueError):
            self.threads.remove(th)
            self.parent._size = self.size = len(self.threads)

    def close(self) -> None:
        self.working = False
        for _ in range(defaults.SThreadPoolSizeMax.get()):
            self.queue_in.put_nowait((0, None))


def auto_size_SThreadPool(pool: SThreadPool, th_count=0) -> None:
    '''создать новый поток, если есть очередь, недостигнут maxsize, и все потоки заняты'''
    qsize = pool.queue_in.qsize()
    if qsize and (pool.size <= defaults.SThreadPoolSizeMax.get()) and all(th.task for th in pool.threads):
        th_count = divmod(qsize, defaults.SThreadPoolAddMinQSize.get())[0]  # 1 поток на каждый MinQSize
        if not th_count:
            th_count = 1
        else:
            max_th = defaults.SThreadPooMaxAddThread.get()
            if th_count > max_th:
                th_count = max_th

        for _ in range(th_count):
            if len(pool.threads) < defaults.SThreadPoolSizeMax.get():  # maxsize
                pool.add_thread()  # создать
            else:
                break

    if pool.working:  # перезапуск auto_size_SThreadPool
        defaults.Tk.after(defaults.SThreadAutoSizeTimeOut.get(), auto_size_SThreadPool, pool)


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


class POOL:
    '''пул потоков, с возможностью выбора его типа'''
    pools = {
        'AsyncPool': AsyncPool,
        'NoPool': NoPool,
        'SThreadPool(threading.Thread)': SThreadPool,
        'concurrent.futures.ThreadPoolExecutor': concurrent.futures.ThreadPoolExecutor,
        'concurrent.futures.ProcessPoolExecutor': concurrent.futures.ProcessPoolExecutor,
        'multiprocessing.Pool': multiprocessing.Pool,
        'multiprocessing.pool.Pool': multiprocessing.pool.Pool,
        'multiprocessing.pool.ThreadPool': multiprocessing.pool.ThreadPool,
        'multiprocessing.dummy.Pool': multiprocessing.dummy.Pool,
    }  # типы пулов, для создания POOL

    def __init__(self, name, size=False):
        if size is False:
            size = defaults.cpu_count

        self.size = tkinter.IntVar(value=size)  # новое кол-во потоков пула
        self.name = tkinter.StringVar(value=name)  # новое имя пула
        self._name = ''  # текущее имя пула
        self._size = 0  # текущее кол-во потоков пула

        self.pool = None  # текущий инстанс пула
        self.reset()

    def __getattr__(self, item):
        '''перенаправление вызовов в self.pool'''
        if (item == 'imap_unordered') and not hasattr(self.pool, 'imap_unordered'):
            item = 'imap'
        if item == 'imap' and not hasattr(self.pool, 'imap'):
            item = 'map'
        return getattr(self.pool, item)

    def reset(self, *args) -> None:
        '''пересоздать пул, при изменении имени/размера'''
        n = self.name.get()
        s = self.size.get()

        if not (self._size == s) or not (self._name == n):
            self.pool_exit()
            self._name, self._size = n, s

            if 'concurrent.futures.' in n:
                self.set_pool(n, max_workers=s)
            elif n in ['NoPool', 'AsyncPool']:
                self.set_pool(n)
            elif n == 'SThreadPool(threading.Thread)':
                self.set_pool(n, s, parent=self)
            else:
                self.set_pool(n, processes=s)

    def set_pool(self, name, *args, **kwargs):
        '''создать пул'''
        self.pool = self.pools[name](*args, **kwargs)
        return self.pool

    def pool_exit(self, ex=Exception) -> None:
        '''закрыть пул'''
        with contextlib.suppress(ex):
            self.pool.shutdown()
        with contextlib.suppress(ex):
            self.pool.close()
        with contextlib.suppress(ex):
            self.shutdown(wait=False)


@contextlib.contextmanager
def POOL_Creator() -> None:
    '''создание пулов'''
    try:
        defaults.M_POOL = POOL(defaults.M_POOL_NAME, defaults.M_POOL_Size)
        defaults.T_POOL = POOL(defaults.T_POOL_NAME, defaults.T_POOL_Size)
        yield
    finally:
        if defaults.M_POOL:
            defaults.M_POOL.pool_exit()
        if defaults.T_POOL:
            defaults.T_POOL.pool_exit()
