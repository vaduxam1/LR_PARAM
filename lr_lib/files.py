# -*- coding: UTF-8 -*-
# AllFiles, создание словарей файлов

import os
import time
import string
import itertools
import contextlib
import configparser

from lr_lib import (
    defaults,
    other as lr_other,
    logger as lr_log,
)


def file_dict_creator(name: str, full_name: str, inf_num: int, enc: str, inf_key: str, allow_deny: bool, set_statistic: bool, dn=-1) -> dict:
    '''создать словарь файла'''
    file = get_file_with_kwargs(defaults.AllFiles, Name=name) if inf_num else None
    if file:  # файл уже есть, те пришел из другого inf
        file['Inf']['Nums'].add(inf_num)
    else:  # новый файл
        n, e = os.path.splitext(name)
        if allow_deny or not ((name in defaults.DENY_FILES) or (e in defaults.DENY_EXT) or any(p in n for p in defaults.DENY_PART_NAMES)):
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
                Inf=dict(
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
    executer = (defaults.M_POOL.imap_unordered if defaults.SetFilesPOOLEnable else map)
    folder_files = next(os.walk(folder))
    folder_files = folder_files[2]
    arg = (folder, enc, allow_deny, statistic, )
    args = ((arg, files) for files in lr_other.chunks(folder_files, defaults.FilesCreatePortionSize))
    yield from filter(bool, itertools.chain(*executer(get_files_portions, args)))


def get_files_portions(args: [(str, str, bool, bool), (str, )]) -> [dict, ]:
    '''создать файлы, для порции inf-файлов'''
    (arg, files) = args
    files = list(itertools.chain(*map(create_files_from_inf, ((arg, file) for file in files))))
    return files


def create_files_from_inf(args: [(str, str, bool, bool), str]) -> iter((dict, )):
    '''создать файлы, из inf-файла'''
    ((folder, enc, allow_deny, statistic), file) = args
    (name, ext) = os.path.splitext(file)
    defaults.VarAllSnapshotConfig.clear()

    n = name[1:]
    if (ext == '.inf') and (name[0] == 't') and all(map(str.isnumeric, n)):
        try:
            config = configparser.ConfigParser()
            config.read(os.path.join(folder, file), encoding='utf-8')

            num = int(n)
            defaults.VarAllSnapshotConfig[num] = config

            for sect in config.sections():
                for opt in config.options(sect):
                    if any(map(opt.startswith, defaults.FileOptionsStartswith)):
                        file_name = config[sect][opt]
                        full_name = os.path.join(folder, file_name)
                        if os.path.isfile(full_name):
                            file = file_dict_creator(file_name, full_name, num, enc, opt, allow_deny, statistic)
                            yield file

        except Exception as ex:
            lr_log.excepthook(ex)

            with open(os.path.join(folder, file), encoding='utf-8', errors='ignore') as inf_file:
                num, *lines = inf_file.read().split('\n')
                try:  # inf номер '[t75]' -> 75
                    num = int(num[2:-1])
                except: num = -1
                defaults.VarAllSnapshotConfig[num] = {}

                for line in lines:  # создать файлы из ключей файла t75.inf
                    if any(map(line.startswith, defaults.FileOptionsStartswith)):
                        key_from_inf, file_name = line.split('=', 1)
                        full_name = os.path.join(folder, file_name)
                        if os.path.isfile(full_name):
                            file = file_dict_creator(file_name, full_name, num, enc, key_from_inf, allow_deny, statistic)
                            yield file


# @lr_log.exec_time
def createAllFiles() -> None:
    '''создать все файлы для поиска param'''
    defaults.AllFiles.clear()
    folder = defaults.VarFilesFolder.get()
    defaults.Logger.info('обработка файлов из [ {d} ] ...'.format(d=folder))
    enc = defaults.VarEncode.get()
    allow_deny = defaults.VarAllowDenyFiles.get()
    statistic = defaults.VarAllFilesStatistic.get()

    if defaults.VarIsInfFiles.get():    # файлы ответов  из LoadRunner inf
        defaults.AllFiles = lr_other.iter_to_list(create_files_from_infs(folder, enc, allow_deny, statistic))
    else:  # все файлы каталога
        for e, name in enumerate(os.listdir(folder)):
            full_name = os.path.join(folder, name)
            if os.path.isfile(full_name):
                file = file_dict_creator(name, full_name, 0, enc, '', allow_deny, statistic)
                if file:
                    defaults.AllFiles.append(file)

    if not defaults.AllFiles:
        defaults.Logger.critical('В "{}" отсутствуют t*.inf LoadRunner файлы!\nнеобходимо выбрать каталог " lr_скрипт\\data "\nлибо сменить директорию кнопкой "Folder"'.format(folder))

    for file in defaults.AllFiles:  # Inf_Nums: set -> list
        file['Inf']['Nums'] = sorted(file['Inf']['Nums'])
        file['Inf']['len'] = len(file['Inf']['Nums'])

    all_files_inf = tuple(lr_other.get_files_infs(defaults.AllFiles))
    defaults.VarSearchMaxInf.set(max(all_files_inf or [-1]))
    defaults.VarSearchMinInf.set(min(all_files_inf or [-1]))

    try:  # сортировка файлов
        defaults.AllFiles = sorted(defaults.AllFiles, key=lr_other.sort_by_file_keys)
    except TypeError:  # если VarFileSortKey2 предназначен только для FilesWithParam
        defaults.AllFiles = sorted(defaults.AllFiles, key=lambda file: file['Inf']['Nums'])

    defaults.VarFileSortKey1.set(defaults.VarFileSortKey1.get())
    defaults.Logger.info(lr_other.all_files_info())


def get_file_with_kwargs(files: (dict,), **kwargs) -> dict:
    '''вернуть первый файл, содержащий kwargs'''
    if not kwargs:
        kwargs = dict(Name=defaults.VarFileName.get())
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
        _set_fileFile_stats(ff, defaults.VarFileText.get().split('\n'))
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
