# -*- coding: UTF-8 -*-
# улаление web_ из action.с (dummy и тд)


def dummy_remove(web_: [str, ], mode=False) -> bool:
    '''похожая web_submit_data или нет'''
    if mode == 'endswith':
        return dummy_endswith_remove(web_)
    else:
        return (len(web_) == Dummy.dummy_len) and \
               all(w.lstrip().startswith(d) for w, d in zip(web_, Dummy.web_dummy))


class Dummy:
    '''шаблоны удаления inf-запросов'''
    web_dummy_template = ''
    web_len = 0
    web_dummy = ()
    dummy_len = 0
    dummy_start = ''
    dummy_end = ''

    @staticmethod
    def setattrs(template: str) -> None:
        '''создать Dummy атрибуты, для web_dummy_template'''
        Dummy.web_dummy_template = template.strip()
        Dummy.web_len = len(Dummy.web_dummy_template)
        Dummy.web_dummy = tuple(filter(bool, map(str.strip, Dummy.web_dummy_template.split('\n'))))
        Dummy.dummy_len = len(Dummy.web_dummy)


WebDummyTemplate_1 = '''
web_submit_data("
    "Action=http://
    "Method=POST",
    "RecContentType=text/plain",
    "Referer=http://
    "Snapshot=t
    "Mode=HTML",
    ITEMDATA,
    "Name=dtid", "Value=
    "Name=cmd_0", "Value=dummy", ENDITEM,
    "Name=opt_0", "Value=i", ENDITEM,
LAST);
    '''


WebDummyTemplate_2 = '''
web_submit_data("
    "Action=http://
    "Method=POST",
    "RecContentType=text/plain",
    "Referer=http://
    "Mode=HTML",
    ITEMDATA,
    LAST);
'''


WebDummyTemplate_3 = '''
web_custom_request("
    "URL=http://clients2.google.com 
    "Method=
    "Resource= 
    "RecContentType= 
    "Referer=
    "Snapshot= 
    "Mode= 
    "EncType= 
    "Body=
    "
    " 
    LAST);
'''


WebDummyTemplate_List = [WebDummyTemplate_1, WebDummyTemplate_2, WebDummyTemplate_3]

# проинициализировать
Dummy.setattrs(WebDummyTemplate_1)


WebDummyTemplate_Part_Endswith = '''
  ITEMDATA, 
  "Name=dtid", "Value=
  "Name=cmd_0", "Value=dummy", ENDITEM, 
  "Name=opt_0", "Value=i", ENDITEM, 
  LAST);
'''
WebDummyTemplate_Part_ = tuple(filter(bool, map(str.strip, WebDummyTemplate_Part_Endswith.split('\n'))))


def dummy_endswith_remove(web_: [str, ]) -> bool:
    '''web_submit_data похожая на WebDummyTemplate_Part_, или нет'''
    if (len(web_) > Dummy.dummy_len) and \
            (web_[-1].strip() == WebDummyTemplate_Part_[-1]) and \
            (web_[-2].strip() == WebDummyTemplate_Part_[-2]) and \
            (web_[-3].strip() == WebDummyTemplate_Part_[-3]) and \
            web_[-4].lstrip().startswith(WebDummyTemplate_Part_[-4]) and \
            (web_[-5].strip() == WebDummyTemplate_Part_[-5]):
        return True