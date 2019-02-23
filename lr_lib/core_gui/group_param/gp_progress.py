# -*- coding: UTF-8 -*-
# progressbar нахождения и замены group_param

import lr_lib.gui.etc.color_change
from lr_lib.core.var import vars as lr_vars
from typing import Iterable, Tuple, List, Callable

progress_str = '{proc}% : {counter}/{len_params} | fail={fail}\n{wrsp}'
final_str = '{state} | создано сейчас = {param} / fail={fail} : {unsuc} | всего {param_counter}'


class ProgressBar:
    """
    рекурсивный асинхронный progressbar
    """

    def __init__(self, len_params: int, widget):
        self.widget = widget
        self.len_params = len_params
        self.p1 = ((self.len_params / 100) or 1)

        p = {'param': ''}
        item = (0, p, '', [], )
        self.item0 = [item, ]  # [(counter, wrsp_dict, wrsp, unsuccess)]
        return

    def __enter__(self) -> 'ProgressBar':
        """
        старт
        """
        self.widget.action.show_hide_bar_1(force_show=True)
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Tuple:
        """
        стоп
        """
        self.stop()
        self.widget.action.show_hide_bar_1()
        item = (exc_type, exc_val, exc_tb)
        return item

    def update(self, item: Tuple[int, dict, str, list]) -> None:
        """
        добавить данные для progressbar
        """
        self.item0[:] = [item]
        return

    def start(self) -> None:
        """
        рекурсивный асинхронный progressbar
        """
        lr_vars.MainThreadUpdater.submit(self._start)
        return

    def _start(self) -> None:
        """
        рекурсивный асинхронный progressbar
        """
        (counter, wrsp_dict, wrsp, unsuccess) = self.item0[0]
        fail = len(unsuccess)

        if wrsp_dict:  # прогресс работы
            i = progress_str.format(
                counter=counter,
                len_params=self.len_params,
                fail=fail,
                proc=round(counter / self.p1),
                wrsp=wrsp,
            )
            self.widget.action.toolbar['text'] = i
            # action цвет по кругу
            lr_lib.gui.etc.color_change.background_color_set(self.widget.action, color=None)
            # перезапуск с задержкой
            lr_vars.T_POOL.submit(self.start)
            return

        else:  # выход - результаты работы
            param_counter = self.widget.action.param_counter(all_param_info=False)
            t = final_str.format(
                state=str(not fail).upper(),
                param_counter=param_counter,
                fail=fail,
                unsuc=(', '.join(unsuccess) if fail else ''),
                param=(self.len_params - fail),
            )
            self.widget.action.toolbar['text'] = t

            if unsuccess:
                i = '{} param не были обработаны:\n\t{}'.format(fail, '\n\t'.join(unsuccess))
                lr_vars.Logger.error(i, parent=self.widget.action)

            lr_lib.gui.etc.color_change.background_color_set(self.widget.action, color='')  # action оригинальный цвет
            self.widget.action.set_combo_len()
            lr_vars.Logger.debug(param_counter)

            if self.widget.action.final_wnd_var.get():
                self.widget.action.legend()
        return

    def stop(self) -> None:
        """
        выход self.start
        """
        item = self.item0[0]
        item = list(item)
        item[1] = None  # выход
        self.item0[:] = [item]
        return
