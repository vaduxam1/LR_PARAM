﻿# -*- coding: UTF-8 -*-
# центразизованная  установка lr_vars Var's callback, после импорта всех модулей
# "иерархическая связь" основных Var's друг с другом
# VarParam ->> VarFileName -> VarFile -> VarFileText ->> VarPartNum ->> VarLB/VarRB -> VarWrspDict ->>
#                                                                                       ->> lr_param.web_reg_save_param

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param as lr_param
import lr_lib.core.wrsp.files as lr_files
import lr_lib.core.etc.other as lr_other
import lr_lib.core.etc.lbrb_checker as lr_lbrb_checker


def init() -> None:
    '''
    установка всех lr_vars.Var's callback
    запускать при старте !
    '''
    lr_vars.VarParam.callback_set = lr_param.get_files_with_param
    lr_vars.VarFileName.callback_set = _set_file_name
    lr_vars.VarFile.callback_set = _set_file
    lr_vars.VarPartNum.callback_set = _set_part_num


def _set_file_name(name: str) -> None:
    '''установка Var имени файла(3)'''
    file = lr_files.get_file_with_kwargs(lr_vars.FilesWithParam, Name=name)
    assert file, 'файл "{n}" ({tn}) ненайден. {tf} {f}'.format(n=name, tn=type(name), tf=type(file), f=file)
    lr_vars.VarFile.set(file)

def _set_file(file: dict) -> None:
    '''чение файла в lr_vars.VarFileText'''
    file_f = file['File']

    with open(file_f['FullName'], encoding=lr_vars.VarEncode.get(), errors='replace') as f:
        lr_vars.VarFileText.set(f.read())
    lr_vars.VarPartNum.set(0)

    if not file_f['Size']:  # создать статистику, если нет
        lr_files.set_file_statistic(file, as_text=True)
        # сохранить статистику в AllFiles
        file_from_all = lr_files.get_file_with_kwargs(lr_vars.AllFiles, Name=file_f['Name'])
        file_from_all['File'].update(file_f)


def _is_mutable_bound(st: str, b1: '{', b2: '}', a2=0) -> int:
    '''находится ли внутри скобок {...}'''
    for e, s in enumerate(st, start=1):
        if s == b1:
            a2 += 1
        elif s == b2:
            if a2:
                a2 -= 1
            else:
                return e
    return 0


def is_mutable_bound(left: str, right: str, b1='{', b2='}') -> [int, int]:
    '''находится ли внутри скобок'''
    return [_is_mutable_bound(left[::-1], b2, b1), _is_mutable_bound(right, b1, b2)]


def _set_part_num(num=0) -> None:
    return set_part_num(num=num)


