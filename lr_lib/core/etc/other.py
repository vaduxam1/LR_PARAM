﻿# -*- coding: UTF-8 -*-
# всяко разно

import functools
import itertools
import json
import os
import re
import string
import subprocess
import tempfile
import time
import types

import lr_lib.core.var.vars as lr_vars


def _chunks(iterable: list, chunk_size: int) -> iter([iter, ]):
    """Yield successive n-sized chunks from l. - не работает с генераторами"""
    for i in range(0, len(iterable), chunk_size):
        val = iterable[i:(i + chunk_size)]
        yield val
        continue
    return


def chunks(iterable: iter, chunk_size: int) -> iter((iter,)):
    """iter-версия, работает с генераторами, Yield successive n-sized chunks from l."""
    if isinstance(iterable, types.GeneratorType):
        chunk_range = range(chunk_size - 1)
        for i in iterable:
            val = tuple(itertools.chain([i], _chunks_range(chunk_range, iterable)))
            yield val
            continue
    else:
        yield from _chunks(iterable, chunk_size)
    return


def _chunks_range(chunk_range: (int,), iterable):
    try:
        for _ in chunk_range:
            yield next(iterable)
            continue
    except Exception as ex:
        pass
    return


def numericalSort(value: str, numbers=re.compile(r'(\d+)')) -> list:
    """корректная сортировка файлов с inf-номерами в имени"""
    value = _snapshot_file_name(value)
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def _snapshot_file_name(name: str) -> str:
    """корректная сортировка snapshot файлов"""
    if name.startswith('snapshot') and '_' in name:
        (nam, num) = name.split('_', 1)
        return 't{num}_{nam}'.format(num=num, nam=nam)
    return name


def sort_files(file: dict):
    """сортировка файлов, по ключам"""
    val = file.get(lr_vars.VarFileSortKey1.get())
    if val:
        k2 = lr_vars.VarFileSortKey2.get()
        if k2 in val:
            value = val[k2]
            if isinstance(value, str):
                value = numericalSort(value)
            return value
    return


def file_string(file=None, deny=(), min_width=25, max_width=50) -> str:
    """инфо о файле, во всплывающей подсказке"""
    if file is None:
        file = lr_vars.VarFile.get()
    if not file:
        return 'None'

    len_all = [len(k) for v in file.values() for k in v.keys()]
    width = (sum(len_all) // len(len_all))
    if width > max_width:
        width = max_width
    elif width < min_width:
        width = min_width

    st = '{:<%s}\t{}' % width
    _st = '{} {}'
    sep = lambda a: (st if (len(a) < width) else _st)

    vmax = lambda b, mx=lr_vars.MaxFileStringWidth: ('{} ...'.format(b[:mx]) if (len(b) > mx) else b)
    val = lambda dt: '\n'.join(sep(a).format('{}:'.format(a), vmax(str(dt[a]))) for a in sorted(dt) if (a not in deny))

    s = '\n'.join('\t[ {k} ] :\n{v}'.format(k=k, v=val(file[k])) for k in sorted(file))
    return s


def not_printable(s: str, printable=set(string.printable).__contains__) -> int:
    """кол-во непечатных символов строки"""
    ls = (len(s) - len(tuple(filter(printable, s))))
    return ls


def all_files_info() -> str:
    """статистическое инфо о всех найденых файлах"""
    lf = len(lr_vars.AllFiles)
    sa = sum(f['File'].get('Size', 0) for f in lr_vars.AllFiles)
    mn = min([f['File'].get('Size', 0) for f in lr_vars.AllFiles] or [0])
    mx = max([f['File'].get('Size', 0) for f in lr_vars.AllFiles] or [0])

    st_ = 'В {i} inf, найдено {f} файлов ответов.\nСтатистика файлов ответов: '.format(
        f=lf, i=len(list(get_files_infs(lr_vars.AllFiles))))

    sum_keys = ['len', 'NotPrintable', 'Lines', 'ascii_letters', 'digits', 'whitespace', 'punctuation']
    _r = [(k, sum(f['File'].get(k, 0) for f in lr_vars.AllFiles)) for k in sum_keys]
    try:
        sl = (_r[-1][1] / lf)
    except ZeroDivisionError:
        sl = 0

    r = '\n\t'.join('{} = {} симв.'.format(*a) for a in sorted(_r, key=lambda b: b[1], reverse=True))
    r = ('\n\t' + r)
    txt = '{s}{r}\n\t' \
          'всего = {sa} byte\n\t' \
          '(мин/сред/макс) = ({mn}/{sl}/{mx} ) byte'.format(s=st_, r=r, mn=mn, mx=mx, sl=round(sl, 3), sa=sa)

    return txt


def param_files_info() -> str:
    """инфо о param файлах"""
    res = [(str(f['Snapshot']['Nums']), f['File']['Name'], str(f['Param']['Count'])) for f in lr_vars.FilesWithParam]
    m = max(len(n) for r in res for n in r)
    if m > 25:
        m = 25
    elif m < 10:
        m = 10
    s = ('{:<%s} | {:<%s} | {:<%s}' % (m, m, m))

    i = '\n'.join(map(str, chunks(tuple(get_files_infs(lr_vars.FilesWithParam)), 15)))
    r = '"{p}" Snapshots{i}:\n{sep}\n{t}\n{res}\n{sep}'.format(
        sep=lr_vars.PRINT_SEPARATOR, t=s.format('Snapshot', 'FileName', 'Кол-во вариантов WRSP'),
        p=lr_vars.VarParam.get(), res='\n'.join(s.format(*r) for r in res), i=i)
    return r


def get_files_infs(files: [dict, ]) -> iter({int, }):
    """inf-номера файлов"""
    yield from sorted(set(n for file in files for n in file['Snapshot']['Nums']))
    return


def only_ascii_symbols(item: (str,), allow=set(string.printable).__contains__) -> iter:
    for s in item:
        if allow(s):
            yield s
        else:
            break
        continue
    return


def iter_to_list(item: iter) -> list:
    """прирвести iter к list"""
    if isinstance(item, (list, tuple)):
        return item
    else:
        return list(item)


def _openTextInEditor(file: str):
    """открытие файл в Блокноте"""
    s = subprocess.Popen([lr_vars.EDITOR['exe'], file])
    return s


def openTextInEditor(text: str) -> None:
    """открытие сообщения в Блокноте"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        with open(f.name, 'w', errors='replace') as tf:
            tf.write(text)
        _openTextInEditor(f.name)
        f.close()
    return


def exec_time(func: callable) -> callable:
    """время выполнения func"""

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        t = time.time()
        lr_vars.Logger.trace('-> {f}'.format(f=func))
        out = func(*args, **kwargs)
        t = (time.time() - t)
        lr_vars.Logger.trace('<- {t} сек: {f}'.format(f=func, t=round(t, 1)))
        return out

    return wrap


def get_files_names(folder: str, i_num: int, file_key='File', file_mask='t{}.inf') -> iter((str,)):
    """все имена файлов из t{i_num}.inf"""
    inf_file = file_mask.format(i_num)
    fi = os.path.join(folder, inf_file)
    if not os.path.isfile(fi):
        return

    yield inf_file
    with open(fi) as inf:
        for line in inf:
            s_line = line.strip().split('=', 1)
            if len(s_line) == 2:
                (key, value) = s_line
                if (file_key in key) and (value != 'NONE'):
                    yield value
            continue
    return


def get_json(obj, indent=5):
    """удобно-смотримый вид"""
    try:
        j = json.dumps(obj, indent=indent, ensure_ascii=False)
    except Exception:
        return obj
    else:
        return j
