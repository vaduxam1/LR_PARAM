# -*- coding: UTF-8 -*-
# все варианты создания web_reg_save_param

import lr_lib
import lr_lib.core
from lr_lib.core.var import vars as lr_vars
from lr_lib.gui.etc.action_lib import event_action_getter


@lr_vars.T_POOL_decorator
def all_wrsp_dict_web_reg_save_param(event, wrsp_web_=None) -> None:
    """все варианты создания web_reg_save_param, искать не ограничивая верхний номер Snapshot"""
    action = event_action_getter(event)
    m = action.max_inf_cbx_var.get()
    action.max_inf_cbx_var.set(0)
    selection = event.widget.selection_get()

    with action.block():
        try:
            for wrsp_web_ in filter(bool, _all_wrsp_dict_web_reg_save_param(action, selection)):
                continue
        finally:
            action.max_inf_cbx_var.set(m)

        if wrsp_web_:
            # action.tk_text_to_web_action(websReport=False)
            action.search_in_action(word=wrsp_web_.to_str())
    return


def _wrsp_text_delta_remove(wr: (dict, str), ) -> str:
    """убрать 'вариативную' часть wrsp текста"""
    (wrsp_dict, wrsp) = wr
    delta = wrsp_dict['web_reg_name']
    without_delta = wrsp.replace(delta, '').strip()
    return without_delta


def _check_wrsp_duplicate(wr: (dict, str), ) -> bool:
    """проверить, не создан ли ранее, такой же wrsp. True - создан, те дубликат."""
    wrsp = _wrsp_text_delta_remove(wr)
    duplicate = any((wrsp == w) for w in map(_wrsp_text_delta_remove, lr_vars.VarWrspDictList))
    return duplicate


def _all_wrsp_dict_web_reg_save_param(action: 'lr_lib.gui.action.main_action.ActionWindow',
                                      selection: str) -> iter((lr_lib.core.action.web_.WebRegSaveParam,)):
    """все варианты создания web_reg_save_param"""
    try:
        wrsp_and_param = action.web_action.websReport.wrsp_and_param_names
        if selection in wrsp_and_param:  # сменить wrsp-имя в ориг. имя param
            selection = wrsp_and_param[selection]
    except AttributeError as ex:
        pass

    lr_vars.VarParam.set(selection, action=action, set_file=True)
    lr_vars.VarWrspDictList.clear()

    wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()
    param = wrsp_dict['param']

    if wrsp_dict:
        dt = [wrsp_dict, lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict)]
        lr_vars.VarWrspDictList.append(dt)
    else:
        return

    while True:
        try:
            lr_lib.core.var.vars_func.next_3_or_4_if_bad_or_enmpy_lb_rb('поиск всех возможных wrsp_dict')
            wrsp_dict = lr_lib.core.wrsp.param.wrsp_dict_creator()
            if wrsp_dict:
                wr = (wrsp_dict, lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict))
                if _check_wrsp_duplicate(wr):
                    continue
                lr_vars.VarWrspDictList.append(wr)
        except UserWarning:
            break
        except Exception:
            pass
        continue

    len_dl = len(lr_vars.VarWrspDictList)
    fl = list(lr_lib.core.wrsp.param.set_param_in_action_inf(action, param))
    if not fl:
        wrsp_and_param = action.web_action.websReport.wrsp_and_param_names
        if param in wrsp_and_param:  # сменить wrsp-имя в ориг. имя param
            fl = list(lr_lib.core.wrsp.param.set_param_in_action_inf(action, wrsp_and_param[param]))
        else:
            wp = {wrsp_and_param[k]: k for k in wrsp_and_param}
            if param in wp:
                fl = list(lr_lib.core.wrsp.param.set_param_in_action_inf(action, wp[param]))
    if not fl:
        fl = [-1]

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        buttons=['Создать', 'Выйти'],
        text_after='Либо оставить только один web_reg_save_param, удалив остальные.\n'
                   'Либо оставить любое кол-во, при этом, у всех web_reg_save_param сменится имя -\n\t'
                   '- на имя первого создаваемого web_reg_save_param.\n'
                   'Если создание происходит при уже существующем web_reg_save_param, '
                   'сначала он будет удален, затем создан новый.',
        text_before=('"{p}" используется {s} раз, в диапазоне snapshot-номеров [{mi}:{ma}].\n'
                     'Учитывать, что snapshot, в котором создается первый web_reg_save_param, должен быть меньше,\n'
                     'snapshot первого использования "{p}".'.format(
            s=len(fl), p=selection, mi=min(fl), ma=max(fl))),
        is_text='\n\n'.join(w[1] for w in lr_vars.VarWrspDictList),
        title='"{s}":len={l} | Найдено {f} вариантов создания web_reg_save_param.'.format(
            s=selection, l=len(selection), f=len_dl), parent=action,
        default_key='Выйти')
    ask = y.ask()

    if ask == 'Создать':
        action.backup()
        word = 'LAST);'
        text = y.text
        first_only = True  # если создается несколько wrsp_web_
        first_name = ''

        for part in text.split(word):
            part = part.lstrip()
            if not part.rstrip():
                continue

            wrsp = (part + word)
            # брать snapshot из камента
            s = wrsp.split(lr_lib.core.wrsp.param.SnapInComentS, 1)[1]
            s = s.split(lr_lib.core.wrsp.param.SnapInComentE, 1)[0]
            s = s.split(',', 1)[0]  # может быть несколько?
            snap = int(s)

            if first_only:
                action.web_action.web_reg_save_param_remove(selection)  # удалить старый wrsp
            else:
                wrsp = _wrsp_name_replace(wrsp, first_name)

            wrsp_web_ = action.web_action.web_reg_save_param_insert(snap, wrsp)  # сохр wrsp в web

            if first_only:
                action.web_action.replace_bodys([(param, wrsp_web_.name)])  # заменить в телах web's
                first_name = wrsp_web_.name
                first_only = False

            yield wrsp_web_
            continue

        action.web_action_to_tk_text(websReport=True)  # вставить в action.c
        return


def _wrsp_name_replace(web_text: str, new_name: str) -> str:
    """замена имени wrsp, в wrsp тексте"""
    for line in web_text.split('\n'):
        if line.lstrip().startswith(lr_lib.core.wrsp.param.wrsp_lr_start):
            new_line = (lr_lib.core.wrsp.param.wrsp_lr_start + new_name + lr_lib.core.wrsp.param.wrsp_lr_end)
            return web_text.replace(line, new_line)
        continue

    lr_vars.Logger.debug('Ошибка замены имени wrsp "{n}" - не найдена web_reg_save_param линия.\n{t}'.format(
        n=new_name, t=web_text))
    return web_text
