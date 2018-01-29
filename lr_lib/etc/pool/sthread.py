# -*- coding: UTF-8 -*-
# SThread - пул потоков с авторазмером

import sys
import contextlib
import queue
import threading

import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.core.var.vars as lr_vars


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
        self._timeout = lr_vars.SThreadExitTimeout.get()
        self._size_min = lr_vars.SThreadPoolSizeMin.get()

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
                        return '' if (self.task is None) else lr_excepthook.excepthook(*sys.exc_info())
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
    def __init__(self, size=lr_vars.cpu_count, parent=None):
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
        for _ in range(lr_vars.SThreadPoolSizeMax.get()):
            self.queue_in.put_nowait((0, None))


def auto_size_SThreadPool(pool: SThreadPool, th_count=0) -> None:
    '''создать новый поток, если есть очередь, недостигнут maxsize, и все потоки заняты'''
    qsize = pool.queue_in.qsize()
    if qsize and (pool.size <= lr_vars.SThreadPoolSizeMax.get()) and all(th.task for th in pool.threads):
        th_count = divmod(qsize, lr_vars.SThreadPoolAddMinQSize.get())[0]  # 1 поток на каждый MinQSize
        if not th_count:
            th_count = 1
        else:
            max_th = lr_vars.SThreadPooMaxAddThread.get()
            if th_count > max_th:
                th_count = max_th

        for _ in range(th_count):
            if len(pool.threads) < lr_vars.SThreadPoolSizeMax.get():  # maxsize
                pool.add_thread()  # создать
            else:
                break

    if pool.working:  # перезапуск auto_size_SThreadPool
        lr_vars.Tk.after(lr_vars.SThreadAutoSizeTimeOut.get(), auto_size_SThreadPool, pool)
