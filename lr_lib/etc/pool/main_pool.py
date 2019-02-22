# -*- coding: UTF-8 -*-
# M_POOL(процессы), T_POOL(потоки) пулы

import concurrent.futures
import multiprocessing.dummy
import multiprocessing.pool
import tkinter
from typing import Any

import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.pool.other
import lr_lib.etc.pool.sthread


STPName = 'SThreadPool(threading.Thread)'
NAPName = ['NoPool', 'AsyncPool', ]


class POOL:
    """
    пул потоков, с возможностью выбора его типа
    """
    pools = {
        # NAPName[1]: lr_lib.etc.pool.other.AsyncPool,
        NAPName[0]: lr_lib.etc.pool.other.NoPool,
        STPName: lr_lib.etc.pool.sthread.SThreadPool,
        'concurrent.futures.ThreadPoolExecutor': concurrent.futures.ThreadPoolExecutor,
        'concurrent.futures.ProcessPoolExecutor': concurrent.futures.ProcessPoolExecutor,
        'multiprocessing.Pool': multiprocessing.Pool,
        'multiprocessing.pool.Pool': multiprocessing.pool.Pool,
        'multiprocessing.pool.ThreadPool': multiprocessing.pool.ThreadPool,
        'multiprocessing.dummy.Pool': multiprocessing.dummy.Pool,
    }  # типы пулов, для создания POOL

    def __init__(self, name: str, size=False):
        if size is False:
            size = lr_vars.cpu_count

        self.size = tkinter.IntVar(value=size or 0)  # новое кол-во потоков пула
        self.name = tkinter.StringVar(value=name)  # новое имя пула
        self._name = ''  # текущее имя пула
        self._size = 0  # текущее кол-во потоков пула

        self.pool = None  # текущий инстанс пула
        self.reset()
        return

    def __getattr__(self, item: str) -> Any:
        """
        перенаправление вызовов в self.pool
        """
        if (item == 'imap_unordered') and (not hasattr(self.pool, 'imap_unordered')):
            item = 'imap'
        if (item == 'imap') and (not hasattr(self.pool, 'imap')):
            item = 'map'

        attr = getattr(self.pool, item)
        return attr

    def reset(self, *args) -> None:
        """
        пересоздать пул, при изменении имени/размера
        """
        n = self.name.get()
        s = self.size.get()

        if (not (self._size == s)) or (not (self._name == n)):
            self.pool_exit()
            (self._name, self._size) = (n, s)

            if 'concurrent.futures.' in n:
                m = (s or None)
                self.set_pool(n, max_workers=m)
            elif n in NAPName:
                self.set_pool(n)
            elif n == STPName:
                self.set_pool(n, s, parent=self)
            else:
                self.set_pool(n, processes=s)
        return

    def set_pool(self, name: str, *args, **kwargs):
        """
        создать пул
        """
        pool = self.pools[name]
        pool = pool(*args, **kwargs)
        self.pool = pool
        return pool

    def pool_exit(self) -> None:
        """закрыть пул"""
        try:
            self.pool.shutdown()
        except Exception as ex:
            pass
        try:
            self.pool.close()
        except Exception as ex:
            pass
        try:
            self.shutdown(wait=False)
        except Exception as ex:
            pass
        return


def init() -> None:
    """
    создание пулов
    """
    lr_vars.M_POOL = POOL(lr_vars.M_POOL_NAME, lr_vars.M_POOL_Size)
    lr_vars.T_POOL = POOL(lr_vars.T_POOL_NAME, lr_vars.T_POOL_Size)
    return


def exit() -> None:
    lr_vars.M_POOL.pool_exit()
    lr_vars.T_POOL.pool_exit()
    return
