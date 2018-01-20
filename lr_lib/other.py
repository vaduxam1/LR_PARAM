# -*- coding: UTF-8 -*-
# всяко разно

import re
import types
import string
import argparse
import itertools
import contextlib


from lr_lib import (
    defaults,
    help as lr_help,
    logger as lr_log,
)


def argument_parser() -> dict:
    ''''аргументы из консоли'''
    p = argparse.ArgumentParser()
    p.add_argument('param', nargs='?', help='параметр из LoadRunner')
    p.add_argument('-last', '--last_file', help='выбрать последний, из найденных файлов, иначе первый', type=int)
    p.add_argument('-min', '--min_inf', help='ограничение(для поиска param) минимального номера inf', type=int)
    p.add_argument('-max', '--max_inf', help='ограничение(для поиска param) максимального номера inf', type=int)
    p.add_argument('-n', '--notepad', help='открыть результат в notepad', type=int, default=1)
    p.add_argument('-e', '--encoding', help='кодировка', type=str)
    p.add_argument('-names', '--file_names', help='показывать имена найденных файлов', type=int, default=0)
    p.add_argument('-s', '--statistic', help='формировать статистику для найденных файлов', type=int, default=0)
    args_dict = {k: v for k, v in p.parse_args().__dict__.items() if not k.startswith('_') if v is not None}

    if 'last_file' in args_dict:
        defaults.VarFirstLastFile.set(args_dict['last_file'])
    if 'min_inf' in args_dict:
        defaults.VarSearchMinInf.set(args_dict['min_inf'])
    if 'max_inf' in args_dict:
        defaults.VarSearchMaxInf.set(args_dict['max_inf'])
    if 'encoding' in args_dict:
        defaults.VarEncode.set(args_dict['encoding'])
    defaults.VarFileNamesNumsShow.set(args_dict['file_names'])
    defaults.VarAllFilesStatistic.set(args_dict['statistic'])

    return args_dict


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
    val = file.get(defaults.VarFileSortKey1.get())
    if val:
        k2 = defaults.VarFileSortKey2.get()
        if k2 in val:
            value = val[k2]
            if isinstance(value, str):
                value = numericalSort(value)
            return value


def file_string(file=None, deny=()) -> str:
    '''инфо о файле, во всплывающей подсказке'''
    if file is None:
        file = defaults.VarFile.get()
    if not file:
        return 'None'

    items = tuple(sorted(file.items()))
    m = max(len(k) for v in file.values() for k in v.keys())
    st = '{:<%s}\t{}' % m
    s = ('\t[ {k} ] :\n{v}'.format(k=k, v='\n'.join(
        st.format(a, str(b)[:defaults.MaxFileStringWidth]) for a, b in sorted(v.items()) if a not in deny))
         for k, v in items)

    return '\n'.join(s)


def not_printable(s: str, printable=set(string.printable).__contains__) -> int:
    '''кол-во непечатных символов строки'''
    return len(s) - len(tuple(filter(printable, s)))


def all_files_info() -> str:
    '''статистическое инфо о всех найденых файлах'''
    lf = len(defaults.AllFiles)
    sa = sum(f['File'].get('Size', 0) for f in defaults.AllFiles)
    mn = min([f['File'].get('Size', 0) for f in defaults.AllFiles] or [0])
    mx = max([f['File'].get('Size', 0) for f in defaults.AllFiles] or [0])
    s = 'в {i} inf, найдено {f} файлов.\n symbols_count  : '.format(
        f=lf, i=len(list(get_files_infs(defaults.AllFiles))))
    sum_keys = ['Size', 'len', 'NotPrintable', 'Lines', 'ascii_letters', 'digits', 'whitespace', 'punctuation']
    _r = [(k, sum(f['File'].get(k, 0) for f in defaults.AllFiles)) for k in sum_keys]
    try: sl = _r[-1][1] / lf
    except ZeroDivisionError: sl = 0
    r = ' '.join('{}({})'.format(*a) for a in sorted(_r, key=lambda b: b[1], reverse=True))
    return '{s}{r}\n file_size byte : all({sa}) min({mn}) several({sl}) max({mx})\n{sep}'.format(
        s=s, r=r, mn=mn, mx=mx, sl=sl, sa=sa, sep=defaults.PRINT_SEPARATOR)


def param_files_info() -> str:
    '''инфо о param файлах'''
    res = [(str(f['Param']['Count']), f['File']['Name'], str(f['Inf']['Nums'])) for f in defaults.FilesWithParam]
    m = max(len(n) for r in res for n in r)
    if m > 25: m = 25
    elif m < 10: m = 10
    s = '{:<%s} | {:<%s} | {:<%s}' % (m, m, m)

    i = '\n'.join(map(str, chunks(tuple(get_files_infs(defaults.FilesWithParam)), 15)))
    r = '\n\tparam -> "{p}" :\n{sep}\n{t}\n{res}\n{sep}\nInfs\n{i}\n{sep}'.format(
        sep=defaults.PRINT_SEPARATOR, t=s.format('ParamCount', 'FileName', 'Snapshots'), p=defaults.VarParam.get(),
        res='\n'.join(s.format(*r) for r in res), i=i)
    return r


def get_files_infs(files: [dict, ]) -> iter({int, }):
    '''inf-номера файлов'''
    yield from sorted(set(n for file in files for n in file['Inf']['Nums']))


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
        lr_log.Logger.info(
            'ImportError keyboard [{}] не работает !\nНеобходимо установить библиотеку keyboard из cmd:\n'
            'cd c:\Python36\Scripts\ \npip install keyboard'.format(defaults.FIND_PARAM_HOTKEY))
    else:
        def get_param_hotkey() -> None:
            '''найти {param} из clipboard, по хоткей'''
            param = defaults.Tk.clipboard_get()
            defaults.Window.get_files(param=param)
        keyboard.add_hotkey(defaults.FIND_PARAM_HOTKEY, get_param_hotkey)


def iter_to_list(item: iter) -> list:
    '''прирвести iter к list'''
    if isinstance(item, (list, tuple)):
        return item
    else:
        return list(item)


def check_bound_lb_rb(left: 'id="', right: '",') -> bool:
    '''id="zkau_11",'''
    return check_bound_rb(right) and check_bound_lb(left)


def check_bound_rb(right: '",', rb_allow=defaults.allow_symbols.__contains__) -> bool:
    '''id="zkau_11",'''
    return right and rb_allow(right[0])


def check_bound_lb(left: 'id="', lb_allow=defaults.allow_symbols.__contains__) -> bool:
    '''id="zkau_11",'''
    return left and lb_allow(left[-1]) or check_lb_percent(left) or check_lb_tnrvf(left)


def check_lb_percent(left: '%22', lb_allow=lr_help.HEX.__contains__) -> bool:
    '''%22zkau_11",'''
    return (len(left) > 2) and lb_allow(left[-3:])


def check_lb_tnrvf(left: '\\r\\n', lb_allow=defaults.tnrvf.__contains__) -> bool:
    '''\\r\\nzkau_11", - "\n" как два символа'''
    return (len(left) > 1) and lb_allow(left[-2:])