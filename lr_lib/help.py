# -*- coding: UTF-8 -*-
# тексты хелпа, и т.д.

import os


_HELP = '''
Скрипт предназначен для:
    Поиска param в файлах LoadRunner-скрипта: шаг ввод(1)-поиск(2)
    Определения места положения(номера вхождения) param в файле: шаг комбобокс(3)-комбобокс(4)
    Определения и изменения LB/RB: шаг редактирование(5)
    Определения Ord с учетом редактирования LB/RB(5): шаг редактирование(5)-формирование(6)
    Формирования LoadRunner web_reg_save_param с экранированием символов: шаг формирование(6)

Основные элементы управления:      
     (1) - поле ввода param
     (2) - кнопка поиска param
     (3) - комбобокс выбора файла c param
     (4) - комбобокс выбора номера вхождения param в файл
     (5) - поля для вывода/редактирования LB/RB
     (6) - кнопка получения web_reg_save_param

Термины:
    param - (1) искомый параметр из LoadRunner, для поиска(2) его в файлах LoadRunner-скрипта
    "номер вхождения param" - число, меньше или равное числу, сколько раз param(1) встретился в файле(3)
    LB - (5) определенное кол-во символов слева от ...param в файле(3)
    RB - (5) определенное кол-во символов справа от param... в файле(3)
    Ord - номер вхождения строк LB/RB(5) в файл(3), при котором между ними будет искомый param(1)
    web_reg_save_param - (6) итововый результат для вставки в LoadRunner-тест

Описание:
    Следует выбрать кодировку(главное_меню/Select Encode) файлов, ту же, что и кодировка в LoadRunner.
    A) Где происходит поиск(2) param(1):
        При старте, из каталога "data" или текуцей директории(копка смены директории), формируется AllFiles список файлов, где будет происходить поиск param(1).
        Формирование AllFiles, чекбоксами[Определить Файлы, для поиска(2)], происходит двумя способами:
         a) Только файлы, прописанные в t*.inf файлах каталога LoadRunner-скрипта, каждому файлу соответствует определенный inf-номер.
            Файлы берутся из inf-ключей, прописанных в defaults.FileOptionsStartswith.
            inf-номер - это номер("Snapshot=t43.inf") бкока запроса в LoadRunner-скрипте, перед которым нужно вставлять web_reg_save_param.
            inf-номерами можно ограничить диапазон поиска файлов.
         b) Все файлы каталога, у всех файлов inf-номер=0.
            Номер("Snapshot=t43.inf") бкока запроса в LoadRunner-скрипте, перед которым нужно вставлять web_reg_save_param, Не определяется, определять вручную, по имени файла.
        Часть файлов дополнительно отфильтруется(чекбокс "споск исключения deny_"), тк находятся в списке исключения файлов - расширения(gif, zip,..) и тд.
        Для каждого файла создается dict, в который сохраняется инфо о размере, кол-ве символов и др. [чекбокс Статистика файлов] 
    B) Результат поиска(2) param(1):
        Формируется FilesWithParam список файлов, в которых param(1) был найден.
         a) Список найденых файлов записывается в комбобокс(3), выбирается один из файлов(3) (чекбокс "last"), происходит чтение файла(3).
         b) Кол-во вхождений param в файл, записывается в комбобокс(4) в виде списка [0, 1, n],  выбирается одно из вхождений(4).
         c) В полях LB/RB(5) отображается текст из "частей", слева/справа от номера вхождения(4) param(1), в файл(3)
    С) Пользователь меняет(при необходимости):
         a) Файл(3) - происходит заполнение комбобокса(4). Комбобокс файлы(3) можно сортировать sortKey комбобоксами, значения ключей для выбора, можно увидеть в toolTip файла(3), после поиска(2).
         b) Вхождение(4) - происходит подтягивание LB/RB(5), с учетом всех виджетов модификаторов LB/RB.
         c) Редактирует поля LB/RB(5) - тк в поле может попасть "вариативный" параметр, нежелательные спец символы, и тд.
            После редактирования полей, может изменится Ord для web_reg_save_param, что будет учтено в (6).
    D) При формировании web_reg_save_param(6) результата:
        Текст файла(3) "разбивается на части", по LB(5)
        В списке "частей", происходит поиск RB(5)
        Если "часть" содержит RB(5) - увеличить Ord
        Если "часть" начинается на 'param(1) + RB(5)' - Ord найден
        Печатные символы искомого param(1), войдут в имя для web_reg_save_param
        Будут экранированы символы: '\\', '"'
        В коментарии собрана статистика по LB/RB(5), inf, файл(3), param(1)
        Результат выведен в Window.Text/блокнот/буфер_обмена/консоль/лог 
                    + при использовании action.c окна: action.c/backup_action.c
'''


