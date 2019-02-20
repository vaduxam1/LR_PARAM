﻿# -*- coding: UTF-8 -*-
# центразизованная  установка lr_vars Var's callback, после импорта всех модулей
# "иерархическая связь" основных Var's друг с другом
# VarParam ->> VarFileName -> VarFile -> VarFileText ->> VarPartNum ->> VarLB/VarRB -> VarWrspDict ->>
#                                                                                       ->> lr_param.web_reg_save_param

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
    """
    установка Var имени файла(3)
    """
    file = lr_lib.core.wrsp.files.get_file_with_kwargs(lr_vars.FilesWithParam, Name=name)
    assert file, 'файл "{n}" ({tn}) ненайден. {tf} {f}'.format(n=name, tn=type(name), tf=type(file), f=file)
    lr_vars.VarFile.set(file)
    return


def _set_file(file: dict, errors='replace', first_param_part4_num=0) -> None:
    """
    чение файла в lr_vars.VarFileText
    """
    ff = file['File']
    fname = ff['FullName']
    with open(fname, encoding=lr_lib.core.var.vars_other.VarEncode.get(), errors=errors) as f:
        file_text = f.read()
        lr_vars.VarFileText.set(file_text)

    lr_vars.VarPartNum.set(first_param_part4_num)  # выбрать номер варианта вхождения param в файл

    ct = ff['timeCreate']
    if not ct:  # создать статистику, если нет
        lr_lib.core.wrsp.files.set_file_statistic(file, as_text=True)
        # сохранить статистику в AllFiles
        name = ff['Name']
        file_from_allfiles = lr_lib.core.wrsp.files.get_file_with_kwargs(lr_vars.AllFiles, Name=name)
        fp = {k: file[k] for k in file if (k != 'Param')}
        file_from_allfiles.update(fp)
    return


def _is_mutable_bound(stri: str, bound_left: '{', bound_right: '}', _equation=0, _indx=0, ) -> int:
    """
    находится ли внутри скобок {...}
    """
    for (_indx, symb) in enumerate(stri, start=1):
        if symb == bound_left:
            _equation += 1
        elif symb == bound_right:
            if _equation:
                _equation -= 1
            else:
                return _indx  # внутри скобок
        else:
            pass
        continue
    return _indx  # не внутри скобок


def is_mutable_bound(left: str, right: str, b1='{', b2='}') -> [int, int]:
    """
    находится ли внутри скобок
    """
    left_ = left[::-1]
    ml = _is_mutable_bound(left_, b2, b1)
    mr = _is_mutable_bound(right, b1, b2)
    item = [ml, mr]
    return item


ER1 = '''
Вероятно закончились доступные комбинации (3)/(4) для посика корректных LB/RB

файлов: {}, param_num: {}, split_text: {}

файл: {}
'''.strip()


def set_part_num(num=0) -> None:
    """
    сформировать VarLB VarRB, с учетом номера вхождения param
    """
    param = lr_vars.VarParam.get()
    assert param, 'Пустой param(1)[{tp}]:"{p}"'.format(tp=type(param), p=param)

    lr_vars.VarWrspDict.set(dict())  # clear

    text = lr_vars.VarFileText.get()
    split_text = text.split(param)

    try:  # обрезать по длине
        __lb = split_text[num]
        __rb = split_text[num + 1]
        il = lr_vars.VarMaxLenLB.get()
        lb = __lb[-il:]
        ir = lr_vars.VarMaxLenRB.get()
        rb = __rb[:ir]
    except Exception:
        f = lr_vars.VarFile.get()
        lf = len(lr_vars.FilesWithParam)
        ls = len(split_text)
        e = ER1.format(lf, num, ls, f)
        lr_vars.Logger.error(e)
        raise

    # next (3) либо (4), при пустом LB/RB(5)
    if lr_vars.VarPartNumEmptyLbNext.get() and (not lb):
        next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[LB]')
        return
    elif lr_vars.VarPartNumEmptyRbNext.get() and (not rb):
        next_3_or_4_if_bad_or_enmpy_lb_rb('пустом[RB]')
        return
    else:
        pass

    # обрезать по \n
    if lr_vars.VarReturnLB.get():
        lb = lb.rsplit('\n', 1)[-1]
    if lr_vars.VarReturnRB.get():
        rb = rb.split('\n', 1)[0]

    # обрезать по 'непечатные/русские'
    if lr_vars.VarRusLB.get():
        l_ = lb[::-1]
        l_ = lr_lib.core.etc.other.only_ascii_symbols(l_)
        lb = ''.join(l_)
        lb = lb[::-1]
    if lr_vars.VarRusRB.get():
        r_ = lr_lib.core.etc.other.only_ascii_symbols(rb)
        rb = ''.join(r_)

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
    elif lr_vars.VarPartNumDenyLbNext.get() and (not lr_lib.core.etc.lbrb_checker.check_bound_lb(__lb)):
        next_3_or_4_if_bad_or_enmpy_lb_rb('недопустимом[LB]')
        return
    elif lr_vars.VarPartNumDenyRbNext.get() and (not lr_lib.core.etc.lbrb_checker.check_bound_rb(__rb)):
        next_3_or_4_if_bad_or_enmpy_lb_rb('недопустимом[RB]')
        return
    else:
        pass

    # сохранить
    lr_vars.VarLB.set(lb)
    lr_vars.VarRB.set(rb)

    wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()
    lr_vars.VarWrspDict.set(wrsp_dict)
    return


