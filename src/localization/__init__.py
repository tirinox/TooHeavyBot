from localization.rus import LangRussian
from localization.eng import LangEnglish


languages = (LangRussian, LangEnglish)
language_instances = {lang.KEY: lang() for lang in languages}
default_language_instance = language_instances[LangRussian.KEY]


def get_localization(lang_name) -> LangEnglish:
    return language_instances.get(lang_name, default_language_instance)