WORK = '''Работа с программой, без чекбокса auto:
   (1) Ввести искомый параметр в "поле ввода {param}".
   (2) Нажать кнопку "поиск {param} файлов".
          a) "список файлов", содержащих param, записан в комбобокс(3).
             в комбобокс(3) выбран "файл" из списка.
          b) "список номеров", вхождения param в файл(3), записан в комбобокс(4).
             в комбобокс(4) выбрано "вхождение".
          c) в полях LB/RB(5) будет отображен текст, с учетом (1)-(5).
   (3) При необходимости выбрать из комбобокс(3) другой "файл с param".
          переход в 2.b)-2.c)
   (4) При необходимости выбрать из комбобокс(4) другое "вхождение param".
          переход в 2.c)
   (5) При необходимости редактировать "поля LB/RB"
   (6) Нажать кнопку "web_reg_save_param".
        Вывод web_reg_save_param с учетом (3)-(5)
'''


ADD = '''Дополнительно:
  + При чекбокс auto=On, шаги (3)-(6) выполняются автоматически, после поиска(2).
  + web_reg_save_param может быть найден, из меню правой кнопки мыши - произойдет поиск(2):
        1) в любом месте программы(например кнопка action), выделить текст(это будет param).
        2) нажать на выделении, правую кнопки мыши / param
  + web_reg_save_param можно получить в фоне(при свернутом окне) - произойдет поиск(2):
    Необходимо установить библиотеку keyboard - cmd: 1)cd c:\Python36\Scripts\ 2)pip install keyboard
        1) искомый param(1) должен находится в буфере обмена.
        2) Нажать "глобальный" хоткей 'ctrl+shift+c'
  + Можно использовать в консоли - произойдет поиск(2): cmd("LR_7.py -h")
  ^ web_reg_save_param открывается в Блокноте (чекбокс notepad), после поиска(2).
  ^ web_reg_save_param копируется в буфер обмена (чекбокс clipboard), после поиска(2).
  
!! Если не работает (буфер обмена, меню пр.кнопки мыши и др) - поменять раскладку клавиатуры на ENG !!!
'''


ACTION1 = '''Кнопка PARAM - аналог нескольких web_reg_save_param/Группа.
    a) При необходимости, в открывшемся диалоге, ввести с новой строки, начала имен параметров
    b) При необходимости, в открывшемся диалоге, test
    c) В открывшемся диалоге, дабавить/удалить найденные param-имена(имя которых начинается на a) b))
Результат: Для каждого найденного param, создан одиночный web_reg_save_param с заменой и подсветкой 

web_reg_save_param/Группа - аналог нескольких web_reg_save_param/Одиночный:
    a) вручную, в тексте, найти и Выделить, начало имени param, те "zkau_" для "zkau_11"
    b) нажать Правой кнопкой мыши на web_reg_save_param / группа
Результат: Для каждого найденного param, создан одиночный web_reg_save_param с заменой и подсветкой 

web_reg_save_param/Одиночный:
    a) вручную, в тексте, найти и Выделить, param для замены
    b) нажать Правой кнопкой мыши на web_reg_save_param / одиночный с заменой и подсветкой
  Результат [Р]:
    1) в главном окне, произведен поиск param и сформирован web_reg_save_param
    2) сделан бекап action.c текста
    3) param, в тексте action.c окна, заменен на имя_{web_reg_save_param}
    4) web_reg_save_param записан в action.c текст, перед соответствующему ему inf-запросу
    5) param и имя_{web_reg_save_param}, в тексте подсвечены цветом
    6) param и имя_{web_reg_save_param} установлены и сохранены в историю виджетов 
    7) в action.c, показано окно релультатов замены, пока открыто, отображен созданный web_reg_save_param.
        после заерытия окна, выполнен переход, на первый замененный param.
    8) в меню правой кнопкой мыши добавлен пункт "Быстрый перход"

Автозамена - спосить, при неопределенности, является ли заменяемое слово, именем текущего param(те заменить), 
 или не является(не заменять). Те если cимвол, слева или справа, от заменяемого текста: Буква, Цифра, или "_!-"'''


