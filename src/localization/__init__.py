from localization.rus import LangRussian
from localization.eng import LangEnglish
from typing import Union


languages = (LangRussian, LangEnglish)
language_instances = {lang.KEY: lang() for lang in languages}
default_language_instance = language_instances[LangRussian.KEY]


def get_localization(lang_name) -> Union[languages]:
    return language_instances.get(lang_name, default_language_instance)