def set_part_num(num=0) -> None:
    '''сформировать VarLB VarRB, с учетом номера вхождения param'''
    param = lr_vars.VarParam.get()
    assert param, 'Пустой param(1)[{tp}]:"{p}"'.format(tp=type(param), p=param)

    lr_vars.VarWrspDict.set({})
    split_text = lr_vars.VarFileText.get().split(param)

    try:  # обрезать по длине
        __lb = split_text[num]
        __rb = split_text[num + 1]
        lb = __lb[-lr_vars.VarMaxLenLB.get():]
        rb = __rb[:lr_vars.VarMaxLenRB.get()]
    except Exception:
        lr_vars.Logger.error('Вероятно закончились доступные комбинации (3)/(4) для посика корректных LB/RB\n\n'
                             'файлов: {}, param_num: {}, split_text: {}\n\nфайл: {}'.format(
            len(lr_vars.FilesWithParam), num, len(split_text), lr_vars.VarFile.get()))
        raise

    # next (3) либо (4), при пустом LB/RB(5)
    if lr_vars.VarPartNumEmptyLbNext.get() and (not lb):
        return next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[LB]')
    elif lr_vars.VarPartNumEmptyRbNext.get() and (not rb):
        return next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[RB]')

    # обрезать по \n
    if lr_vars.VarReturnLB.get():
        lb = lb.rsplit('\n', 1)[-1]
    if lr_vars.VarReturnRB.get():
        rb = rb.split('\n', 1)[0]

    # обрезать по 'непечатные/русские'
    if lr_vars.VarRusLB.get():
        lb = ''.join(lr_other.only_ascii_symbols(lb[::-1]))[::-1]
    if lr_vars.VarRusRB.get():
        rb = ''.join(lr_other.only_ascii_symbols(rb))

    # lr_vars.VarSplitListNumRB.set(1) если {} : {... , 'value': 'param', ...}
    VarSplitListNumRB = lr_vars.VarSplitListNumRB.get()
    vlb1 = lr_vars.VarLbB1.get()
    vlb2 = lr_vars.VarLbB2.get()
    vrb1 = lr_vars.VarRbB1.get()
    vrb2 = lr_vars.VarRbB2.get()
    _l = __lb if (vlb1 or vrb1) else ''
    _r = __rb if (vlb2 or vrb2) else ''
    if _l or _r:
        bound1 = is_mutable_bound(_l, _r, b1='{', b2='}')
        bound2 = is_mutable_bound(_l, _r, b1='[', b2=']')
        for (indx_1, indx_2, allow_1, allow_2) in zip(bound1, bound2, [vlb1, vrb1], [vlb2, vrb2]):
            if allow_1 and indx_1:
                if indx_2:
                    if indx_1 < indx_2:
                        lr_vars.VarSplitListNumRB.set(1)
                    elif allow_2:
                        lr_vars.VarSplitListNumRB.set(3)
                else:
                    lr_vars.VarSplitListNumRB.set(1)
                break
            elif allow_2 and indx_2:
                lr_vars.VarSplitListNumRB.set(3)
                break
    
    try:  # обрезать из SplitList
        lb_combo = lr_vars.Window.LBent_SplitList
        lb_combo = splitters_combo(lb_combo)
        rb_combo = lr_vars.Window.RBent_SplitList
        rb_combo = splitters_combo(rb_combo)
    except AttributeError:
        lb_combo = rb_combo = lr_vars.SplitList

    if lr_vars.VarSplitListLB.get():
        i_lb = lr_vars.VarSplitListNumLB.get()
        for word in lb_combo:
            lb = lb[:-i_lb].rsplit(word, 1)[-1] + lb[-i_lb:]

    if lr_vars.VarSplitListRB.get():
        i_rb = lr_vars.VarSplitListNumRB.get()
        for word in rb_combo:
            rb = rb[:i_rb] + rb[i_rb:].split(word, 1)[0]

    lr_vars.VarSplitListNumRB.set(VarSplitListNumRB)  # вернуть

    if lr_vars.VarRbRstrip.get():
        rb = rb.rstrip()
    if lr_vars.VarLbLstrip.get():
        lb = lb.lstrip()

    if lr_vars.VarREnd.get():
        lrb = len(rb)
        if lrb < 5:
            for s in ['{', '}', '[', ']', ]:
                rb = rb.split(s, 1)[0]
        if (lrb > 2) and any(map(rb.endswith, [',{', ])):
            rb = rb[:-2].rstrip()
        elif (lrb > 1) and any(map(rb.endswith, ['{', ','])):
            rb = rb[:-1].rstrip()

    if lr_vars.VarLEnd.get():
        llb = len(lb)
        if llb < 5:
            for s in ['{', '}', '[', ']', ]:
                lb = lb.rsplit(s, 1)
                lb = lb[1 if (len(lb) == 2) else 0]
        if (llb > 2) and any(map(lb.startswith, ['},', ])):
            lb = lb[2:].lstrip()
        elif (llb > 1) and any(map(lb.startswith, ['{', ',', ])):
            lb = lb[1:].lstrip()

    # next (3) либо (4), при некорректном LB/RB(5)
    if lr_vars.VarPartNumEmptyLbNext.get() and not lb.strip():
        return next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[LB]')
    elif lr_vars.VarPartNumEmptyRbNext.get() and not rb.strip():
        return next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[RB]')
    if lr_vars.VarPartNumDenyLbNext.get() and not lr_lbrb_checker.check_bound_lb(__lb):
        return next_3_or_4_if_bad_or_enmpy_lb_rb('недопустимом[LB]')
    if lr_vars.VarPartNumDenyRbNext.get() and (not lr_lbrb_checker.check_bound_rb(__rb)):
        return next_3_or_4_if_bad_or_enmpy_lb_rb('недопустимом[RB]')

    # сохранить
    lr_vars.VarLB.set(lb)
    lr_vars.VarRB.set(rb)

    wrsp_dict = lr_param.wrsp_dict_creator()
    lr_vars.VarWrspDict.set(wrsp_dict)


def next_3_or_4_if_bad_or_enmpy_lb_rb(text='') -> None:
    '''увеличить(3) либо (4))'''
    len_files = len(lr_vars.FilesWithParam) - 1  # нумерация с 0
    num = lr_vars.VarPartNum.get()
    n = num + 1
    file = lr_vars.VarFile.get()

    if n < file['Param']['Count']:  # вхождение(4)
        lr_vars.VarPartNum.set(n)

        if lr_vars.Window and not lr_vars.Window._block_:  # при изменении из ядра, менять gui виджеты
            lr_vars.Window.comboParts.set(lr_vars.VarPartNum.get())

        lr_vars.Logger.trace('next вхождение(4), при {text} в (5)\n\t{num}->{n}/{pc} : {f} | {p}'.format(
            num=num, n=n, pc=(file['Param']['Count'] - 1), f=file['File']['Name'], text=text, p=lr_vars.VarParam.get()))
        return

    elif len_files > 0:  # файл(3)
        indx = lr_vars.FilesWithParam.index(file)
        if indx < len_files:
            i = indx + 1
            next_file = lr_vars.FilesWithParam[i]
            file_name = next_file['File']['Name']
            lr_vars.VarFileName.set(file_name)

            if lr_vars.Window and not lr_vars.Window._block_:  # при изменении из ядра, менять gui виджеты
                lr_vars.Window.comboFiles.set(lr_vars.VarFileName.get())
                lr_vars.Window.comboPartsFill()

            lr_vars.Logger.trace('next файл(3), при {text} в (5)\n\t{indx}->{ni}/{len_files} : {f} -> {next_file} | {p}'.format(
                len_files=len_files, indx=indx, ni=i, f=file['File']['Name'], next_file=file_name, text=text, p=lr_vars.VarParam.get()))
            return

    raise UserWarning('Все возможные LB/RB(5), для формирования param "{p}", пустые/недопустимые.\n'
                      'Снятие чекбокса "deny" или "strip", вероятно поможет. Если требуется, переход к месту замены '
                      'в тексте, снять чекбоскс "NoAsk", либо установить "forceAsk".'.format(p=lr_vars.VarParam.get()))


def splitters_combo(combo) -> [str, ]:
    '''eval + история'''
    splitter = combo.get()
    all_splitters = list(combo['values'])

    if splitter not in all_splitters:
        combo['values'] = list(reversed(all_splitters + [splitter]))

    return eval(splitter)