# -*- coding: UTF-8 -*-
# AllFiles, создание словарей файлов

import collections
import configparser
import os
import string
import time

import lr_lib
import lr_lib.core.etc.other
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_other
import lr_lib.core.var.vars_param
import lr_lib.etc.excepthook


def is_responce_file(name: str) -> (str, str):
    """вернуть файлы ответов, отбраковать "вероятно ненужные" файлы"""
    (n, ext) = os.path.splitext(name)
    if (name in lr_lib.core.var.vars_param.DENY_FILES) or (ext in lr_lib.core.var.vars_param.DENY_EXT) or any(
            (p in n) for p in
            lr_lib.core.var.vars_param.DENY_PART_NAME):
        return
    else:
        return n, ext


default = -1


def file_dict_creator(name: str, full_name: str, inf_num: int, enc: str, inf_key: str, deny: bool, stats: bool) -> dict:
    """создать словарь файла"""
    is_responce = is_responce_file(name)
    if not (deny or is_responce):
        return

    if is_responce is None:  # из lr_lib.gui.widj.responce_files
        (name_, _ext) = os.path.splitext(name)
    else:
        (name_, _ext) = is_responce

    file = dict(
        File=dict(
            Name=name,
            FullName=full_name,
            _ext=_ext,
            name_=name_,
            encoding=enc,
            len=default,
            NotPrintable=default,
            ascii_letters=default,
            digits=default,
            whitespace=default,
            punctuation=default,
            Size=default,
            Lines=default,
            timeCreate='',
        ),
        Snapshot=dict(
            Nums={inf_num},
            len=default,
            inf_key=inf_key
        ),
        Param=dict(
            Name='',
            Count=default,
            Count_indexs=[],
            Count_indexs_len=[],
            NotPrintable=default,
            len=default,
            inf_max=default,
            inf_min=default,
            max_action_inf=default,
            action_id=default,
        ),
    )

    if stats:
        set_file_statistic(file)
    return file


def get_inf_file_num(file: str) -> int:
    """если подходящий t*.inf, вернуть номер Snapshot"""
    (name, ext) = os.path.splitext(file)
    num = name[1:]
    if (ext == '.inf') and (name[0] == 't') and all(map(str.isnumeric, num)):
        return int(num)  # Snapshot > 0
    return


def get_folder_infs(folder: str) -> iter((str, int), ):
    """inf файлы/номера каталога"""
    for file in next(os.walk(folder))[2]:
        num = get_inf_file_num(file)
        if num:
            item = (file, num)
            yield item
        continue
    return


def create_files_from_infs(folder: str, enc: str, allow_deny: bool, statistic: bool) -> iter([dict, ]):
    """создать файлы ответов, из всех t*.ini файлов"""
    arg = (folder, enc, allow_deny, statistic,)
    chunks = ((arg, files) for files in
              lr_lib.core.etc.other.chunks(get_folder_infs(folder), lr_vars.FilesCreatePortionSize))
    executer = (lr_vars.M_POOL.imap_unordered if lr_vars.SetFilesPOOLEnable else map)

    # создать файлы ответов
    for chunk_files in executer(get_files_portions, chunks):
        for new_file in filter(bool, chunk_files):
            name = new_file['File']['Name']
            file = get_file_with_kwargs(lr_vars.AllFiles, Name=name)
            if file:  # файл уже есть, те пришел из другого inf
                nums = new_file['Snapshot']['Nums']
                file['Snapshot']['Nums'].update(nums)
            else:
                lr_vars.AllFiles.append(new_file)
            continue
        continue
    return


def get_files_portions(args: [(str, str, bool, bool), ((str, int),)]) -> [dict, ]:
    """создать файлы, для порции inf-файлов"""
    (arg, files) = args
    gn = ((arg, file) for file in files)
    files_gen = map(_create_files_from_inf, gn)
    files_ = tuple(file for portion in files_gen for file in portion)
    return files_


def _create_files_from_inf(args: [(str, str, bool, bool), (str, int)]) -> iter((dict,)):
    """создать файлы ответов, из одного inf-файла"""
    ((folder, enc, allow_deny, statistic), (file, num)) = args

    try:  # ConfigParser(вроде когдато были какието проблемы, с кодировкой?)
        config = configparser.ConfigParser()
        config.read(os.path.join(folder, file), encoding='utf-8')

        for sect in config.sections():
            for opt in config.options(sect):
                if any(map(opt.startswith, lr_lib.core.var.vars_param.FileOptionsStartswith)):
                    file_name = config[sect]

                    try:
                        file_name = file_name[opt]
                    except Exception as ex:
                        # InterpolationSyntaxError '%' must be followed by '%' or '(', found: '%20Federation.png',
                        print('ERROR!!! files.py', str([ex.__class__, ex, ex.args]))
                        continue

                    full_name = os.path.join(folder, file_name)
                    if os.path.isfile(full_name):
                        f = file_dict_creator(file_name, full_name, num, enc, opt, allow_deny, statistic)
                        if f:
                            f.update(config._sections)
                            yield f
                continue
            continue

    except Exception as ex:
        lr_lib.etc.excepthook.full_tb_write(ex)
        # как текст файл
        with open(os.path.join(folder, file), encoding='utf-8', errors='ignore') as inf_file:
            (num, *lines) = inf_file.read().split('\n')
            try:  # inf номер '[t75]' -> 75
                num = int(num[2:-1])
            except:
                num = -1

            for line in lines:  # создать файлы из ключей файла t75.inf
                if any(map(line.startswith, lr_lib.core.var.vars_param.FileOptionsStartswith)):
                    (key_from_inf, file_name) = line.split('=', 1)
                    full_name = os.path.join(folder, file_name)
                    if os.path.isfile(full_name):
                        f = file_dict_creator(file_name, full_name, num, enc, key_from_inf, allow_deny, statistic)
                        yield f
                continue
    return


