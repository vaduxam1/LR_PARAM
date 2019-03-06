# -*- coding: UTF-8 -*-
# проверить обновление версии утилиты на github.com

import collections
import threading
import tkinter.messagebox
import urllib.request
from typing import Tuple

import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.excepthook


def git_update_check() -> None:
    """
    проверить на наличие обновлений
    """
    try:
        t = threading.Thread(target=check_git_ver)
        t.start()  # threading чтобы не блокировать gui
    except Exception as ex:
        lr_lib.etc.excepthook.excepthook(ex)
    finally:  # не threading.Timer, тк главный поток не закончит работу при выходе, до окончания Timer future
        lr_vars.Tk.after(lr_vars.GitUpdPeriod, git_update_check)  # перезапуск
    return


def check_git_ver() -> None:
    """
    проверить обновление версии утилиты на github.com
    """
    git_version = find_git_ver()
    if (not git_version) or (git_version == lr_vars.VERSION):
        return

    version_changes = find_version_changes(lr_vars.VERSION)

    _t = "Для версии {version} доступно обновление."
    _s = "По адресу {url} доступно последнее {git_version} обновление утилиты.\n{version_changes}"
    ttl = _t.format(version=lr_vars.VERSION, )
    msg = _s.format(url=lr_vars.githubDownloadUrl, git_version=git_version, version_changes=version_changes, )
    m = '{t}\n\n{m}'.format(t=ttl, m=msg, )

    lr_vars.Logger.info(m)
    tkinter.messagebox.showwarning(ttl, msg)
    return


def find_git_ver() -> str:
    """
    версия утилиты на github.com
    """
    if not lr_vars.githubCheckUpdateEnable:
        return ''

    with urllib.request.urlopen(lr_vars.GitHub) as f:
        v_text = f.read()

    v_text = v_text.decode('utf-8')
    v = v_text.split('>VERSION</span>', 1)
    v = v[1].split('\n', 1)
    v = v[0].split('</span>v', 1)
    v = v[1].split('<', 1)

    vn = 'v{num}'  # формат версии утилиты
    git_version = vn.format(num=v[0], )
    return git_version


def find_version_changes(ver: str) -> str:
    """
    текст изменений для версии
    """
    current_ver = ver_to_int(ver)
    description = []

    with urllib.request.urlopen(lr_vars.GitHub2) as f:
        ch_text = f.read()

    ch_text = ch_text.decode('utf-8')
    ch_changes = ch_text.rsplit(VName, 1)
    if len(ch_changes) != 2:
        e = 'описание изменений для версии не определено!'
        return e

    ch_changes = ch_changes[1].split('=', 1)
    changes = ch_changes[1]
    try:
        version_changes = eval(changes)
    except Exception as ex:
        er = 'ошибка определения описания изменений для версии!\n{e}\n{ea}'
        text = er.format(e=ex.__class__.__name__, ea=ex.args, )
        return text

    for ver_num in version_changes:
        new_ver = ver_to_int(ver_num)
        if new_ver > current_ver:
            changes = version_changes[ver_num]
            it = [ver_num, changes]
            description.append(it)
        else:
            break
        continue

    if description:
        t = '{s} {ver} {s}\n{desc}'
        s = ('_' * 3)
        abd = lambda d: '\n'.join(' {0}) {1}'.format(a, b) for (a, b) in enumerate(
            (filter(bool, map(str.strip, d.split(V_SEP)))), start=1))
        text = '\n'.join(t.format(ver=v, desc=abd(d), s=s, ) for (v, d) in description)
    else:
        text = 'описание изменений для версии не задано!'
    return text


def ver_to_int(ver: str) -> Tuple[int, ]:
    """
    привести к [int, ], чтобы сравнивать
    :param ver: str: "v11.5.4"
    :return: (int, ): (11, 5, 4)
    """
    v = ver[1:].split('.')
    vint = tuple(map(int, v))
    return vint


VName = 'VersionChanges'  # одноименно с переменной ниже
# должно располагатся в конце файла, для find_version_changes()
VersionChanges = collections.OrderedDict({

#     'v11.6.5': '''
# * добавить whl для библиотеки keyboard - найти param из буфера обмена
# * lr_start.cmd - изменены условия проверки установлен ли python
#     ''',

    'v11.6.4': '''
* утилита стала "portable" - добавлен запускающий файл lr_start.cmd - если python не установлен, произойдет автоустановка python 3.4.4
* можно использовать сторонние библиотеки, произойдет автоустановка офлайн whl файлов из каталога lr_lib\whl\install
* исправления совместимости с win2k3
    ''',

    'v11.6.3': '''
* в меню правой кнопки мыши, добавлен "Переход по тексту" action.c, по именам transaction/web_reg_save_param/Snapshot/WARNING/...
    ''',

    'v11.6.2': '''
* показать "тип" линии, рядом с номером, в action.c
* в action.c и при перекодировке из base64, не выводился текст содержащий не-ascii/unicode символы
* общий рефакторинг
        ''',

    'v11.6.1': '''
* не работал ctrl-z/ctrl-y
* добавлено декодирование из base64, для контекстного меню мыши "Encodinc"
* многие команды меню правой кнопки мыши, корректно работали только в action.c окне, теперь работает для всех виджетов
* изменены описания диалог окон действий, исправлено поведение tooltip, исправлено меню удалить цвет, другие мелкие фиксы
* общий рефакторинг, аннотации в "правильном" формате
        ''',

    'v11.6.0': '''
* добавлена настройка максимальной разрешенной длины {param} = 99 символов
* удаление "мусора" - не {param} слов, из результатов поиска "Найти и Создать WRSP"
* по умолчанию, методы поиска "Найти и Создать WRSP" №(2, 4, 6) теперь отключены
        ''',

    'v11.5.9': '''
* в меню добавлен новый метод удаления web "Remove dummy NEW"
        ''',

    'v11.5.8': '''
* из скриптов на 190, добавлены новые "не-param слова", для фильтрации param от лишних слов, при поиске всех param
* добавлен чекбокс запрещающий фильтрацию param, при поиске всех param, тк теоритически может отфильтровать лишнего
* неправильно работал чекбокс минимальной длины param: -= 1 ненужен
        ''',
    'v11.5.7': '''
* не работал показ изменений для обновленной версии, при проверке наличия обновления утилиты - теперь текст изменений загружается из github
        ''',

    'v11.5.6': '''
* неверно работал "Поиск WRSP" №5 и №6, если он производился кнопкой "Запуск" из меню "Найти и Создать WRSP" - не использовались, найденные перед этим другими способоми, но еще не созданные param
        ''',

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

})  # "\n*" - признак отдельного пункта изменений в версии - это строка для enumerate, изпользовать в описании нельзя

V_SEP = '\n*'  # "\n*" - признак отдельного пункта изменений в версии
