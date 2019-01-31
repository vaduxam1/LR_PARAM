# -*- coding: UTF-8 -*-
# SThread - пул потоков с авторазмером

import sys
import threading
from queue import Empty, PriorityQueue

import lr_lib
import lr_lib.core.var.vars as lr_vars

DLOCK = threading.Lock()
QLOCK = threading.Lock()

Text = '''
target = {target}
   type_target = {lt} : {t_target}
args = {args}
  type_args = {la} : {t_args}
kwargs = {kwargs}
  type_kwargs = {lk} : {t_kwargs}
'''


class Task:
    """
    задача для пула
    """
    __slots__ = ('target', 'args', 'kwargs',)

    def __init__(self, target: callable, args: tuple, kwargs: dict):
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def to_str(self):
        """инфо о задаче"""
        try:
            la = len(self.args)
        except TypeError:
            la = None

        try:
            lk = len(self.kwargs)
        except TypeError:
            lk = None

        task_text = Text.format(
            target=self.target, args=self.args, kwargs=self.kwargs, t_args=str(list(map(type, self.args))),
            t_kwargs=str(list(map(type, self.kwargs.values()))), la=la, lk=lk,
            t_target=type(self.target), lt=(len(self.target) if hasattr(self.target, '__len__') else None),
        )

        return task_text


class SThreadIOQueue:
    """
    priority_DeQueue_in
    """
    __slots__ = ('priority', 'queue_in',)

    def __init__(self, queue_in: PriorityQueue):
        self.queue_in = queue_in
        self.priority = 0  # -= 1 для поведения как de-queue
        return

    def submit(self, target: callable, *args, **kwargs) -> None:
        """выполнить target, последняя зашедшая, выполнится первой"""
        QLOCK.acquire()
        self.priority -= 1  # отрицательные - для поведения как dequeue
        self.queue_in.put((self.priority, Task(target, args, kwargs)))
        QLOCK.release()
        return


class _NoPool:
    """
    заглушка пула для SThread
    """
    size = 1

    def __getattr__(self, item):
        """self.pool.working -> True"""
        return [True]


class SThread(threading.Thread, SThreadIOQueue):
    """
    worker поток Thread пула
    """
    __slots__ = ('task', 'pool', 'timeout', 'size_min',)

    def __init__(self, queue_in: PriorityQueue, pool=None):
        self.timeout = lr_vars.SThreadExitTimeout.get()
        self.size_min = lr_vars.SThreadPoolSizeMin.get()

        SThreadIOQueue.__init__(self, queue_in)
        self.pool = (pool or _NoPool())
        self.task = None  # свободен/занят

        threading.Thread.__init__(self)
        self.setDaemon(True)
        return

    def run(self) -> None:
        """
        worker-поток, выполнять task из queue_in, при простое выйти
        """
        try:
            while self.pool.working:
                try:  # получить задачу / поток занят
                    (priority, task) = self.queue_in.get(timeout=self.timeout)
                    self.task = task

                except Empty:  # таймаут бездействия
                    if self.pool.size > self.size_min:
                        return
                except Exception:
                    lr_lib.etc.excepthook.excepthook(*sys.exc_info())
                    return

                else:
                    try:  # выполнить задачу
                        task.target(*task.args, **task.kwargs)
                        continue

                    except Exception as ex:  # выход/ошибка
                        if task is None:
                            return
                        lr_lib.etc.excepthook.excepthook(ex)
                        return

                    finally:  # поток свободен
                        self.task = self.queue_in.task_done()
                continue
        finally:  # выход потока
            self.task = self.pool._remove_thread(th=self)
        return

    def __bool__(self) -> bool:
        """
        поток свободен/занят
        """
        return bool(self.task)


class SThreadPool(SThreadIOQueue):
    """
    threading.Thread пул
    """
    __slots__ = ('_qsize', 'threads', 'parent', 'working', 'size',)

    def __init__(self, size=lr_vars.cpu_count, parent=None):
        self.parent = parent

        SThreadIOQueue.__init__(self, queue_in=PriorityQueue())
        self._qsize = self.queue_in.qsize()  # размер очереди

        self.size = size  # размер пула
        self.threads = []  # workers

        self.working = True
        self.thread_create(th_count=self.size)

        self._auto_size(timeout=lr_vars.SThreadAutoSizeTimeOut.get(), pmax=lr_vars.SThreadPoolSizeMax.get(),
                        max_th=lr_vars.SThreadPooMaxAddThread.get(), qmin=lr_vars.SThreadPoolAddMinQSize.get())
        return

    def thread_create(self, th_count=1) -> None:
        """
        создать, сохранить и запустить worker-поток
        """
        for _ in range(th_count):
            th = self._create_thread()
            DLOCK.acquire()
            self.threads.append(th)
            self._set_pool_size()
            DLOCK.release()
            th.start()
            continue
        return

    def _create_thread(self) -> SThread:
        """
        создать worker-поток
        """
        th = SThread(self.queue_in, pool=self)
        # print(' + add {}, from: {}'.format(th.name, threading.current_thread().name))
        return th

    def _remove_thread(self, th: SThread) -> None:
        """
        удалить поток
        """
        DLOCK.acquire()
        try:
            self.threads.remove(th)
        except ValueError as ex:
            pass
        self._set_pool_size()
        # print(' - del {}, from: {}'.format(th.name, threading.current_thread().name))
        DLOCK.release()
        return

    def _set_pool_size(self) -> None:
        """
        сохранить размер пула
        """
        self.parent._size = self.size = len(self.threads)
        return

    def close(self) -> None:
        """
        выход
        """
        self.working = False
        for _ in range(lr_vars.SThreadPoolSizeMax.get()):
            self.queue_in.put((0, None))
            continue
        return

    def _auto_size(self, timeout: int, pmax: int, max_th: int, qmin: int) -> None:
        """
        создать новый поток, если есть очередь, недостигнут maxsize, и все потоки заняты
        """
        self._qsize = self.queue_in.qsize()

        if self._qsize:
            t_max = (pmax - self.size)
            if (t_max > 0) and all(self.threads):
                th_count = divmod(self._qsize, qmin)[0]  # 1 поток на каждый MinQSize
                if th_count:
                    if th_count > max_th:
                        th_count = max_th
                else:
                    th_count = 1

                if th_count > t_max:
                    th_count = t_max

                self.thread_create(th_count=th_count)  # создать

        if self.working:  # перезапуск auto_size_SThreadPool
            lr_vars.Tk.after(timeout, self._auto_size, timeout, pmax, max_th, qmin)
        return
