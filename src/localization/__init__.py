from localization.rus import LangRussian
from localization.eng import LangEnglish
from typing import Union


class LangDummy:
    KEY = 'dummy'
    def __getattr__(self, item):
        return item


languages = (LangRussian, LangEnglish, LangDummy)
language_instances = {lang.KEY: lang() for lang in languages}


def get_localization(lang_name) -> Union[languages]:
    return language_instances.get(lang_name,
                                  language_instances[LangDummy.KEY])
