# -*- coding: UTF-8 -*-
# SThread - пул потоков с авторазмером

import sys
import contextlib
import threading

from queue import Empty, PriorityQueue

import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.core.var.vars as lr_vars


class Task:
    """задача для пула"""
    __slots__ = ('target', 'args', 'kwargs', )

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

        task_text = '''
    target = {target}
       type_target = {lt} : {t_target}
    args = {args}
      type_args = {la} : {t_args}
    kwargs = {kwargs}
      type_kwargs = {lk} : {t_kwargs}
        '''.format(target=self.target, args=self.args, kwargs=self.kwargs, t_args=str(list(map(type, self.args))),
                   t_kwargs=str(list(map(type, self.kwargs.values()))), la=la, lk=lk,
                   t_target=type(self.target), lt=(len(self.target) if hasattr(self.target, '__len__') else None))

        return task_text


class SThreadIOQueue:
    """priority_DeQueue_in"""
    __slots__ = ('count', 'queue_in', )

    def __init__(self, queue_in: PriorityQueue):
        self.count = 0  # count -= 1 для de-queue для sort в PriorityQueue
        self.queue_in = queue_in

    def submit(self, target: callable, *args, **kwargs) -> None:
        """выполнить target, последняя зашедшая, выполнится первой"""
        self.count -= 1  # отрицательные - как dequeue при sort PriorityQueue
        self.queue_in.put_nowait((self.count, Task(target, args, kwargs)))


class _NoPool:
    """заглушка пула для SThread"""
    def __getattr__(self, item):
        """self.pool.working -> True"""
        return [True]


class SThread(threading.Thread, SThreadIOQueue):
    """worker поток Thread пула"""
    __slots__ = ('task', 'pool', 'timeout', 'size_min',)

    def __init__(self, queue_in: PriorityQueue, pool=None):
        self.timeout = lr_vars.SThreadExitTimeout.get()
        self.size_min = lr_vars.SThreadPoolSizeMin.get()

        SThreadIOQueue.__init__(self, queue_in)
        self.pool = pool or _NoPool()
        self.task = None  # свободен/занят

        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self) -> None:
        """worker-поток, выполнять task из queue_in, при простое выйти"""
        try:
            while self.pool.working:
                try:  # получить задачу / поток занят
                    (count, self.task) = self.queue_in.get(timeout=self.timeout)

                except Empty:  # таймаут бездействия
                    if len(self.pool.threads) > self.size_min:
                        return
                    continue
                except Exception as ex:
                    return lr_excepthook.excepthook(ex)

                else:
                    try:  # выполнить задачу
                        self.task.target(*self.task.args, **self.task.kwargs)

                    except Exception:
                        if self.task is not None:  # ошибка
                            lr_excepthook.excepthook(*sys.exc_info())
                        return
                    else:
                        continue
                    finally:  # поток свободен
                        self.task = self.queue_in.task_done()

        finally:  # выход потока
            self.task = self.pool._remove_thread(th=self)

    def __bool__(self) -> bool:
        """поток свободен/занят"""
        return bool(self.task)


class SThreadPool(SThreadIOQueue):
    """threading.Thread пул"""
    __slots__ = ('_qsize', 'threads', 'parent', 'working', 'size', )

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

    def thread_create(self, th_count=1) -> None:
        """создать, сохранить и запустить worker-поток"""
        for _ in range(th_count):
            th = self._create_thread()
            self.threads.append(th)

            self._set_pool_size()
            th.start()

    def _create_thread(self) -> SThread:
        """создать worker-поток"""
        th = SThread(self.queue_in, pool=self)
        return th

    def _remove_thread(self, th: SThread) -> None:
        """удалить поток"""
        with contextlib.suppress(ValueError):
            self.threads.remove(th)

        self._set_pool_size()

    def _set_pool_size(self) -> None:
        """сохранить размер пула"""
        self.parent._size = self.size = len(self.threads)

    def close(self) -> None:
        self.working = False
        for _ in range(lr_vars.SThreadPoolSizeMax.get()):
            self.queue_in.put_nowait((0, None))

    def _auto_size(self, timeout: int, pmax: int, max_th: int, qmin: int) -> None:
        """создать новый поток, если есть очередь, недостигнут maxsize, и все потоки заняты"""
        self._qsize = self.queue_in.qsize()

        if self._qsize and (self.size < pmax) and all(self.threads):
            th_count = divmod(self._qsize, qmin)[0]  # 1 поток на каждый MinQSize

            if th_count:
                if th_count > max_th:
                    th_count = max_th
                if pmax < (th_count + self._qsize):
                    th_count = (pmax - self._qsize)
            else:
                th_count = 1

            self.thread_create(th_count=th_count)  # создать

        if self.working:  # перезапуск auto_size_SThreadPool
            lr_vars.Tk.after(timeout, self._auto_size, timeout, pmax, max_th, qmin)
