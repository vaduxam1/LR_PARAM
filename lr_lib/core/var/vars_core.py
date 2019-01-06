# -*- coding: UTF-8 -*-
# центразизованная  установка lr_vars Var's callback, после импорта всех модулей
# "иерархическая связь" основных Var's друг с другом
# VarParam ->> VarFileName -> VarFile -> VarFileText ->> VarPartNum ->> VarLB/VarRB -> VarWrspDict ->>
#                                                                                       ->> lr_param.web_reg_save_param

import string  # через gui, используется в eval splitters_combo(), не удалять !

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_other
import lr_lib.core.var.vars_param


def init() -> None:
    """
    установка всех lr_vars.Var's callback
    запускать при старте !
    """
    lr_vars.VarParam.callback_set = lr_lib.core.wrsp.param.get_files_with_param
    lr_vars.VarFileName.callback_set = _set_file_name
    lr_vars.VarFile.callback_set = _set_file
    lr_vars.VarPartNum.callback_set = set_part_num
    return


def _set_file_name(name: str) -> None:
    """установка Var имени файла(3)"""
    file = lr_lib.core.wrsp.files.get_file_with_kwargs(lr_vars.FilesWithParam, Name=name)
    assert file, 'файл "{n}" ({tn}) ненайден. {tf} {f}'.format(n=name, tn=type(name), tf=type(file), f=file)
    lr_vars.VarFile.set(file)
    return


def _set_file(file: dict, errors='replace') -> None:
    """чение файла в lr_vars.VarFileText"""
    ff = file['File']

    with open(ff['FullName'], encoding=lr_lib.core.var.vars_other.VarEncode.get(), errors=errors) as f:
        lr_vars.VarFileText.set(f.read())

    lr_vars.VarPartNum.set(0)

    if not ff['timeCreate']:  # создать статистику, если нет
        lr_lib.core.wrsp.files.set_file_statistic(file, as_text=True)
        # сохранить статистику в AllFiles
        file_from_allfiles = lr_lib.core.wrsp.files.get_file_with_kwargs(lr_vars.AllFiles, Name=ff['Name'])
        file_from_allfiles.update({k: file[k] for k in file if (k != 'Param')})
    return


def _is_mutable_bound(st: str, b1: '{', b2: '}', a2=0) -> int:
    """находится ли внутри скобок {...}"""
    for (e, s) in enumerate(st, start=1):
        if s == b1:
            a2 += 1
        elif s == b2:
            if a2:
                a2 -= 1
            else:
                return e
        continue
    return 0


def is_mutable_bound(left: str, right: str, b1='{', b2='}') -> [int, int]:
    """находится ли внутри скобок"""
    ml = _is_mutable_bound(left[::-1], b2, b1)
    mr = _is_mutable_bound(right, b1, b2)
    return [ml, mr]


def set_part_num(num=0) -> None:
    """сформировать VarLB VarRB, с учетом номера вхождения param"""
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
        next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[LB]')
        return
    elif lr_vars.VarPartNumEmptyRbNext.get() and (not rb):
        next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[RB]')
        return

    # обрезать по \n
    if lr_vars.VarReturnLB.get():
        lb = lb.rsplit('\n', 1)[-1]
    if lr_vars.VarReturnRB.get():
        rb = rb.split('\n', 1)[0]

    # обрезать по 'непечатные/русские'
    if lr_vars.VarRusLB.get():
        lb = ''.join(lr_lib.core.etc.other.only_ascii_symbols(lb[::-1]))[::-1]
    if lr_vars.VarRusRB.get():
        rb = ''.join(lr_lib.core.etc.other.only_ascii_symbols(rb))

    (lb, rb) = lb_rb_split_list_set(__lb, __rb, lb, rb)
    (lb, rb) = lb_rb_split_end(lb, rb)

    if lr_vars.VarLbLstrip.get():
        lb = lb.lstrip()
    if lr_vars.VarRbRstrip.get():
        rb = rb.rstrip()

    # next (3) либо (4), при некорректном LB/RB(5)
    if lr_vars.VarPartNumEmptyLbNext.get() and not lb.strip():
        next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[LB]')
        return
    elif lr_vars.VarPartNumEmptyRbNext.get() and not rb.strip():
        next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[RB]')
        return
    if lr_vars.VarPartNumDenyLbNext.get() and not lr_lib.core.etc.lbrb_checker.check_bound_lb(__lb):
        next_3_or_4_if_bad_or_enmpy_lb_rb('недопустимом[LB]')
        return
    if lr_vars.VarPartNumDenyRbNext.get() and (not lr_lib.core.etc.lbrb_checker.check_bound_rb(__rb)):
        next_3_or_4_if_bad_or_enmpy_lb_rb('недопустимом[RB]')
        return

    # сохранить
    lr_vars.VarLB.set(lb)
    lr_vars.VarRB.set(rb)

    wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()
    lr_vars.VarWrspDict.set(wrsp_dict)
    return


def lb_rb_split_end(lb: str, rb: str) -> (str, str):
    """обрезать конечные символы lb rb"""
    if lr_vars.VarLEnd.get():
        llb = len(lb)
        if llb < 5:
            for s in lr_lib.core.var.vars_param.StripLBEnd1:
                lb = lb.rsplit(s, 1)
                lb = lb[1 if (len(lb) == 2) else 0]
                continue
        if (llb > 2) and any(map(lb.startswith, lr_lib.core.var.vars_param.StripLBEnd2)):
            lb = lb[2:].lstrip()
        elif (llb > 1) and any(map(lb.startswith, lr_lib.core.var.vars_param.StripLBEnd3)):
            lb = lb[1:].lstrip()

    if lr_vars.VarREnd.get():
        lrb = len(rb)
        if lrb < 5:
            for s in lr_lib.core.var.vars_param.StripRBEnd1:
                rb = rb.split(s, 1)[0]
                continue
        if (lrb > 2) and any(map(rb.endswith, lr_lib.core.var.vars_param.StripRBEnd2)):
            rb = rb[:-2].rstrip()
        elif (lrb > 1) and any(map(rb.endswith, lr_lib.core.var.vars_param.StripRBEnd3)):
            rb = rb[:-1].rstrip()

    return lb, rb