ACTION2 = '''Меню правой кнопкой мыши:
    * "web_reg_save_param" / 
       + с заменой и подсветкой - Результат [Р]: 1), 2), 3), 4), 5), 6), 7), 8)
       + с заменой - Результат [Р]: 1), 2), 3), 4), 6), 7), 8)
       + с подсветкой - Результат [Р]: 1), 5), 6)
       + только тоиск - Результат [Р]: 1), 6)
       + переформатировать LB/RB - Описание : Например в LB/RB попал session_id. 
                Недостаточно просто удалить нежелательные символы из "LB= "RB= в web_reg_save_param, 
                тк при этом может изменится "Ord=. Тк имя_{web_reg_save_param} в action.c тексте уже заменено, 
                формирование нового "правильного" web_reg_save_param так или иначе связано с трудностями.
            Работа: в action.c тексте, в блоке "неправильного" сформированного web_reg_save_param, в полях LB и RB
                1) раз-экранировать символы (актуально, если между "~" разные цифры: // LB[19~22](0), RB[25~25])
                2) удалить лишние(session_id) символы в полях LB и RB
                3) выделить весь блок web_reg_save_param(с комментариями)
                4) нажать правой кнопкой мыши web_reg_save_param / переформатировать LB/RB
            Результат:
                1) старый блок web_reg_save_param, заменен новым
                2) имя_{web_reg_save_param} осталось прежним
                3) сформирован новый "Ord=, с учетом отредактированных "LB= "RB=
    * "поиск" '"201.33+2c" - [Строка].[Столбец]+[ДлинаСлова]c
    * Быстрый перход - для перехода к сформированному web_reg_save_param, или первому замененному param
    * Inf-min/max - выбрать из выделенного текста только цифры, установить полученным значением inf_min/max виждет
    * Подсветка - для выделенного текста, добавить/удалить подсветку в action.c тексте'''


ACTION3= '''Поиск текста:
    1) ввести текст в search_entry
    2) нажать кнопку search_button
   Результат - заполнение, списком координат, search_res_combo(комбобокс результатов поиска)
        up_search_button - перейти вверх, по результатам поиска
        down_search_button - перейти вниз, по результатам поиска
        прокрутка колеса мыши на комбобоксе - быстрый переход между областями
        внучную выбрать из комбобокса координаты
        вручную ввести координаты в формате Строка.Столбец: 201.33 - Enter
Замена текста:
    1) ввести в SearchReplace_searchCombo, искомый текст для замены
    2) ввести в SearchReplace_replaceCombo текст, на который заменить
    3) нажать SearchReplace_button - Найти и Заменить
  Результат:
    в action.c, искомый текст, заменен на новый: 
        Если cимвол, слева или справа, от заменяемого текста: Буква, Цифра, или "_!-"
            Вывести диалог окно, c заменяемой строкой, и вропросом о замене.
            По умолчанию, отвечать "Нет для всех", тк подойдет в большинстве случаев.'''


CODE = '''Соответствие defaults.Var's с шагами : | <<(на этом шаге используются Vars.get()) | [=> соответствующий gui виджет]
    LR_7.py -> files.createAllFiles() | <<(VarFilesFolder, VarIsInfFiles, VarAllowDenyFiles, VarEncode, VarAllFilesStatistic, FileOptionsStartswith, DENY_FILES, DENY_PART_NAMES, DENY_EXT)
        |
  AllFiles[..] | <<(VarFileSortKey1/2) | [=> Window.folder_wind]
        |
(1) # ввод param | [=> Window.comboParam]
        |
(2) VarParam.set  # поиск param | <<(Window.cbxWrspAutoCreate) | [=> Window.ButtonFindParamFiles]
        | <- param.create_files_with_search_data()
  param.get_files_with_param() | <<(VarSearchMinInf, VarSearchMaxInf, VarEncode, VarFileNamesNumsShow)
        |
    FilesWithParam[..]  |ред|-->  | <<(VarFileSortKey1/2) | [=> Window.comboFiles]
        |
(3) VarFileName.set  <--|ред|-->  | <<(VarFirstLastFile) |  [=> Window.comboFiles]
        |
    VarFile.set
        |
    VarFileText.set  <<(VarEncode, ~VarAllFilesStatistic~)
        |
(4) VarPartNum.set  <--|ред|  [=> Window.comboParts]
        |
(5) VarLB.set / VarRB.set  <--|ред|-->  <<(VarReturn, VarRus, VarMaxLen, VarUnicode, VarSplitList, VarPartNumEmptyNext, VarPartNumDenyNext, allow_symbols) | [=> Window.LB/RB]
        | <- param.wrsp_dict_creator()
(3-5) # редактирование -->|ред|<--
        | <- param.wrsp_dict_creator() <- param.find_param_ord()
(6) param.create_web_reg_save_param()  <<(Window.cbxClearShowVar) | [=> Window.ButtonShowParam]
        |
   param.web_reg_save_param # результат  <<(Window.cbxNotepadWrsp, Window.cbxWrspClipboard) | [=> Window.text]'''


