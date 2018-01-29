# -*- coding: UTF-8 -*-
# AllFiles, создание словарей файлов

import os
import time
import string
import itertools
import contextlib
import configparser

import lr_lib.core.etc.other as lr_other
import lr_lib.core.var.vars as lr_vars


def file_dict_creator(name: str, full_name: str, inf_num: int, enc: str, inf_key: str, allow_deny: bool, set_statistic: bool, dn=-1) -> dict:
    '''создать словарь файла'''
    file = get_file_with_kwargs(lr_vars.AllFiles, Name=name) if inf_num else None
    if file:  # файл уже есть, те пришел из другого inf
        file['Snapshot']['Nums'].add(inf_num)
    else:  # новый файл
        n, e = os.path.splitext(name)
        if allow_deny or not ((name in lr_vars.DENY_FILES) or (e in lr_vars.DENY_EXT) or any(p in n for p in lr_vars.DENY_PART_NAMES)):
            file = dict(
                File=dict(
                    Name=name,
                    FullName=full_name,
                    _ext=e,
                    name_=n,
                    encoding=enc,
                    len=dn,
                    NotPrintable=dn,
                    ascii_letters=dn,
                    digits=dn,
                    whitespace=dn,
                    punctuation=dn,
                    Size=dn,
                    Lines=dn,
                    timeCreate='',
                ),
                Snapshot=dict(
                    Nums={inf_num},
                    len=dn,
                    inf_key=inf_key
                ),
                Param=dict(
                    Name='',
                    Count=dn,
                    Count_indexs=[],
                    Count_indexs_len=[],
                    NotPrintable=dn,
                    len=dn,
                    inf_max=dn,
                    inf_min=dn,
                    max_action_inf=dn,
                    action_id=dn,
                ),
            )

            if set_statistic:
                set_file_statistic(file)

            return file


def create_files_from_infs(folder: str, enc: str, allow_deny: bool, statistic: bool) -> iter([dict, ]):
    '''создать файлы, из LoadRunner ini-файлов'''
    executer = (lr_vars.M_POOL.imap_unordered if lr_vars.SetFilesPOOLEnable else map)
    folder_files = next(os.walk(folder))
    folder_files = folder_files[2]

    arg = (folder, enc, allow_deny, statistic, )
    chunks = tuple(lr_other.chunks(folder_files, lr_vars.FilesCreatePortionSize))
    args = ((arg, files) for files in chunks)

    proc1 = 100 / len(chunks)
    for (e, files) in enumerate(executer(get_files_portions, args)):
        for file in files:
            if file:
                yield file

        lr_vars.Tk.title('создание файлов ответов: {p} % | {v}'.format(
            p=round(proc1 * e), f=len(lr_vars.AllFiles), v=lr_vars.VERSION))

def get_files_portions(args: [(str, str, bool, bool), (str, )]) -> [dict, ]:
    '''создать файлы, для порции inf-файлов'''
    (arg, files) = args
    files = list(itertools.chain(*map(create_files_from_inf, ((arg, file) for file in files))))
    return files


def create_files_from_inf(args: [(str, str, bool, bool), str]) -> iter((dict, )):
    '''создать файлы, из inf-файла'''
    ((folder, enc, allow_deny, statistic), file) = args
    (name, ext) = os.path.splitext(file)
    lr_vars.VarAllSnapshotConfig.clear()

    n = name[1:]
    if (ext == '.inf') and (name[0] == 't') and all(map(str.isnumeric, n)):
        try:
            config = configparser.ConfigParser()
            config.read(os.path.join(folder, file), encoding='utf-8')

            num = int(n)
            lr_vars.VarAllSnapshotConfig[num] = config

            for sect in config.sections():
                for opt in config.options(sect):
                    if any(map(opt.startswith, lr_vars.FileOptionsStartswith)):
                        file_name = config[sect][opt]
                        full_name = os.path.join(folder, file_name)
                        if os.path.isfile(full_name):
                            file = file_dict_creator(file_name, full_name, num, enc, opt, allow_deny, statistic)
                            yield file

        except Exception as ex:
            lr_other.excepthook(ex)

            with open(os.path.join(folder, file), encoding='utf-8', errors='ignore') as inf_file:
                num, *lines = inf_file.read().split('\n')
                try:  # inf номер '[t75]' -> 75
                    num = int(num[2:-1])
                except: num = -1
                lr_vars.VarAllSnapshotConfig[num] = {}

                for line in lines:  # создать файлы из ключей файла t75.inf
                    if any(map(line.startswith, lr_vars.FileOptionsStartswith)):
                        key_from_inf, file_name = line.split('=', 1)
                        full_name = os.path.join(folder, file_name)
                        if os.path.isfile(full_name):
                            file = file_dict_creator(file_name, full_name, num, enc, key_from_inf, allow_deny, statistic)
                            yield file