def lb_rb_split_list_set(__lb: str, __rb: str, lb: str, rb: str) -> (str, str):
    """lr_vars.VarSplitListNumRB.set(1) если {}: {...,'value':'param',...} / или .set(1) если []"""
    VarSplitListNumRB = lr_vars.VarSplitListNumRB.get()
    vlb1 = lr_vars.VarLbB1.get()
    vlb2 = lr_vars.VarLbB2.get()
    vrb1 = lr_vars.VarRbB1.get()
    vrb2 = lr_vars.VarRbB2.get()
    _l = (__lb if (vlb1 or vrb1) else '')
    _r = (__rb if (vlb2 or vrb2) else '')

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

            continue

    try:
        lb_combo = splitters_combo(lr_vars.Window.LBent_SplitList)
    except AttributeError:
        lb_combo = lr_lib.core.var.vars_param.SplitList
    try:
        rb_combo = splitters_combo(lr_vars.Window.RBent_SplitList)
    except AttributeError:
        rb_combo = lr_lib.core.var.vars_param.SplitList

    # обрезать из SplitList
    if lr_vars.VarSplitListLB.get():
        i_lb = lr_vars.VarSplitListNumLB.get()
        for word in lb_combo:
            lb_add = lb[:-i_lb]
            lb_main = lb[-i_lb:]

            lb_add = lb_add.rsplit(word, 1)
            lb_add = lb_add[-1]

            lb = (lb_add + lb_main)  # add_main_lb_{param}_rb_main_add
            continue

    if lr_vars.VarSplitListRB.get():
        i_rb = lr_vars.VarSplitListNumRB.get()
        for word in rb_combo:
            rb_main = rb[:i_rb]
            rb_add = rb[i_rb:]

            rb_add = rb_add.split(word, 1)
            rb_add = rb_add[0]

            rb = (rb_main + rb_add)  # add_main_lb_{param}_rb_main_add
            continue

    lr_vars.VarSplitListNumRB.set(VarSplitListNumRB)  # вернуть
    return lb, rb


def gui_updater_comboParts() -> None:
    """при изменении из ядра, менять gui comboParts"""
    if lr_vars.Window and (not lr_vars.Window._block_):
        lr_vars.Window.comboParts.set(lr_vars.VarPartNum.get())
    return


def gui_updater_comboFiles() -> None:
    """при изменении из ядра, менять gui comboFiles"""
    if lr_vars.Window and (not lr_vars.Window._block_):
        f = lr_vars.VarFileName.get()
        lr_vars.Window.comboFiles.set(f)
        lr_vars.Window.comboPartsFill()
    return


NF3 = ('%s\nNEXT файл(3), при {text} в (5):\n {indx}-> {ni}/{len_files} : {f} -> {next_file}' % ('_'*50))
NP4 = ' next вхождение(4), при {text} в (5):\n\t\t[ {num}-> {n}/{pc} ] : {f}'
UW = '''
Все возможные LB/RB(5), для формирования param "{p}", пустые/недопустимые.
'Снятие чекбокса "deny" или "strip", вероятно поможет. 
Если требуется, переход к месту замены в тексте, снять чекбоскс "NoAsk", либо установить "forceAsk".
'''


def next_3_or_4_if_bad_or_enmpy_lb_rb(text='') -> None:
    """увеличить(3) либо (4)"""
    file = lr_vars.VarFile.get()
    name = file['File']['Name']

    count_n = file['Param']['Count']
    old_n = lr_vars.VarPartNum.get()
    new_n = (old_n + 1)

    if new_n < count_n:  # вхождение(4)
        lr_vars.MainThreadUpdater.submit(gui_updater_comboParts)
        lr_vars.Logger.trace(NP4.format(num=(old_n + 1), n=(new_n + 1), pc=count_n, f=name, text=text, p='', ))

        # установить
        lr_vars.VarPartNum.set(new_n)
        return  # корректный выход

    else:  # файл(3)
        index = lr_vars.FilesWithParam.index(file)
        new_i = (index + 1)
        try:
            file_new = lr_vars.FilesWithParam[new_i]
        except IndexError:
            pass
        else:
            new_file_name = file_new['File']['Name']

            lr_vars.MainThreadUpdater.submit(gui_updater_comboFiles)
            lr_vars.Logger.trace(NF3.format(len_files=len(lr_vars.FilesWithParam), indx=(index + 1), ni=(new_i + 1),
                                            f=name, next_file=new_file_name, text=text, ))
            lr_vars.Logger.trace(NP4.format(num=1, n=1, pc=file_new['Param']['Count'], f=new_file_name, text=text, ))

            # установить
            lr_vars.VarFileName.set(new_file_name)
            return  # корректный выход

    # UserWarning - признак окончания для action_lib._all_wrsp_dict_web_reg_save_param()
    raise UserWarning(UW.format(p=lr_vars.VarParam.get(), ))


def splitters_combo(combo) -> [str, ]:
    """eval разделителей из gui"""
    splitter = combo.get()
    all_splitters = list(combo['values'])

    if splitter not in all_splitters:
        combo['values'] = list(reversed(all_splitters + [splitter]))

    e = eval(splitter)
    return e

