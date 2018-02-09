# -*- coding: UTF-8 -*-
# команды из меню мыши - нахождение и замена group_param

import sys
import queue
import contextlib

import lr_lib.gui.etc.gui_other

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param as lr_param
import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.gui.widj.dialog as lr_dialog


@lr_vars.T_POOL_decorator
def group_param(event, widget=None, params=None, ask=True) -> None:
    '''нахождение и замена для группы web_reg_save_param's'''
    if widget is None:
        widget = event.widget

    if params is None:
        params = widget.action.group_param_search(widget.selection_get())
    elif params is False:
        params = widget.action.session_params(lb_list=[widget.selection_get()], ask=False)
    if not params:
        return lr_vars.Logger.warning('param не найдены! %s' % params, parent=widget.action)

    _len_params = len(params)
    if ask:
        y = lr_dialog.YesNoCancel(
            buttons=['Найти', 'Отменить', 'Пропуск'], text_before='найти group param', text_after='%s шт.' % _len_params,
            is_text='\n'.join(params), title='group param', parent=widget.action, default_key='Найти')
        ask = y.ask()
        if ask == 'Найти':
            params = sorted(filter(bool, y.text.split('\n')), key=len, reverse=True)
        elif ask == 'Пропуск':
            params = []
        else:
            return

    len_params = len(params)
    lr_vars.Logger.info('Имеется {l} ранее созданных param.\nДля создания выбрано/найдено {p}/{_p} param.\n'.format(
        _p=_len_params, p=len_params, l=len(widget.action.web_action.websReport.wrsp_and_param_names)))

    def progress(p1=((len_params/100) or 1)) -> None:
        '''прогресс выполнения vars'''
        if wrsp_dict:  # прогресс работы
            lu = len(unsuccess_params)
            widget.action.toolbar['text'] = '{p} : {counter}/{len_params} : {w} %{u}\n{wrsp}'.format(
                counter=counter, len_params=len_params, u=(' | fail: %s' % lu if lu else ''), w=round(counter / p1),
                p=wrsp_dict['param'], wrsp=wrsp)
            widget.action.background_color_set(color=None)  # action цвет по кругу
            widget.action.after(upd, progress)  # перезапуск progress

        else:  # результаты работы
            pl = widget.action.param_counter(all_param_info=False)
            lr_vars.Logger.debug(pl)
            widget.action.toolbar['text'] = pl
            widget.action.set_combo_len()

            if unsuccess_params:
                err = len(unsuccess_params)
                widget.action.toolbar['text'] = '{s}: {e} param не созданы {u}\nсозданы {p} param\n{pl}'.format(
                    s=str(not err).upper(), pl=pl, n=n, e=err, u=(', '.join(unsuccess_params) if err else ''), p=(len_params-err))
                lr_vars.Logger.error('{} param не были обработаны:\n\t{}'.format(
                    err, '\n\t'.join(unsuccess_params)), parent=widget.action)

            if widget.action.final_wnd_var.get():
                lr_lib.gui.etc.gui_other.repA(widget)
            widget.action.background_color_set(color='')  # action оригинальный цвет

    widget.action.backup()
    with lr_vars.Window.block(), widget.action.block():
        lr_vars.Window._block_ = True

        # vars для progress
        counter, wrsp_dict, wrsp, unsuccess_params, upd = 0, {'param': None}, '', [], lr_vars.MainThreadUpdateTime.get()
        widget.action.after(upd, progress)

        # найти и заменить
        for (counter, wrsp_dict, wrsp, unsuccess_params) in _set_group_param(params, widget.action):
            continue  # vars для progress

        lr_vars.Window._block_ = False


def _set_group_param(params: [str, ], action) -> iter((int, dict, str, [str, ]),):
    '''найти и заменить группу web_reg_save_param'''
    wrsp_dicts = queue.Queue()
    unsuccess_params = []  # обработанные с ошибкой
    _thread_wrsp_dict_creator(wrsp_dicts, params, unsuccess_params, action)  # создавать в фоне

    replace_bodys_iter = action.web_action.replace_bodys_iter()
    next(replace_bodys_iter)
    counter = 0
    try:
        for counter, wrsp_dict in enumerate(iter(wrsp_dicts.get, None), start=1):
            wrsp = lr_param.create_web_reg_save_param(wrsp_dict)
            action.web_action.web_reg_save_param_insert(wrsp_dict, wrsp)  # вставить web_reg_save_param

            wrsp_name = lr_param.param_bounds_setter(wrsp_dict['web_reg_name'])
            replace_bodys_iter.send((wrsp_dict['param'], wrsp_name))  # заменить param на web_reg_save_param

            with contextlib.suppress(UserWarning, AssertionError):  # продолжать
                action.param_inf_checker(wrsp_dict, wrsp)  # inf запроса <= inf web_reg_save_param
            yield (counter, wrsp_dict, wrsp, unsuccess_params)  # прогресс
    finally:
        action.web_action_to_tk_text(websReport=True)  # вставить в action.c
        yield (counter, {}, '', unsuccess_params)  # выход прогресс


@lr_vars.T_POOL_decorator
def _thread_wrsp_dict_creator(wrsp_dicts: queue.Queue, params: [str, ], unsuccess_params: [], action) -> None:
    '''создать wrsp_dicts в фоне, чтобы не терять время, при показе popup окон'''
    for param in params:
        try:
            lr_vars.VarParam.set(param, action=action, set_file=True)
            wrsp_dict = lr_vars.VarWrspDict.get()
        except Exception:
            unsuccess_params.append(param)
            lr_excepthook.excepthook(*sys.exc_info())
        else:
            wrsp_dicts.put_nowait(wrsp_dict)

    wrsp_dicts.put_nowait(None)  # stop

