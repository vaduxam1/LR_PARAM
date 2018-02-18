# -*- coding: UTF-8 -*-
# SThread - пул потоков с авторазмером

import sys
import contextlib
import threading

from queue import Empty, PriorityQueue, Queue

import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.core.var.vars as lr_vars


class Task:
    '''задача для пула'''
    __slots__ = ('target', 'args', 'kwargs', )

    def __init__(self, target: callable, args: tuple, kwargs: dict):
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def execute(self) -> None:
        '''выполнить задачу'''
        self.target(*self.args, **self.kwargs)


class SThreadIOQueue:
    '''priority_DeQueue_in'''
    __slots__ = ('qsize', 'count', 'task_add', 'task_get', 'task_done', 'queue_in', )

    def __init__(self, queue_in: PriorityQueue):
        self.count = 0  # count -= 1 для de-queue для sort в PriorityQueue

        self.queue_in = queue_in
        self.qsize = self.queue_in.qsize

        self.task_add = queue_in.put_nowait
        self.task_get = queue_in.get
        self.task_done = queue_in.task_done

    def submit(self, target: callable, *args, **kwargs) -> None:
        '''выполнить target, последняя зашедшая, выполнится первой'''
        self.count -= 1  # отрицательные - как dequeue при sort PriorityQueue
        self.task_add((self.count, Task(target, args, kwargs).execute))


class SThread(threading.Thread, SThreadIOQueue):
    '''worker поток Thread пула'''
    def __init__(self, queue_in: PriorityQueue, pool=None):
        threading.Thread.__init__(self)
        SThreadIOQueue.__init__(self, queue_in)

        self.pool = pool
        self.task = None  # свободен/занят

        self.setDaemon(True)
        self.start()

    def run(self, is_work=True) -> None:
        '''worker-поток, выполнять task из queue_in, при простое выйти'''
        pool = self.pool  # SThreadPool
        threads = pool.threads  # потоки
        task_get = self.task_get  # получить задачу
        task_done = self.task_done  # поток незанят
        timeout = lr_vars.SThreadExitTimeout.get()
        size_min = lr_vars.SThreadPoolSizeMin.get()

        try:
            while pool.working:
                try:
                    (_, execute_task) = task_get(timeout=timeout)
                    self.task = is_work
                    try:
                        execute_task()  # выполнить задачу
                    except Exception:
                        return '' if (execute_task is None) else lr_excepthook.excepthook(*sys.exc_info())  # выход
                    finally:
                        self.task = task_done()
                except Empty:  # таймаут
                    if len(threads) > size_min:
                        return None
        finally:  # выход потока
            self.task = pool.remove_thread(self)

    def __bool__(self) -> bool:
        return bool(self.task)


class SThreadPool(SThreadIOQueue):
    '''threading.Thread пул'''
    __slots__ = ('_qsize', 'threads', 'parent', 'working', 'size', )

    def __init__(self, size=lr_vars.cpu_count, parent=None):
        SThreadIOQueue.__init__(self, queue_in=PriorityQueue())
        self.parent = parent
        self.working = True

        self.threads = []  # workers
        self.size = size  # размер пула

        self._qsize = 0  # размер очереди

        for _ in range(self.size):
            self.add_thread()

        auto_size_SThreadPool(self, lr_vars.Tk.after, lr_vars.SThreadAutoSizeTimeOut.get(), lr_vars.SThreadPoolSizeMax.get(),
                              lr_vars.SThreadPooMaxAddThread.get(), lr_vars.SThreadPoolAddMinQSize.get(), self.set_qsize,
                              self.threads, self.add_thread)

    def new_thread(self) -> SThread:
        '''создать новый поток'''
        return SThread(self.queue_in, pool=self)

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
        for _ in range(lr_vars.SThreadPoolSizeMax.get()):
            self.queue_in.put_nowait((0, None))

    def set_qsize(self) -> int:
        '''размер queue_in'''
        self._qsize = qsize = self.qsize()
        return qsize


def auto_size_SThreadPool(pool: SThreadPool, restart: callable, timeout: int, pmax: int, pmin: int, qmin: int,
                          set_qsize: callable, threads: [SThread, ], add_thread: callable) -> None:
    '''создать новый поток, если есть очередь, недостигнут maxsize, и все потоки заняты'''
    qs = set_qsize()
    if qs and (pool.size <= pmax) and all(threads):
        th_count = divmod(qs, qmin)[0]  # 1 поток на каждый MinQSize
        if th_count:
            max_th = pmin
            if th_count > max_th:
                th_count = max_th
        else:
            th_count = 1

        for _ in range(th_count):
            add_thread()  # создать

    if pool.working:  # перезапуск auto_size_SThreadPool
        restart(timeout, auto_size_SThreadPool, pool, restart, timeout, pmax, pmin, qmin, set_qsize, threads, add_thread)