def lb_rb_split_end(lb: str, rb: str) -> (str, str):
    """
    обрезать конечные символы lb rb
    """
    if lr_vars.VarLEnd.get():
        llb = len(lb)
        if llb < 5:
            for s in lr_lib.core.var.vars_param.StripLBEnd1:
                lb = lb.rsplit(s, 1)
                _llb = len(lb)
                i = (1 if (_llb == 2) else 0)
                lb = lb[i]
                continue
        if (llb > 2) and any(map(lb.startswith, lr_lib.core.var.vars_param.StripLBEnd2)):
            lb = lb[2:].lstrip()
        elif (llb > 1) and any(map(lb.startswith, lr_lib.core.var.vars_param.StripLBEnd3)):
            lb = lb[1:].lstrip()
        else:
            pass

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
        else:
            pass

    item = (lb, rb)
    return item


def lb_rb_split_list_set(__lb: str, __rb: str, lb: str, rb: str, r_min=1, r_max=3, ) -> (str, str):
    """
    lr_vars.VarSplitListNumRB.set(1) если {}: {...,'value':'param',...} / или .set(1) если []
    """
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

        vb1 = [vlb1, vrb1, ]
        vb2 = [vlb2, vrb2, ]
        zi = zip(bound1, bound2, vb1, vb2, )
        for (indx_1, indx_2, allow_1, allow_2) in zi:

            if allow_1 and indx_1:
                if indx_2:
                    if indx_1 < indx_2:
                        lr_vars.VarSplitListNumRB.set(r_min)
                    elif allow_2:
                        lr_vars.VarSplitListNumRB.set(r_max)
                else:
                    lr_vars.VarSplitListNumRB.set(r_min)
                break
            elif allow_2 and indx_2:
                lr_vars.VarSplitListNumRB.set(r_max)
                break
            else:
                pass
            continue

    try:
        lb_combo = splitters_combo(lr_vars.Window.LBent_SplitList)
    except AttributeError:
        lb_combo = lr_lib.core.var.vars_param.SplitList
    try:
        rb_combo = splitters_combo(lr_vars.Window.RBent_SplitList)
    except AttributeError:
        rb_combo = lr_lib.core.var.vars_param.SplitList

    # LB обрезать из SplitList
    if lr_vars.VarSplitListLB.get():
        i_lb = lr_vars.VarSplitListNumLB.get()
        for word in lb_combo:
            lb_add = lb[:-i_lb]
            lb_main = lb[-i_lb:]

            lb_add = lb_add.rsplit(word, 1)
            lb_add = lb_add[-1]

            lb = (lb_add + lb_main)  # add_main_lb_{param}_rb_main_add
            continue

    # RB обрезать из SplitList
    if lr_vars.VarSplitListRB.get():
        check = False

        for bound in lr_lib.core.var.vars_param.RbStartswithBoundFixed:
            if rb.startswith(bound):
                rb = bound
                check = True
                break
            continue

        if not check:
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
    """
    при изменении из ядра, менять gui comboParts
    """
    if lr_vars.Window and (not lr_vars.Window._block_):
        lr_vars.Window.comboParts.set(lr_vars.VarPartNum.get())
    return


def gui_updater_comboFiles() -> None:
    """
    при изменении из ядра, менять gui comboFiles
    """
    if lr_vars.Window and (not lr_vars.Window._block_):
        f = lr_vars.VarFileName.get()
        lr_vars.Window.comboFiles.set(f)
        lr_vars.Window.comboPartsFill()
    return


NF3 = '%s\nNEXT файл(3), при {text} в (5):\n {indx}-> {ni}/{len_files} : {f} -> {next_file}'
NF3 = (NF3 % lr_vars.SEP)
NP4 = '\n\n next вхождение(4), при {text} в (5):\n\t\t[ {num}-> {n}/{pc} ] : {f}'
UW = '''
Все возможные LB/RB(5), для формирования param "{p}", пустые/недопустимые.
'Снятие чекбокса "deny" или "strip", вероятно поможет. 
Если требуется, переход к месту замены в тексте, снять чекбоскс "NoAsk", либо установить "forceAsk".
'''


def next_3_or_4_if_bad_or_enmpy_lb_rb(text='') -> None:
    """
    увеличить(3) либо (4)
    """
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
            lf = len(lr_vars.FilesWithParam)
            pc = file_new['Param']['Count']
            i = NF3.format(len_files=lf, indx=(index + 1), ni=(new_i + 1), f=name, next_file=new_file_name, text=text, )
            i += NP4.format(num=1, n=1, pc=pc, f=new_file_name, text=text, )
            lr_vars.Logger.trace(i)

            # установить
            lr_vars.VarFileName.set(new_file_name)
            return  # корректный выход

    # UserWarning - признак окончания для action_lib._all_wrsp_dict_web_reg_save_param()
    raise UserWarning(UW.format(p=lr_vars.VarParam.get(), ))


def splitters_combo(combo) -> [str, ]:
    """
    eval разделителей из gui
    """
    splitter = combo.get()
    all_splitters = list(combo['values'])

    if splitter not in all_splitters:
        combo['values'] = list(reversed(all_splitters + [splitter]))

    e = eval(splitter)
    return e
