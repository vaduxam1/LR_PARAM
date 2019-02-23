# -*- coding: UTF-8 -*-
# старт core

import argparse
from typing import Iterable, Tuple, List, Callable, Any, Dict

import lr_lib
import lr_lib.core.var.etc.init_vars
import lr_lib.core.var.etc.vars_other
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_param


def init(as_console: bool) -> dict:
    """
    стартовать core
    """
    lr_lib.core.var.etc.init_vars.init()  # связь основных Var
    lr_lib.core.var.vars_highlight.init_highlight_words()  # слова для подсветки
    lr_lib.core.var.vars_param.DENY_PARAMS_update_and_lower()  # слова для подсветки

    if as_console:  # поиск param из консоли
        c_args = _console_argument_parser()
        _console_vars_setter(c_args)
        lr_lib.core.wrsp.files.init()
        return c_args

    else:  # для поиска из gui
        lr_lib.core.wrsp.files.init()
        return {}


def start(c_args: dict, echo=True) -> str:
    """
    консольное использование - поиск param из ядра
    """
    lr_vars.VarParam.set(c_args['param'])  # найти файлы с param
    web_reg_save_param = lr_lib.core.wrsp.param.create_web_reg_save_param()  # сформировать wrsp

    if echo:
        lr_vars.Logger.info(web_reg_save_param, notepad=True)
    return web_reg_save_param


def _console_vars_setter(c_args: dict) -> None:
    """
    задать из ArgumentParser
    """
    if 'last_file' in c_args:
        lr_vars.VarFirstLastFile.set(c_args['last_file'])
    if 'min_inf' in c_args:
        lr_vars.VarSearchMinSnapshot.set(c_args['min_inf'])
    if 'max_inf' in c_args:
        lr_vars.VarSearchMaxSnapshot.set(c_args['max_inf'])
    if 'encoding' in c_args:
        lr_lib.core.var.etc.vars_other.VarEncode.set(c_args['encoding'])
    lr_vars.VarFileNamesNumsShow.set(c_args['file_names'])
    lr_vars.VarAllFilesStatistic.set(c_args['statistic'])
    return


def _console_argument_parser() -> Dict[str, str]:
    """
    ArgumentParser - аргументы из консоли
    """
    p = argparse.ArgumentParser()
    p.add_argument('param', nargs='?', help='параметр из LoadRunner')
    p.add_argument('-last', '--last_file', help='выбрать последний, из найденных файлов, иначе первый', type=int)
    p.add_argument('-min', '--min_inf', help='ограничение(для поиска param) минимального номера inf', type=int)
    p.add_argument('-max', '--max_inf', help='ограничение(для поиска param) максимального номера inf', type=int)
    p.add_argument('-n', '--notepad', help='открыть результат в notepad', type=int, default=1)
    p.add_argument('-e', '--encoding', help='кодировка', type=str)
    p.add_argument('-names', '--file_names', help='показывать имена найденных файлов', type=int, default=0)
    p.add_argument('-s', '--statistic', help='формировать статистику для найденных файлов', type=int, default=0)

    c_args = {k: v for (k, v) in p.parse_args().__dict__.items() if ((not k.startswith('_')) and (v is not None))}
    return c_args
