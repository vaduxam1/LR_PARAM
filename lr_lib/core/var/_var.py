# -*- coding: UTF-8 -*-
# Var - вероятно хотел сделать потокобезопасную tkiner.Var(value=any_type) переменную


def default_callback(value, *args, **kwargs) -> None:
    """заглушка - пустой callback"""
    pass


class Var:
    """переменная, по типу tkiner.StringVar, + callback"""
    def __init__(self, value=None, callback_set=default_callback):
        self.value_ = self.default_value = value
        self.callback_set = callback_set  # выполнить callback при установке
        return

    def set(self, value, *args, callback=True, **kwargs) -> None:
        """установить"""
        self.value_ = value
        if callback:
            self.callback_set(value, *args, **kwargs)
        return

    def get(self):
        """получить"""
        return self.value_