HELP = '\n'.join([_HELP, WORK, ADD, ACTION1, ACTION2, ACTION3])

COLORS = {
  "aliceblue": "#f0f8ff",
  "antiquewhite": "#faebd7",
  "aqua": "#00ffff",
  "aquamarine": "#7fffd4",
  "azure": "#f0ffff",
  "beige": "#f5f5dc",
  "bisque": "#ffe4c4",
  "black": "#000000",
  "blanchedalmond": "#ffebcd",
  "blue": "#0000ff",
  "blueviolet": "#8a2be2",
  "brown": "#a52a2a",
  "burlywood": "#deb887",
  "cadetblue": "#5f9ea0",
  "chartreuse": "#7fff00",
  "chocolate": "#d2691e",
  "coral": "#ff7f50",
  "cornflowerblue": "#6495ed",
  "cornsilk": "#fff8dc",
  "crimson": "#dc143c",
  "cyan": "#00ffff",
  "darkblue": "#00008b",
  "darkcyan": "#008b8b",
  "darkgoldenrod": "#b8860b",
  "darkgray": "#a9a9a9",
  "darkgreen": "#006400",
  "darkgrey": "#a9a9a9",
  "darkkhaki": "#bdb76b",
  "darkmagenta": "#8b008b",
  "darkolivegreen": "#556b2f",
  "darkorange": "#ff8c00",
  "darkorchid": "#9932cc",
  "darkred": "#8b0000",
  "darksalmon": "#e9967a",
  "darkseagreen": "#8fbc8f",
  "darkslateblue": "#483d8b",
  "darkslategray": "#2f4f4f",
  "darkslategrey": "#2f4f4f",
  "darkturquoise": "#00ced1",
  "darkviolet": "#9400d3",
  "deeppink": "#ff1493",
  "deepskyblue": "#00bfff",
  "dimgray": "#696969",
  "dimgrey": "#696969",
  "dodgerblue": "#1e90ff",
  "firebrick": "#b22222",
  "floralwhite": "#fffaf0",
  "forestgreen": "#228b22",
  "fuchsia": "#ff00ff",
  "gainsboro": "#dcdcdc",
  "ghostwhite": "#f8f8ff",
  "gold": "#ffd700",
  "goldenrod": "#daa520",
  "gray": "#808080",
  "green": "#008000",
  "greenyellow": "#adff2f",
  "grey": "#808080",
  "honeydew": "#f0fff0",
  "hotpink": "#ff69b4",
  "indianred": "#cd5c5c",
  "indigo": "#4b0082",
  "ivory": "#fffff0",
  "khaki": "#f0e68c",
  "lavender": "#e6e6fa",
  "lavenderblush": "#fff0f5",
  "lawngreen": "#7cfc00",
  "lemonchiffon": "#fffacd",
  "lightblue": "#add8e6",
  "lightcoral": "#f08080",
  "lightcyan": "#e0ffff",
  "lightgoldenrodyellow": "#fafad2",
  "lightgray": "#d3d3d3",
  "lightgreen": "#90ee90",
  "lightgrey": "#d3d3d3",
  "lightpink": "#ffb6c1",
  "lightsalmon": "#ffa07a",
  "lightseagreen": "#20b2aa",
  "lightskyblue": "#87cefa",
  "lightslategray": "#778899",
  "lightslategrey": "#778899",
  "lightsteelblue": "#b0c4de",
  "lightyellow": "#ffffe0",
  "lime": "#00ff00",
  "limegreen": "#32cd32",
  "linen": "#faf0e6",
  "magenta": "#ff00ff",
  "maroon": "#800000",
  "mediumaquamarine": "#66cdaa",
  "mediumblue": "#0000cd",
  "mediumorchid": "#ba55d3",
  "mediumpurple": "#9370db",
  "mediumseagreen": "#3cb371",
  "mediumslateblue": "#7b68ee",
  "mediumspringgreen": "#00fa9a",
  "mediumturquoise": "#48d1cc",
  "mediumvioletred": "#c71585",
  "midnightblue": "#191970",
  "mintcream": "#f5fffa",
  "mistyrose": "#ffe4e1",
  "moccasin": "#ffe4b5",
  "navajowhite": "#ffdead",
  "navy": "#000080",
  "oldlace": "#fdf5e6",
  "olive": "#808000",
  "olivedrab": "#6b8e23",
  "orange": "#ffa500",
  "orangered": "#ff4500",
  "orchid": "#da70d6",
  "palegoldenrod": "#eee8aa",
  "palegreen": "#98fb98",
  "paleturquoise": "#afeeee",
  "palevioletred": "#db7093",
  "papayawhip": "#ffefd5",
  "peachpuff": "#ffdab9",
  "peru": "#cd853f",
  "pink": "#ffc0cb",
  "plum": "#dda0dd",
  "powderblue": "#b0e0e6",
  "purple": "#800080",
  "red": "#ff0000",
  "rosybrown": "#bc8f8f",
  "royalblue": "#4169e1",
  "saddlebrown": "#8b4513",
  "salmon": "#fa8072",
  "sandybrown": "#f4a460",
  "seagreen": "#2e8b57",
  "seashell": "#fff5ee",
  "sienna": "#a0522d",
  "silver": "#c0c0c0",
  "skyblue": "#87ceeb",
  "slateblue": "#6a5acd",
  "slategray": "#708090",
  "slategrey": "#708090",
  "snow": "#fffafa",
  "springgreen": "#00ff7f",
  "steelblue": "#4682b4",
  "tan": "#d2b48c",
  "teal": "#008080",
  "thistle": "#d8bfd8",
  "tomato": "#ff6347",
  "turquoise": "#40e0d0",
  "violet": "#ee82ee",
  "wheat": "#f5deb3",
  "white": "#ffffff",
  "whitesmoke": "#f5f5f5",
  "yellow": "#ffff00",
  "yellowgreen": "#9acd32"
}

