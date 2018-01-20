# -*- coding: UTF-8 -*-
# центразизованная  установка defaults Var's callback, после импорта всех модулей
# "иерархическая связь" основных Var's друг с другом
# VarParam ->> VarFileName -> VarFile -> VarFileText ->> VarPartNum ->> VarLB/VarRB -> VarWrspDict ->>
#                                                                                       ->> lr_param.web_reg_save_param

import string  # не удалять!, для пользовательского eval() из программы

from lr_lib import (
    defaults,
    param as lr_param,
    files as lr_files,
    other as lr_other,
    logger as lr_log,
)


def initVars() -> None:
    '''
    установка всех defaults.Var's callback
    запускать при старте !
    '''
    defaults.VarParam.callback_set = lr_param.get_files_with_param
    defaults.VarFileName.callback_set = _set_file_name
    defaults.VarFile.callback_set = _set_file
    defaults.VarPartNum.callback_set = _set_part_num


def _set_file_name(name: str) -> None:
    '''установка Var имени файла(3)'''
    file = lr_files.get_file_with_kwargs(defaults.FilesWithParam, Name=name)
    assert file, 'файл "{n}" ({tn}) ненайден. {tf} {f}'.format(n=name, tn=type(name), tf=type(file), f=file)
    defaults.VarFile.set(file)

def _set_file(file: dict) -> None:
    '''чение файла в defaults.VarFileText'''
    file_f = file['File']

    with open(file_f['FullName'], encoding=defaults.VarEncode.get(), errors='replace') as f:
        defaults.VarFileText.set(f.read())
    defaults.VarPartNum.set(0)

    if not file_f['Size']:  # создать статистику, если нет
        lr_files.set_file_statistic(file, as_text=True)
        # сохранить статистику в AllFiles
        file_from_all = lr_files.get_file_with_kwargs(defaults.AllFiles, Name=file_f['Name'])
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
    param = defaults.VarParam.get()
    assert param, 'Пустой param(1)[{tp}]:"{p}"'.format(tp=type(param), p=param)

    defaults.VarWrspDict.set({})
    split_text = defaults.VarFileText.get().split(param)

    try:  # обрезать по длине
        __lb = split_text[num]
        __rb = split_text[num + 1]
        lb = __lb[-defaults.VarMaxLenLB.get():]
        rb = __rb[:defaults.VarMaxLenRB.get()]
    except Exception:
        lr_log.Logger.error('Вероятно закончились доступные комбинации (3)/(4) для посика корректных LB/RB\n\nфайлов: {}, param_num: {}, split_text: {}\n\nфайл: {}'.format(len(defaults.FilesWithParam), num, len(split_text), defaults.VarFile.get()))
        raise

    # next (3) либо (4), при пустом LB/RB(5)
    if defaults.VarPartNumEmptyLbNext.get() and (not lb):
        return next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[LB]')
    elif defaults.VarPartNumEmptyRbNext.get() and (not rb):
        return next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[RB]')

    # обрезать по \n
    if defaults.VarReturnLB.get():
        lb = lb.rsplit('\n', 1)[-1]
    if defaults.VarReturnRB.get():
        rb = rb.split('\n', 1)[0]

    # обрезать по 'непечатные/русские'
    if defaults.VarRusLB.get():
        lb = ''.join(lr_other.only_ascii_symbols(lb[::-1]))[::-1]
    if defaults.VarRusRB.get():
        rb = ''.join(lr_other.only_ascii_symbols(rb))

    # defaults.VarSplitListNumRB.set(1) если {} : {... , 'value': 'param', ...}
    VarSplitListNumRB = defaults.VarSplitListNumRB.get()
    vlb1 = defaults.VarLbB1.get()
    vlb2 = defaults.VarLbB2.get()
    vrb1 = defaults.VarRbB1.get()
    vrb2 = defaults.VarRbB2.get()
    _l = __lb if (vlb1 or vrb1) else ''
    _r = __rb if (vlb2 or vrb2) else ''
    if _l or _r:
        bound1 = is_mutable_bound(_l, _r, b1='{', b2='}')
        bound2 = is_mutable_bound(_l, _r, b1='[', b2=']')
        for (indx_1, indx_2, allow_1, allow_2) in zip(bound1, bound2, [vlb1, vrb1], [vlb2, vrb2]):
            if allow_1 and indx_1:
                if indx_2:
                    if indx_1 < indx_2:
                        defaults.VarSplitListNumRB.set(1)
                    elif allow_2:
                        defaults.VarSplitListNumRB.set(3)
                else:
                    defaults.VarSplitListNumRB.set(1)
                break
            elif allow_2 and indx_2:
                defaults.VarSplitListNumRB.set(3)
                break
    
    try:  # обрезать из SplitList
        lb_combo = defaults.Window.LBent_SplitList
        rb_combo = defaults.Window.RBent_SplitList
    except AttributeError:
        lb_combo = rb_combo = defaults.SplitList

    if defaults.VarSplitListLB.get():
        i_lb = defaults.VarSplitListNumLB.get()
        for word in splitters_combo(lb_combo):
            lb = lb[:-i_lb].rsplit(word, 1)[-1] + lb[-i_lb:]
    if defaults.VarSplitListRB.get():
        i_rb = defaults.VarSplitListNumRB.get()
        for word in splitters_combo(rb_combo):
            rb = rb[:i_rb] + rb[i_rb:].split(word, 1)[0]
    defaults.VarSplitListNumRB.set(VarSplitListNumRB)

    if defaults.VarRbRstrip.get():
        rb = rb.rstrip()
    if defaults.VarLbLstrip.get():
        lb = lb.lstrip()

    if defaults.VarREnd.get():
        lrb = len(rb)
        if lrb < 5:
            for s in ['{', '}', '[', ']', ]:
                rb = rb.split(s, 1)[0]
        if (lrb > 2) and any(map(rb.endswith, [',{', ])):
            rb = rb[:-2].rstrip()
        elif (lrb > 1) and any(map(rb.endswith, ['{', ','])):
            rb = rb[:-1].rstrip()

    if defaults.VarLEnd.get():
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
    if defaults.VarPartNumEmptyLbNext.get() and not lb.strip():
        return next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[LB]')
    elif defaults.VarPartNumEmptyRbNext.get() and not rb.strip():
        return next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[RB]')
    if defaults.VarPartNumDenyLbNext.get() and not lr_other.check_bound_lb(__lb):
        return next_3_or_4_if_bad_or_enmpy_lb_rb('недопустимом[LB]')
    if defaults.VarPartNumDenyRbNext.get() and (not lr_other.check_bound_rb(__rb)):
        return next_3_or_4_if_bad_or_enmpy_lb_rb('недопустимом[RB]')

    # сохранить
    defaults.VarLB.set(lb)
    defaults.VarRB.set(rb)

    wrsp_dict = lr_param.wrsp_dict_creator()
    defaults.VarWrspDict.set(wrsp_dict)


