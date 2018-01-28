﻿# -*- coding: UTF-8 -*-
# всяко разно

import re
import os
import types
import string
import itertools
import contextlib
import sys
import time
import tempfile
import subprocess
import traceback
import functools

import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.help as lr_help



def _chunks(_list, chunk_size: int) -> iter([iter,]):
    """Yield successive n-sized chunks from l. - не работает с генераторами"""
    for i in range(0, len(_list), chunk_size):
        yield _list[i:i + chunk_size]


def chunks(iterable: iter, chunk_size: int) -> iter((iter,)):
    """iter-версия, работает с генераторами, Yield successive n-sized chunks from l."""
    if isinstance(iterable, types.GeneratorType):
        chunk_range = tuple(range(chunk_size - 1))
        for i in iterable:
            yield list(itertools.chain([i], _chunks_range(chunk_range, iterable)))
    else:
        yield from _chunks(iterable, chunk_size)


def _chunks_range(chunk_range: (int, ), iterable):
    with contextlib.suppress(StopIteration):
        for _ in chunk_range:
            yield next(iterable)


def numericalSort(value: str, numbers=re.compile(r'(\d+)')) -> list:
    '''корректная сортировка файлов с inf-номерами в имени'''
    value = _snapshot_file_name(value)
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def _snapshot_file_name(name: str) -> str:
    '''корректная сортировка snapshot файлов'''
    if name.startswith('snapshot') and '_' in name:
        nam, num = name.split('_', 1)
        return 't{num}_{nam}'.format(num=num, nam=nam)
    return name


def sort_by_file_keys(file: dict):
    '''сортировка файлов, по ключам'''
    val = file.get(lr_vars.VarFileSortKey1.get())
    if val:
        k2 = lr_vars.VarFileSortKey2.get()
        if k2 in val:
            value = val[k2]
            if isinstance(value, str):
                value = numericalSort(value)
            return value


def file_string(file=None, deny=()) -> str:
    '''инфо о файле, во всплывающей подсказке'''
    if file is None:
        file = lr_vars.VarFile.get()
    if not file:
        return 'None'

    items = tuple(sorted(file.items()))
    m = max(len(k) for v in file.values() for k in v.keys())
    st = '{:<%s}\t{}' % m
    lv = lambda v: '\n'.join(st.format(a, str(b)[:lr_vars.MaxFileStringWidth]) for (a, b) in sorted(v.items()) if a not in deny)
    s = ('\t[ {k} ] :\n{v}'.format(k=k, v=lv(v)) for (k, v) in items)
    return '\n'.join(s)


def not_printable(s: str, printable=set(string.printable).__contains__) -> int:
    '''кол-во непечатных символов строки'''
    return len(s) - len(tuple(filter(printable, s)))


def all_files_info() -> str:
    '''статистическое инфо о всех найденых файлах'''
    lf = len(lr_vars.AllFiles)
    sa = sum(f['File'].get('Size', 0) for f in lr_vars.AllFiles)
    mn = min([f['File'].get('Size', 0) for f in lr_vars.AllFiles] or [0])
    mx = max([f['File'].get('Size', 0) for f in lr_vars.AllFiles] or [0])
    s = 'в {i} inf, найдено {f} файлов.\n symbols_count  : '.format(f=lf, i=len(list(get_files_infs(lr_vars.AllFiles))))
    sum_keys = ['Size', 'len', 'NotPrintable', 'Lines', 'ascii_letters', 'digits', 'whitespace', 'punctuation']
    _r = [(k, sum(f['File'].get(k, 0) for f in lr_vars.AllFiles)) for k in sum_keys]
    try: sl = _r[-1][1] / lf
    except ZeroDivisionError: sl = 0
    r = ' '.join('{}({})'.format(*a) for a in sorted(_r, key=lambda b: b[1], reverse=True))
    return '{s}{r}\n file_size byte : all({sa}) min({mn}) several({sl}) max({mx})\n{sep}'.format(
        s=s, r=r, mn=mn, mx=mx, sl=sl, sa=sa, sep=lr_vars.PRINT_SEPARATOR)


def param_files_info() -> str:
    '''инфо о param файлах'''
    res = [(str(f['Param']['Count']), f['File']['Name'], str(f['Snapshot']['Nums'])) for f in lr_vars.FilesWithParam]
    m = max(len(n) for r in res for n in r)
    if m > 25: m = 25
    elif m < 10: m = 10
    s = '{:<%s} | {:<%s} | {:<%s}' % (m, m, m)

    i = '\n'.join(map(str, chunks(tuple(get_files_infs(lr_vars.FilesWithParam)), 15)))
    r = '\n\tparam -> "{p}" :\n{sep}\n{t}\n{res}\n{sep}\nSnapshots\n{i}\n{sep}'.format(
        sep=lr_vars.PRINT_SEPARATOR, t=s.format('ParamCount', 'FileName', 'Snapshots'), p=lr_vars.VarParam.get(),
        res='\n'.join(s.format(*r) for r in res), i=i)
    return r


def get_files_infs(files: [dict, ]) -> iter({int, }):
    '''inf-номера файлов'''
    yield from sorted(set(n for file in files for n in file['Snapshot']['Nums']))


def only_ascii_symbols(item: (str, ), allow=set(string.printable).__contains__) -> iter:
    for s in item:
        if allow(s):
            yield s
        else:
            break


