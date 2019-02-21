# -*- coding: UTF-8 -*-
# сформировать VarLB VarRB

import lr_lib
from lr_lib.core.var import vars as lr_vars
from lr_lib.core.var.var_callback.mutable_bound import lb_rb_split_list_set


def set_param_part_num(num=0) -> None:
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
                i = (_llb == 2)
                lb = lb[i]  # True=1/False=0
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
    p = lr_vars.VarParam.get()
    raise UserWarning(UW.format(p=p, ))


ER1 = '''
Вероятно закончились доступные комбинации (3)/(4) для посика корректных LB/RB

файлов: {}, param_num: {}, split_text: {}

файл: {}
'''.strip()


def gui_updater_comboParts() -> None:
    """
    при изменении из ядра, менять gui comboParts
    """
    if lr_vars.Window and (not lr_vars.Window._block_):
        n = lr_vars.VarPartNum.get()
        lr_vars.Window.comboParts.set(n)
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
