# -*- coding: UTF-8 -*-
# переменная, по типу tkiner.StringVar


def default_callback(value, *args, **kwargs) -> None:
    '''заглушка - пустой callback'''
    pass


class Var:
    '''переменная, по типу tkiner.StringVar, + callback'''
    def __init__(self, value=None, callback_set=default_callback):
        self.default_value = value
        self.value = value
        self.callback_set = callback_set  # выполнить callback при установке

    def set(self, value, *args, callback=True, **kwargs) -> None:
        '''установить'''
        self.value = value
        if callback:
            self.callback_set(value, *args, **kwargs)

    def get(self):
        '''получить'''
        return self.value