# @lr_other.exec_time
def init() -> None:
    '''создать все файлы ответов, для поиска в них param'''
    lr_vars.AllFiles.clear()
    folder = lr_vars.VarFilesFolder.get()
    lr_vars.Logger.info('обработка файлов из [ {d} ] ...'.format(d=folder))
    enc = lr_vars.VarEncode.get()
    allow_deny = lr_vars.VarAllowDenyFiles.get()
    statistic = lr_vars.VarAllFilesStatistic.get()

    if lr_vars.VarIsSnapshotFiles.get():    # файлы ответов  из LoadRunner inf
        lr_vars.AllFiles = lr_other.iter_to_list(create_files_from_infs(folder, enc, allow_deny, statistic))
    else:  # все файлы каталога
        for e, name in enumerate(os.listdir(folder)):
            full_name = os.path.join(folder, name)
            if os.path.isfile(full_name):
                file = file_dict_creator(name, full_name, 0, enc, '', allow_deny, statistic)
                if file:
                    lr_vars.AllFiles.append(file)

    if not lr_vars.AllFiles:
        lr_vars.Logger.critical('В "{}" отсутствуют t*.inf LoadRunner файлы!\nнеобходимо выбрать каталог " lr_скрипт\\data "\n'
                                'либо сменить директорию кнопкой "Folder"'.format(folder))

    for file in lr_vars.AllFiles:  # Snapshot_Nums: set -> list
        file['Snapshot']['Nums'] = sorted(file['Snapshot']['Nums'])
        file['Snapshot']['len'] = len(file['Snapshot']['Nums'])

    all_files_inf = tuple(lr_other.get_files_infs(lr_vars.AllFiles))
    lr_vars.VarSearchMaxSnapshot.set(max(all_files_inf or [-1]))
    lr_vars.VarSearchMinSnapshot.set(min(all_files_inf or [-1]))

    try:  # сортировка файлов
        lr_vars.AllFiles = sorted(lr_vars.AllFiles, key=lr_other.sort_by_file_keys)
    except TypeError:  # если VarFileSortKey2 предназначен только для FilesWithParam
        lr_vars.AllFiles = sorted(lr_vars.AllFiles, key=lambda file: file['Snapshot']['Nums'])

    lr_vars.VarFileSortKey1.set(lr_vars.VarFileSortKey1.get())
    lr_vars.Logger.info(lr_other.all_files_info())


def get_file_with_kwargs(files: (dict,), **kwargs) -> dict:
    '''вернуть первый файл, содержащий kwargs'''
    if not kwargs:
        kwargs = dict(Name=lr_vars.VarFileName.get())
    for file in get_files_with_kwargs(files, **kwargs):
        return file


def get_files_with_kwargs(files: (dict,), key='File', **kwargs) -> iter((dict,)):
    '''найти файлы, содержащие kwargs'''
    for file in files:
        f = file[key]
        with contextlib.suppress(KeyError):
            if all(kwargs[k] == f[k] for k in kwargs):
                yield file


def set_file_statistic(file: dict, as_text=False) -> dict:
    '''создание ключей статистики по файлу'''
    ff = file['File']
    ff['Size'] = os.path.getsize(ff['FullName'])
    ff['timeCreate'] = time.strftime('%H:%M:%S %m.%d.%y', time.gmtime(os.path.getmtime(ff['FullName'])))
    if as_text:  # есть текст файла
        _set_fileFile_stats(ff, lr_vars.VarFileText.get().split('\n'))
    else:  # новый файл
        with open(ff['FullName'], encoding=ff['encoding'], errors='replace') as iter_lines:
            _set_fileFile_stats(ff, iter_lines)
    return file


def _set_fileFile_stats(fileFile: dict, lines: (str,)) -> None:
    '''file['File'] статистика'''
    line_counter = punctuation = whitespace = ascii_letters = no_ascii = digits = 0
    for line_counter, line in enumerate(lines, start=1):
        for symbol in line:
            if symbols_letters(symbol):
                ascii_letters += 1
            elif symbols_whitespace(symbol):
                whitespace += 1
            elif symbols_punctuation(symbol):
                punctuation += 1
            elif symbols_digits(symbol):
                digits += 1
            else:
                no_ascii += 1

    fileFile['len'] = punctuation + whitespace + ascii_letters + digits + no_ascii
    fileFile['ascii_letters'] = ascii_letters
    fileFile['punctuation'] = punctuation
    fileFile['digits'] = digits
    fileFile['whitespace'] = whitespace
    fileFile['NotPrintable'] = no_ascii
    fileFile['Lines'] = line_counter


symbols_punctuation = set(string.punctuation).__contains__
symbols_digits = set(string.digits).__contains__
symbols_letters = set(string.ascii_letters).__contains__
symbols_whitespace = set(string.whitespace).__contains__
