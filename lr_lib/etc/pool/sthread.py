# -*- coding: UTF-8 -*-
# SThread - пул потоков с авторазмером

import sys
import contextlib
import queue
import threading

import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.core.var.vars as lr_vars


class Task:
    '''задача для пула'''
    __slots__ = ('target', 'args', 'kwargs', 'return_callback', )

    def __init__(self, target: callable, args: tuple, kwargs: dict, return_callback: callable):
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.return_callback = return_callback

    def execute(self) -> None:
        '''выполнить задачу'''
        self.return_callback(self.target(*self.args, **self.kwargs))


class SThreadIOQueue:
    '''priority_DeQueue_in -> queue_out'''
    count = 0  # count -= 1 для de-queue для sort в PriorityQueue

    def __init__(self, queue_in: queue.PriorityQueue, queue_out: queue.Queue):
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.return_callback = self.queue_out.put_nowait

    def submit(self, target: callable, *args, **kwargs) -> None:
        '''выполнить target, последняя зашедшая, выполнится первой'''
        SThreadIOQueue.count -= 1  # отрицательные - как dequeue при sort PriorityQueue
        self.queue_in.put_nowait((SThreadIOQueue.count, Task(target, args, kwargs, self.return_callback).execute))

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
        self.start()

    def run(self) -> None:
        '''поток'''
        done = self.queue_in.task_done
        pool = self.pool
        task_get = self.queue_in.get
        _timeout = lr_vars.SThreadExitTimeout.get()
        _size_min = lr_vars.SThreadPoolSizeMin.get()

        try:
            while pool.working:
                try:
                    _, self.task = task_get(timeout=_timeout)  # получить задачу
                    try:
                        self.task()  # выполнить задачу
                    except Exception:
                        return '' if (self.task is None) else lr_excepthook.excepthook(*sys.exc_info())  # выход
                    finally:
                        self.task = done()  # поток незанят
                except queue.Empty:  # таймаут
                    if len(pool.threads) > _size_min:
                        return None
        finally:  # выход потока
            self.task = pool.remove_thread(self)

    def __bool__(self) -> bool:
        return bool(self.task)


class SThreadPool(SThreadIOQueue):
    '''threading.Thread пул'''
    def __init__(self, size=lr_vars.cpu_count, parent=None):
        SThreadIOQueue.__init__(self, queue_in=queue.PriorityQueue(), queue_out=queue.Queue())
        self.parent = parent
        self.working = True

        self.threads = []  # workers
        self.size = size  # размер пула
        self._q_size = 0  # размер очереди

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
        for _ in range(lr_vars.SThreadPoolSizeMax.get()):
            self.queue_in.put_nowait((0, None))

    def qsize(self) -> int:
        '''размер queue_in'''
        self._q_size = self.queue_in.qsize()
        return self._q_size


def auto_size_SThreadPool(pool: SThreadPool, restart=lr_vars.Tk.after, timeout=lr_vars.SThreadAutoSizeTimeOut.get,
                          pmax=lr_vars.SThreadPoolSizeMax.get, pmin=lr_vars.SThreadPooMaxAddThread.get,
                          qmin=lr_vars.SThreadPoolAddMinQSize.get) -> None:
    '''создать новый поток, если есть очередь, недостигнут maxsize, и все потоки заняты'''
    qs = pool.qsize()
    if qs and (pool.size <= pmax()) and all(pool.threads):
        th_count = divmod(qs, qmin())[0]  # 1 поток на каждый MinQSize
        if th_count:
            max_th = pmin()
            if th_count > max_th:
                th_count = max_th
        else:
            th_count = 1

        for _ in range(th_count):
            pool.add_thread()  # создать

    if pool.working:  # перезапуск auto_size_SThreadPool
        restart(timeout(), auto_size_SThreadPool, pool)
