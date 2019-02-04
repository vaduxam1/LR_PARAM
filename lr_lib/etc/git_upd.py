# -*- coding: UTF-8 -*-
# создание главного окна + заблокировать

import threading
import collections
import tkinter.messagebox
import urllib.request

import lr_lib.core.var.vars as lr_vars


def _git_update_check():
    """
    проверить на наличие обновлений
    """
    t = threading.Thread(target=check_git_ver)
    t.start()
    return


def find_git_ver():
    """
    версия утилиты на github.com
    """
    if not lr_vars.githubCheckUpdateEnable:
        return

    with urllib.request.urlopen(lr_vars.GitHub) as f:
        html = f.read()

    html = html.decode('utf-8')
    v = html.split('>VERSION</span>', 1)
    v = v[1].split('\n', 1)
    v = v[0].split('</span>v', 1)
    v = v[1].split('<', 1)

    ver = 'v{0}'.format(v[0])
    return ver


def check_git_ver():
    """
    проверить обновление версии утилиты на github.com
    """
    changes = find_version_changes(lr_vars.VERSION)
    GVER = find_git_ver()
    lr_vars.Logger.info([lr_vars.githubDownloadUrl, GVER, ])
    lr_vars.Logger.info(changes)

    if lr_vars.VERSION != GVER:
        i1 = "Для версии {v} доступно обновление".format(v=lr_vars.VERSION)
        i2 = "По адресу {a} доступно последнее [{v}] обновление утилиты.\n\n{d}".format(
            v=GVER, a=lr_vars.githubDownloadUrl, d=changes,
        )
        tkinter.messagebox.showwarning(i1, i2)
    return


def find_version_changes(ver: str) -> str:
    """
    текст изменений для версии
    """
    current_ver = ver_to_int(ver)
    description = []

    for v in VersionChanges:
        if ver_to_int(v) > current_ver:
            it = [v, VersionChanges[v]]
            description.append(it)
        continue

    text = '\n'.join(' [ {} ]:{}'.format(k, v) for (k, v) in description)
    return text


def ver_to_int(ver: str) -> (int,):
    """
    привести к [int, ], чтобы сравнивать
    :param ver: str: "v11.5.4"
    :return: (int, ): [11, 5, 4]
    """
    v = ver[1:].split('.')
    vint = tuple(map(int, v))
    return vint


VersionChanges = collections.OrderedDict({
    'v11.5.5': '''
* неверно работал "Поиск WRSP на основе регулярных выражений" №2, если при работе было выведено диалог окно
* неверно работал "Поиск по началу имени - взять n первых символов" №5 - не использовались уже созданные param
* нумерация в меню "Найти и Создать WRSP", и в самих методах различалась - исправлены описания методов
* общий рефакторинг
    ''',

    'v11.5.4': '''
* добавлен WARNING: Неправильное использование WRSP: value={P_3874_1__Tree__bJsPc0}_1"
* в методе "LAST: по lb известных" - для увеличения вариантов поиска param, добавлены новые источники lb
* добавлены подсказки к кнопкам меню "Setting" из каментов исходного кода
* не закрывать диалог окно, при отмене нажатия "Создать"
* добавлено описание изменений, для новых версий утилиты
* общий рефакторинг
        ''',

    'v11.5.3': '''
* добавлено меню: "Setting" - настройка var
* добавлено меню: "Удалить все созданные WRSP"
* добавлены настройки поиска, для меню "Найти и Создать WRSP"
* удаление уже созданных WRSP, из результатов поиска меню "Найти и Создать WRSP"
* toolTip снижен до 2 сек, добавлена задержка перед стартом
* исправления для совместимости с win2k3
* общий рефакторинг
        ''',

    'v11.5': '''
* новая система поиска WRSP в action.c и других файлах - 6 способов
* реакция гирляндой(циклическая смена цвета кнопок), на действия пользователя
        ''',

})
