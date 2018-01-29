# -*- coding: UTF-8 -*-
# action.c транзакции

import collections

import lr_lib.core.var.vars as lr_vars


class Transactions:
    '''объект хранящий иерархию "транзакций" в action.c'''
    _no_transaction_name = 'NoTransaction_'

    def __init__(self, parent):
        self.parent = parent
        self.names = []  # порядок следования имен
        self.start_stop = dict(start=[], stop=[])
        self.sub_transaction = collections.OrderedDict()  # иерархия
        self._no_transaction_num = 0
        self.__is_no_transaction_name = ''

    def __no_transaction_name(self) -> str:
        '''если нет имени транзакции'''
        self._no_transaction_num += 1
        name = '{a}{u}'.format(a=self._no_transaction_name, u=self._no_transaction_num)
        self.start_transaction(name)
        self.__is_no_transaction_name = name
        return name

    def _current(self) -> str:
        '''для определения где находится web, во время разбора action.c текста'''
        for n in reversed(self.names):
            if n not in self.start_stop['stop']:
                return n
        return self.__no_transaction_name()

    def start_transaction(self, transaction: str) -> None:
        if self.__is_no_transaction_name:
            self.stop_transaction(self.__is_no_transaction_name)
            self.__is_no_transaction_name = ''

        if transaction in self.names:
            lr_vars.Logger.error(
                'транзакция: start после start\nПовторное использование start_transaction("{}")'.format(transaction))
        else:
            dt = self.sub_transaction
            for t in self.names:
                if t not in self.start_stop['stop']:
                    dt = dt[t]
            dt[transaction] = collections.OrderedDict()

            self.names.append(transaction)
            self.start_stop['start'].append(transaction)

    def stop_transaction(self, transaction: str) -> None:
        if transaction not in self.names:
            lr_vars.Logger.error(
                'транзакция: stop перед start\nОтсутствует start_transaction("{}")'.format(transaction))
        else:
            self.start_stop['stop'].append(transaction)
