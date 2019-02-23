# -*- coding: UTF-8 -*-
# инфо о системе

import sys
from typing import Iterable, List, Tuple


def system_info() -> Iterable[str]:
    """
    всякая ненужная инфа(при старте скрипта)
    """
    s = str_separator('\n'.join(_system_info()).lstrip('\n'))
    return s


def _system_info() -> Iterable[str]:
    """
    всякая ненужная инфа(при старте скрипта)
    """
    replace_dt = {ord(s): '' for s in "(')"}

    def attrs_from_all_objs() -> (object, 'attrs',):
        """
        объект_источник_инфы, "атрибуты, "
        """
        yield sys, 'dont_write_bytecode, executable, getdefaultencoding, ' \
                   'getfilesystemencoding, getwindowsversion, implementation, platform, exc_info, '
        import platform
        yield platform, '_sys_version, architecture, uname, win32_ver, '
        try:
            import psutil
            yield psutil, 'cpu_count, virtual_memory, users, '
        except Exception as xe:
            pass
        return

    def create_obj_attrs_message(obj: object, attrs: str) -> Iterable[str]:
        """
        формирование сообщения для всех атрибутов объекта
        """
        # yield '\n{}'.format(obj)
        n = obj.__name__
        ats = attrs.replace(' ', '').split(',')
        for atr in sorted(filter(bool, ats)):
            result = getattr(obj, atr)
            if callable(result):
                result = result()

            s = '{}.{} = {}'.format(n, atr, result).translate(replace_dt)
            yield s
            continue
        return

    def get_messages() -> Iterable[str]:
        """
        все сообщения для вывода
        """
        for ob, at in attrs_from_all_objs():
            yield from create_obj_attrs_message(ob, at)
            continue
        try:
            import psutil
            s = 'psutil.disk_usage = {}'.format(psutil.disk_usage('/'))
            yield s
        except Exception as xe:
            pass
        return

    m = get_messages()
    yield from m
    return


def _separator(msg: Tuple[str], max_len: int) -> Iterable[str]:
    """
    выравнивание пробелами для сообщения в рамки
    """
    for i in range(len(msg)):
        lm = len(msg[i])
        if lm < max_len:
            m = (msg[i] + (' ' * (max_len - lm)))
        else:
            m = msg[i]
        yield m
        continue
    return


def str_separator(message: str, s_width='#', s_height='#', t='  ', max_=70, n=5) -> str:
    """
    сообщение в рамке
    """

    def len_split(_m: List[str]) -> Iterable[str]:
        """
        макс длина строки по '\n'
        """
        for st in _m:
            if len(st) > max_:
                yield st[:max_]
                m = ((' ' * n) + st[max_:])
                yield from len_split([m])
            else:
                yield st
            continue
        return

    msg = tuple(len_split(message.split('\n')))
    ml = max(len(a) for a in msg)
    s = '{t}{0}%s{1}%s{0}'
    s1 = s % (s_width, s_width)
    s_ = s1.format(s_height, s_width * ml, t=t)
    m1 = s % (' ', ' ')
    m_ = '\n'.join(m1.format(s_height, m, t=t) for m in _separator(msg, ml))
    i = '{0}\n{1}\n{0}'.format(s_, m_)
    return i
