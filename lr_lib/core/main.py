# -*- coding: UTF-8 -*-
# старт core

import argparse

import lr_lib.core.var.vars_func as lr_vars_func
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.files as lr_files
import lr_lib.core.wrsp.param as lr_param


def init() -> None:
    '''стартовать core'''
    lr_vars_func.init()  # связь основных Var
    lr_files.init()  # создать файлы ответов


def console_start(echo=True) -> str:
    '''консольное использование'''
    args_dict = console_argument_parser()
    console_vars_setter(args_dict)

    web_reg_save_param = core_find_wrsp(args_dict['param'])
    if echo:
        lr_vars.Logger.info(web_reg_save_param, notepad=True)
    return web_reg_save_param


def core_find_wrsp(param: str) -> str:
    '''поиск param из ядра'''
    lr_vars.VarParam.set(param)  # найти файлы с param
    web_reg_save_param = lr_param.create_web_reg_save_param()  # сформировать wrsp
    return web_reg_save_param


def console_vars_setter(args_dict: dict) -> None:
    '''задать переданные переменные'''
    if 'last_file' in args_dict:
        lr_vars.VarFirstLastFile.set(args_dict['last_file'])
    if 'min_inf' in args_dict:
        lr_vars.VarSearchMinSnapshot.set(args_dict['min_inf'])
    if 'max_inf' in args_dict:
        lr_vars.VarSearchMaxSnapshot.set(args_dict['max_inf'])
    if 'encoding' in args_dict:
        lr_vars.VarEncode.set(args_dict['encoding'])
    lr_vars.VarFileNamesNumsShow.set(args_dict['file_names'])
    lr_vars.VarAllFilesStatistic.set(args_dict['statistic'])


def console_argument_parser() -> {str: str}:
    ''''аргументы из консоли + задать переданные переменные'''
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
    return args_dict
