# -*- coding: UTF-8 -*-
# M_POOL(процессы), T_POOL(потоки) пулы

import contextlib
import concurrent.futures
import multiprocessing.pool
import multiprocessing.dummy
import tkinter

import lr_lib.etc.pool.sthread as lr_sthread
import lr_lib.etc.pool.other

import lr_lib.core.var.vars as lr_vars


class POOL:
    """пул потоков, с возможностью выбора его типа"""
    pools = {
        'AsyncPool': lr_lib.etc.pool.other.AsyncPool,
        'NoPool': lr_lib.etc.pool.other.NoPool,
        'SThreadPool(threading.Thread)': lr_sthread.SThreadPool,
        'concurrent.futures.ThreadPoolExecutor': concurrent.futures.ThreadPoolExecutor,
        'concurrent.futures.ProcessPoolExecutor': concurrent.futures.ProcessPoolExecutor,
        'multiprocessing.Pool': multiprocessing.Pool,
        'multiprocessing.pool.Pool': multiprocessing.pool.Pool,
        'multiprocessing.pool.ThreadPool': multiprocessing.pool.ThreadPool,
        'multiprocessing.dummy.Pool': multiprocessing.dummy.Pool,
    }  # типы пулов, для создания POOL

    def __init__(self, name, size=False):
        if size is False:
            size = lr_vars.cpu_count

        self.size = tkinter.IntVar(value=size or 0)  # новое кол-во потоков пула
        self.name = tkinter.StringVar(value=name)  # новое имя пула
        self._name = ''  # текущее имя пула
        self._size = 0  # текущее кол-во потоков пула

        self.pool = None  # текущий инстанс пула
        self.reset()

    def __getattr__(self, item):
        """перенаправление вызовов в self.pool"""
        if (item == 'imap_unordered') and not hasattr(self.pool, 'imap_unordered'):
            item = 'imap'
        if item == 'imap' and not hasattr(self.pool, 'imap'):
            item = 'map'
        return getattr(self.pool, item)

    def reset(self, *args) -> None:
        """пересоздать пул, при изменении имени/размера"""
        n = self.name.get()
        s = self.size.get()

        if not (self._size == s) or not (self._name == n):
            self.pool_exit()
            self._name, self._size = n, s

            if 'concurrent.futures.' in n:
                self.set_pool(n, max_workers=(s or None))
            elif n in ['NoPool', 'AsyncPool']:
                self.set_pool(n)
            elif n == 'SThreadPool(threading.Thread)':
                self.set_pool(n, s, parent=self)
            else:
                self.set_pool(n, processes=s)

    def set_pool(self, name, *args, **kwargs):
        """создать пул"""
        self.pool = self.pools[name](*args, **kwargs)
        return self.pool

    def pool_exit(self, ex=Exception) -> None:
        """закрыть пул"""
        with contextlib.suppress(ex):
            self.pool.shutdown()
        with contextlib.suppress(ex):
            self.pool.close()
        with contextlib.suppress(ex):
            self.shutdown(wait=False)


@contextlib.contextmanager
def init() -> iter((POOL, POOL), ):
    """создание пулов"""
    try:
        M_POOL = POOL(lr_vars.M_POOL_NAME, lr_vars.M_POOL_Size)
        T_POOL = POOL(lr_vars.T_POOL_NAME, lr_vars.T_POOL_Size)

        yield M_POOL, T_POOL
    finally:
        lr_vars.M_POOL.pool_exit()
        lr_vars.T_POOL.pool_exit()
