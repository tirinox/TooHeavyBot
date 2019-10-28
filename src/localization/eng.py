class LangEnglish:
    KEY = 'eng'

    def __init__(self):
        # common

        self.back = 'Back'
        self.cancel = 'Cancel'

        # main menu

        self.hello = "Hi! I'm a trainer robot. I will help you to drop or gain body weight."

        self.mm_ideal_weight = 'My perfect weight'
        self.mm_aim_percent = 'Weight progress'
        self.mm_settings = 'Settings'

        # settings

        self.s_title = 'Bot settings:'
        self.s_timezone = 'Time zone'
        self.s_notification = 'Notification'
        self.s_language = 'Language'

        self.s_lang_hi = 'Hi / Привет!'
        self.s_lang_set = 'English is set.'
        self.s_russian = 'Русский'
        self.s_english = 'English'

        # settings -> time zone

        self.time_zone_prompt = ("In order to send you notifications in time,"
                                 "I need to know your time zone.\n\n"
                                 "You can send me your location. You don't have to "
                                 "send me your exact address. Just send me where "
                                 "your city is.")
        self.time_zone_err_bad_loc = ('Мы не смогли найти подходящий часовой пояс для вашей локации. '
                                      'Введите название города вручную:')
        self.time_zone_ok = lambda tz_name: f'Мы установили, что ваш часовой пояс: <b>{tz_name}</b>. Верно?\n'
        self.time_zone_unknown_city = 'Не знаю такого города...'
        self.send_location = '📍 Send my location'

        # setting -> notification

        self.s_not_dont = 'Не уведомлять'
        self.s_not_ask_1 = 'Введите время в формате ЧЧ:ММ или ЧЧ ММ - 24 часа. Например: "8:00" или "12 05".'
        self.s_not_ask = f'Давайте настроим напонимание о том, что вам пора внести вес. {self.s_not_ask_1}'
        self.s_not_off = 'Напонимание выключено!'
        self.s_not_on = lambda d_hh, d_mm: f'Напонимание установлено! Оно прозвучит через {d_hh} ч. {d_mm} мин.'
        self.s_not_err = f'Кажется, вы меня не так поняли! {self.s_not_ask_1}'

        # service

        self.invalid_menu_option = "<pre>Unknown menu option!</pre>"
        self.invalid_number = "<pre>Bad number!</pre>"