def next_3_or_4_if_bad_or_enmpy_lb_rb(text='') -> None:
    '''увеличить(3) либо (4), при пустом str.strip(LB/RB(5))'''
    len_files = len(defaults.FilesWithParam) - 1  # нумерация с 0
    num = defaults.VarPartNum.get()
    n = num + 1
    file = defaults.VarFile.get()

    if n < file['Param']['Count']:  # вхождение(4)
        defaults.VarPartNum.set(n)

        if defaults.Window and not defaults.Window._block_:  # при изменении из ядра, менять gui виджеты
            defaults.Window.comboParts.set(defaults.VarPartNum.get())

        lr_log.Logger.trace('next вхождение(4), при {text} в (5)\n\t{num}->{n}/{pc} : {f} | {p}'.format(num=num, n=n, pc=(file['Param']['Count'] - 1), f=file['File']['Name'], text=text, p=defaults.VarParam.get()))
        return

    elif len_files > 0:  # файл(3)
        indx = defaults.FilesWithParam.index(file)
        if indx < len_files:
            i = indx + 1
            next_file = defaults.FilesWithParam[i]
            file_name = next_file['File']['Name']
            defaults.VarFileName.set(file_name)

            if defaults.Window and not defaults.Window._block_:  # при изменении из ядра, менять gui виджеты
                defaults.Window.comboFiles.set(defaults.VarFileName.get())
                defaults.Window.comboPartsFill()

            lr_log.Logger.trace('next файл(3), при {text} в (5)\n\t{indx}->{ni}/{len_files} : {f} -> {next_file} | {p}'.format(len_files=len_files, indx=indx, ni=i, f=file['File']['Name'], next_file=file_name, text=text, p=defaults.VarParam.get()))
            return

    raise UserWarning('Все возможные LB/RB(5), для формирования param "{p}", пустые/недопустимые.\nСнятие чекбокса "deny" или "strip", вероятно поможет. Если требуется, переход к месту замены в тексте, снять чекбоскс "NoAsk", либо установить "forceAsk".'.format(p=defaults.VarParam.get()))


def splitters_combo(combo) -> [str, ]:
    '''eval + история'''
    splitter = combo.get()
    all_splitters = list(combo['values'])

    if splitter not in all_splitters:
        combo['values'] = list(reversed(all_splitters + [splitter]))

    return eval(splitter)