def keyboard_listener() -> None:
    '''перехват keyboard-hotkey'''
    try:
        import keyboard
    except ImportError:
        lr_vars.Logger.info('ImportError keyboard [{}] не работает !\nНеобходимо установить библиотеку keyboard из cmd:\n'
                            'cd c:\Python36\Scripts\ \npip install keyboard'.format(lr_vars.FIND_PARAM_HOTKEY))
    else:
        def get_param_hotkey() -> None:
            '''найти {param} из clipboard, по хоткей'''
            param = lr_vars.Tk.clipboard_get()
            lr_vars.Window.get_files(param=param)

        keyboard.add_hotkey(lr_vars.FIND_PARAM_HOTKEY, get_param_hotkey)


def iter_to_list(item: iter) -> list:
    '''прирвести iter к list'''
    if isinstance(item, (list, tuple)):
        return item
    else:
        return list(item)


def check_bound_lb_rb(left: 'id="', right: '",') -> bool:
    '''id="zkau_11",'''
    return check_bound_rb(right) and check_bound_lb(left)


def check_bound_rb(right: '",', rb_allow=lr_vars.allow_symbols.__contains__) -> bool:
    '''id="zkau_11",'''
    return right and rb_allow(right[0])


def check_bound_lb(left: 'id="', lb_allow=lr_vars.allow_symbols.__contains__) -> bool:
    '''id="zkau_11",'''
    return left and lb_allow(left[-1]) or check_lb_percent(left) or check_lb_tnrvf(left)


def check_lb_percent(left: '%22', lb_allow=lr_help.HEX.__contains__) -> bool:
    '''%22zkau_11",'''
    return (len(left) > 2) and lb_allow(left[-3:])


def check_lb_tnrvf(left: '\\r\\n', lb_allow=lr_vars.tnrvf.__contains__) -> bool:
    '''\\r\\nzkau_11", - "\n" как два символа'''
    return (len(left) > 1) and lb_allow(left[-2:])


def openTextInEditor(text: str) -> None:
    '''открытие сообщения в Блокноте'''
    with tempfile.NamedTemporaryFile(delete=False) as f:
        with open(f.name, 'w', errors='replace') as tf:
            tf.write(text)
        subprocess.Popen([lr_vars.EDITOR['exe'], f.name])
        f.close()


def excepthook(*args) -> None:
    """обработка raise: сокращенный стектрейс + исходный код"""
    len_args = len(args)
    if len_args == 1:
        exc_type, exc_val, exc_tb = type(args[0]), args[0], args[0].__traceback__
    elif len_args == 3:
        exc_type, exc_val, exc_tb = args
    else:
        exc_type, exc_val, exc_tb = sys.exc_info()

    full_tb_write(exc_type, exc_val, exc_tb)

    ern = exc_type.__name__
    if lr_vars.Window:
        lr_vars.Window.err_to_widgts(exc_type, exc_val, exc_tb, ern)
    lr_vars.Logger.critical(get_tb(exc_type, exc_val, exc_tb, ern))


def full_tb_write(exc_type, exc_val, exc_tb) -> None:
    '''логировать полный traceback'''
    traceback.print_tb(exc_tb)  # в консоль
    # в лог
    with open(lr_vars.logFullName, 'a') as log:
        log.write('\n{0}\n\t>>> traceback.print_tb\n{0}\n'.format(lr_vars.PRINT_SEPARATOR))
        traceback.print_tb(exc_tb, file=log)
        log.write('{t}\n{v}'.format(t=exc_type, v=exc_val))
        log.write('\n{0}\n\t<<< traceback.print_tb\n{0}\n'.format(lr_vars.PRINT_SEPARATOR))


def get_tb(exc_type, exc_val, exc_tb, err_name: str) -> str:
    '''traceback + исходный код'''
    if not exc_tb:
        return '{} {} {}'.format(exc_type, exc_val, exc_tb)
    exc_lines = traceback.format_exception(exc_type, exc_val, exc_tb)

    def get_code(lib='\{}\\'.format(lr_vars.lib_folder)) -> str:
        '''исходный код'''
        line = ''
        for line in reversed(exc_lines):
            if lib in line:
                break
        try:
            fileName = line.split('"')[1]
            lineNum = int(line.split(',')[1].split('line')[-1])
            with open(fileName, errors='replace', encoding='utf-8') as file:
                text = file.read().split('\n')

            left = []
            for line in reversed(text[:lineNum]):
                if line.strip():
                    left.append(line)
                    if len(left) == lr_vars.EHOME:
                        break
            _, f = os.path.split(fileName)
            left[0] = '\n!!! {e} [ {f} : строка {l} ]\n{line}\n'.format(e=err_name, line=left[0], f=f, l=lineNum)
            left.reverse()

            right = []
            for line in text[lineNum:]:
                if line.strip():
                    right.append(line)
                    if len(right) == lr_vars.EEND:
                        break

            code = '{l}\n{r}'.format(l='\n'.join(left), r='\n'.join(right))
            return code
        except Exception as ex:
            return 'неудалось загрузить код файла\n{}'.format(ex)

    tb = ''.join(exc_lines[-1:]).rstrip()
    code = get_code().rstrip()
    return '{tb}\n{s}\n{code}'.format(tb=tb, code=code, s=lr_vars.PRINT_SEPARATOR)


def exec_time(func: callable) -> callable:
    '''время выполнения func'''
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        t = time.time()
        lr_vars.Logger.trace('-> {f}'.format(f=func))
        out = func(*args, **kwargs)
        t = time.time() - t
        lr_vars.Logger.trace('<- {t} сек: {f}'.format(f=func, t=round(t, 1)))
        return out
    return wrap
