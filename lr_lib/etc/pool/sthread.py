# -*- coding: UTF-8 -*-
# SThread - пул потоков с авторазмером

import contextlib
import threading

from queue import Empty, PriorityQueue

import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.core.var.vars as lr_vars


LockC = threading.Lock()
LockT = threading.Lock()


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
        with LockC:
            self.count -= 1  # отрицательные - как dequeue при sort PriorityQueue
        self.task_add((self.count, Task(target, args, kwargs).execute))


class SThread(threading.Thread, SThreadIOQueue):
    '''worker поток Thread пула'''
    __slots__ = ('task', 'pool', )

    def __init__(self, queue_in: PriorityQueue, pool=None):
        self.timeout = lr_vars.SThreadExitTimeout.get()
        self.size_min = lr_vars.SThreadPoolSizeMin.get()

        SThreadIOQueue.__init__(self, queue_in)
        self.pool = pool
        self.task = None  # свободен/занят

        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()

    def run(self, is_work=True) -> None:
        '''worker-поток, выполнять task из queue_in, при простое выйти'''
        pool = self.pool  # SThreadPool
        threads = pool.threads  # потоки
        task_get = self.task_get
        task_done = self.task_done
        timeout = self.timeout
        size_min = self.size_min

        try:
            while pool.working:
                try:
                    (count, execute_task) = task_get(timeout=timeout)  # получить задачу

                except Empty:  # таймаут бездействия
                    with LockT:
                        lt = len(threads)
                    if lt > size_min:
                        return
                    continue
                except Exception as ex:
                    return lr_excepthook.excepthook(ex)

                else:
                    self.task = is_work  # поток занят
                    try:
                        execute_task()  # выполнить задачу
                        continue
                    except Exception as ex:
                        if execute_task is not None:  # ошибка/выход
                            lr_excepthook.excepthook(ex)
                        return
                    finally:
                        self.task = task_done()  # поток свободен

        finally:  # выход потока
            self.task = pool.remove_thread(self)

    def __bool__(self) -> bool:
        '''поток свободен/занят'''
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

        auto_size_SThreadPool(pool=self, timeout=lr_vars.SThreadAutoSizeTimeOut.get(), pmax=lr_vars.SThreadPoolSizeMax.get(),
                              max_th=lr_vars.SThreadPooMaxAddThread.get(), qmin=lr_vars.SThreadPoolAddMinQSize.get(),
                              set_qsize=self.set_qsize, threads=self.threads, add_thread=self.add_thread)

    def new_thread(self) -> SThread:
        '''создать новый поток'''
        return SThread(self.queue_in, pool=self)

    def add_thread(self) -> None:
        '''сохранить поток'''
        self.threads.append(self.new_thread())
        self.parent._size = self.size = len(self.threads)

    def remove_thread(self, th: SThread) -> None:
        '''удалить поток'''
        with contextlib.suppress(ValueError), LockT:
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


def auto_size_SThreadPool(pool: SThreadPool, timeout: int, pmax: int, max_th: int, qmin: int, set_qsize: callable,
                          threads: [SThread, ], add_thread: callable, restart=lr_vars.Tk.after) -> None:
    '''создать новый поток, если есть очередь, недостигнут maxsize, и все потоки заняты'''
    with LockT:
        qs = set_qsize()
        ps = pool.size

        if qs and (ps < pmax) and all(threads):
            th_count = divmod(qs, qmin)[0]  # 1 поток на каждый MinQSize
            if th_count:
                if th_count > max_th:
                    th_count = max_th
                if pmax < (th_count + qs):
                    th_count = (pmax - qs)
            else:
                th_count = 1

            for _ in range(th_count):
                add_thread()  # создать

    if pool.working:  # перезапуск auto_size_SThreadPool
        restart(timeout, auto_size_SThreadPool, pool, timeout, pmax, max_th, qmin, set_qsize, threads, add_thread)