HEX = {
    '%00', '%01', '%02', '%03', '%04', '%05', '%06', '%07', '%08', '%09', '%0A', '%0B', '%0C', '%0D', '%0E', '%0F',
    '%10', '%11', '%12', '%13', '%14', '%15', '%16', '%17', '%18', '%19', '%1A', '%1B', '%1C', '%1D', '%1E', '%1F',
    '%20', '%21', '%22', '%23', '%24', '%25', '%26', '%27', '%28', '%29', '%2A', '%2B', '%2C', '%2D', '%2E', '%2F',
    '%30', '%31', '%32', '%33', '%34', '%35', '%36', '%37', '%38', '%39', '%3A', '%3B', '%3C', '%3D', '%3E', '%3F',
    '%40', '%41', '%42', '%43', '%44', '%45', '%46', '%47', '%48', '%49', '%4A', '%4B', '%4C', '%4D', '%4E', '%4F',
    '%50', '%51', '%52', '%53', '%54', '%55', '%56', '%57', '%58', '%59', '%5A', '%5B', '%5C', '%5D', '%5E', '%5F',
    '%60', '%61', '%62', '%63', '%64', '%65', '%66', '%67', '%68', '%69', '%6A', '%6B', '%6C', '%6D', '%6E', '%6F',
    '%70', '%71', '%72', '%73', '%74', '%75', '%76', '%77', '%78', '%79', '%7A', '%7B', '%7C', '%7D', '%7E', '%7F',
    '%80', '%81', '%82', '%83', '%84', '%85', '%86', '%87', '%88', '%89', '%8A', '%8B', '%8C', '%8D', '%8E', '%8F',
    '%90', '%91', '%92', '%93', '%94', '%95', '%96', '%97', '%98', '%99', '%9A', '%9B', '%9C', '%9D', '%9E', '%9F',
    '%A0', '%A1', '%A2', '%A3', '%A4', '%A5', '%A6', '%A7', '%A8', '%A9', '%AA', '%AB', '%AC', '%AD', '%AE', '%AF',
    '%B0', '%B1', '%B2', '%B3', '%B4', '%B5', '%B6', '%B7', '%B8', '%B9', '%BA', '%BB', '%BC', '%BD', '%BE', '%BF',
    '%C0', '%C1', '%C2', '%C3', '%C4', '%C5', '%C6', '%C7', '%C8', '%C9', '%CA', '%CB', '%CC', '%CD', '%CE', '%CF',
    '%D0', '%D1', '%D2', '%D3', '%D4', '%D5', '%D6', '%D7', '%D8', '%D9', '%DA', '%DB', '%DC', '%DD', '%DE', '%DF',
    '%E0', '%E1', '%E2', '%E3', '%E4', '%E5', '%E6', '%E7', '%E8', '%E9', '%EA', '%EB', '%EC', '%ED', '%EE', '%EF',
    '%F0', '%F1', '%F2', '%F3', '%F4', '%F5', '%F6', '%F7', '%F8', '%F9', '%FA', '%FB', '%FC', '%FD', '%FE', '%FF'
}
