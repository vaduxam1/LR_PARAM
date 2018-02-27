# -*- coding: UTF-8 -*-
# инфо о системе

import sys
import contextlib


def system_info() -> str:
    return str_separator('\n'.join(_system_info()).lstrip('\n'))


def _system_info() -> (str, ):
    """всякая ненужная инфа(при старте скрипта)"""
    replace_dt = {ord(s): '' for s in "(')"}

    def attrs_from_all_objs() -> (object, 'attrs',):
        """объект_источник_инфы, "атрибуты, " """
        yield sys, 'dont_write_bytecode, executable, getdefaultencoding, ' \
                   'getfilesystemencoding, getwindowsversion, implementation, platform, exc_info, '
        import platform
        yield platform, '_sys_version, architecture, uname, win32_ver, '
        with contextlib.suppress(Exception):
            import psutil
            yield psutil, 'cpu_count, virtual_memory, users, '

    def create_obj_attrs_message(obj: object, attrs: str):
        """формирование сообщения для всех атрибутов объекта"""
        # yield '\n{}'.format(obj)
        n = obj.__name__
        for atr in sorted(filter(bool, attrs.replace(' ', '').split(','))):
            result = getattr(obj, atr)
            if callable(result):
                result = result()

            yield '{}.{} = {}'.format(n, atr, result).translate(replace_dt)

    def get_messages():
        """все сообщения для вывода"""
        for ob, at in attrs_from_all_objs():
            yield from create_obj_attrs_message(ob, at)
        with contextlib.suppress(Exception):
            import psutil
            yield 'psutil.disk_usage = {}'.format(psutil.disk_usage('/'))

    yield from get_messages()


def _separator(msg: (str, ), max_len: int) -> (str, ):
    """выравнивание пробелами для сообщения в рамки"""
    for i in range(len(msg)):
        l = len(msg[i])
        if l < max_len:
            yield msg[i] + ' ' * (max_len-l)
        else:
            yield msg[i]


def str_separator(message: str, s_width='#', s_height='#', t='  ', max_=70, n=5) -> str:
    """сообщение в рамке"""
    def len_split(_m: [str, ]):  # макс длина строки по '\n'
        for st in _m:
            if len(st) > max_:
                yield st[:max_]
                yield from len_split([' ' * n + st[max_:]])
            else: yield st

    msg = tuple(len_split(message.split('\n')))
    ml = max(len(a) for a in msg)
    s = '{t}{0}%s{1}%s{0}'
    s1 = s % (s_width, s_width)
    s_ = s1.format(s_height, s_width * ml, t=t)
    m1 = s % (' ', ' ')
    m_ = '\n'.join(m1.format(s_height, m, t=t) for m in _separator(msg, ml))
    return '{0}\n{1}\n{0}'.format(s_, m_)