# @lr_other.exec_time
def init() -> None:
    """создать все файлы ответов, для поиска в них param"""
    lr_vars.AllFiles.clear()
    folder = lr_vars.VarFilesFolder.get()
    lr_vars.Logger.info('Поиск файлов ответов в "{d}" ...'.format(d=folder))

    enc = lr_lib.core.var.vars_other.VarEncode.get()
    allow_deny = lr_vars.VarAllowDenyFiles.get()
    statistic = lr_vars.VarAllFilesStatistic.get()

    if lr_vars.VarIsSnapshotFiles.get():  # файлы ответов из LoadRunner inf
        create_files_from_infs(folder, enc, allow_deny, statistic)

    else:  # все файлы каталога
        for (e, name) in enumerate(os.listdir(folder)):
            full_name = os.path.join(folder, name)
            if os.path.isfile(full_name):
                new_file = file_dict_creator(name, full_name, 0, enc, '', allow_deny, statistic)
                file = get_file_with_kwargs(lr_vars.AllFiles, Name=new_file['File']['Name'])
                if file:  # файл уже есть, те пришел из другого inf
                    file['Snapshot']['Nums'].update(new_file['Snapshot']['Nums'])
                else:
                    lr_vars.AllFiles.append(new_file)
            continue

    if not lr_vars.AllFiles:
        lr_vars.Logger.critical('В "{f}" отсутствуют t*.inf LoadRunner файлы!\nнеобходимо, кнопкой Folder, '
                                'выбрать каталог lr_скрипт\\data'.format(f=folder))

    for file in lr_vars.AllFiles:
        fs = file['Snapshot']
        fs['Nums'] = sorted(fs['Nums'])  # set -> list
        fs['len'] = len(fs['Nums'])
        continue

    all_files_inf = tuple(lr_lib.core.etc.other.get_files_infs(lr_vars.AllFiles))
    lr_vars.VarSearchMaxSnapshot.set(max(all_files_inf or [-1]))
    lr_vars.VarSearchMinSnapshot.set(min(all_files_inf or [-1]))

    try:  # сортировка файлов
        lr_vars.AllFiles = sorted(lr_vars.AllFiles, key=lr_lib.core.etc.other.sort_files)
    except TypeError:  # если VarFileSortKey2 предназначен только для FilesWithParam
        lr_vars.AllFiles = sorted(lr_vars.AllFiles, key=lambda file: file['Snapshot']['Nums'])

    if statistic:
        lr_vars.Logger.info(lr_lib.core.etc.other.all_files_info())
    else:
        lr_vars.Tk.after(500, lambda: thread_set_stat(lr_vars.AllFiles))
    return


def get_file_with_kwargs(files: (dict,), **kwargs) -> dict:
    """вернуть первый файл, содержащий kwargs"""
    if not kwargs:
        kwargs = dict(Name=lr_vars.VarFileName.get())
    for file in get_files_with_kwargs(files, **kwargs):
        return file
    return


def get_files_with_kwargs(files: (dict,), key='File', **kwargs) -> iter((dict,)):
    """найти файлы, содержащие kwargs"""
    for file in files:
        f = file[key]
        try:
            if all((kwargs[k] == f[k]) for k in kwargs):
                yield file
        except Exception as ex:
            pass
        continue
    return


def set_file_statistic(file: dict, as_text=False, errors='replace') -> dict:
    """создание ключей статистики по файлу"""
    ff = file['File']
    full_name = ff['FullName']
    ff['Size'] = os.path.getsize(full_name)
    ff['timeCreate'] = time.strftime('%H:%M:%S %m.%d.%y', time.gmtime(os.path.getmtime(full_name)))

    if as_text:  # есть текст файла
        _set_fileFile_stats(ff, lr_vars.VarFileText.get())
    else:  # новый файл
        with open(full_name, encoding=ff['encoding'], errors=errors) as f:
            _set_fileFile_stats(ff, f.read())

    return file


def _set_fileFile_stats(fileFile: dict, text: str, let=0, wts=0, ptn=0, dts=0, na=0) -> None:
    """file['File'] статистика"""
    counter = collections.Counter(text)  # Counter({' ': 12, 'T': 2, 'a': 2, '<': 1, '/': 1, ...
    for key in counter:
        if key in string.ascii_letters:
            let += counter[key]
        elif key in string.whitespace:
            wts += counter[key]
        elif key in string.punctuation:
            ptn += counter[key]
        elif key in string.digits:
            dts += counter[key]
        else:
            na += counter[key]
        continue

    fileFile['ascii_letters'] = let
    fileFile['whitespace'] = wts
    fileFile['punctuation'] = ptn
    fileFile['digits'] = dts
    fileFile['NotPrintable'] = na
    fileFile['len'] = (ptn + wts + let + dts + na)
    fileFile['Lines'] = (counter.get('\n', 0) + 1)
    return


@lr_lib.core.var.vars_other.T_POOL_decorator
def thread_set_stat(files: [dict, ]) -> None:
    """создавать статистику в фоне, для всех файлов"""
    for file in files:
        set_file_statistic(file)
        continue

    lr_vars.Logger.info(lr_lib.core.etc.other.all_files_info())
    return
