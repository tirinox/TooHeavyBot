class LangRussian:
    KEY = 'rus'

    def __init__(self):
        # common

        self.back = 'Назад'
        self.cancel = 'Отмена'
        self.skip = 'Пропустить'

        # main menu

        self.hello = 'Привет! Я робот-тренер и помогу тебе достичь идеального веса (похудеть или набрать массу)!'
        self.mm_ideal_weight = 'Мой идеальный вес'
        self.mm_aim_percent = 'Процент цели?'
        self.mm_settings = 'Настройки'

        # settings

        self.s_title = 'Настройки бота:'
        self.s_timezone = 'Часовой пояс'
        self.s_notification = 'Уведомление'
        self.s_language = 'Язык'

        self.s_lang_hi = 'Hi / Привет!'
        self.s_lang_set = 'Установлен русский язык.'
        self.s_russian = 'Русский'
        self.s_english = 'English'

        # settings -> time zone

        self.time_zone_prompt = ('Чтобы вовремя отправлять вам уведомления, '
                                 'нам нужно узнать ваш часовой пояс.\n\n'
                                 'Вы может отправить геолокацию, чтобы мы определели '
                                 'часовой пояс. Не обязательно '
                                 'отправлять ваш точный адрес. '
                                 'Вы можете отправить любую локацию из вашего часового пояса.')
        self.time_zone_err_bad_loc = ('Мы не смогли найти подходящий часовой пояс для вашей локации. '
                                      'Введите название города вручную:')
        self.time_zone_ok = lambda tz_name: f'Мы установили, что ваш часовой пояс: <b>{tz_name}</b>. Верно?\n'
        self.time_zone_unknown_city = 'Не знаю такого города...'
        self.send_location = '📍 Отправить локацию'

        # setting -> notification

        self.s_not_dont = 'Не уведомлять'
        self.s_not_ask_1 = 'Введите время в формате ЧЧ:ММ или ЧЧ ММ - 24 часа. Например: "8:00" или "12 05".'
        self.s_not_ask = f'Давайте настроим напонимание о том, что вам пора внести вес. {self.s_not_ask_1}'
        self.s_not_off = 'Напонимание выключено!'
        self.s_not_on = lambda d_hh, d_mm: f'Напонимание установлено! Оно прозвучит через {d_hh} ч. {d_mm} мин.'
        self.s_not_err = f'Кажется, вы меня не так поняли! {self.s_not_ask_1}'

        # service

        self.invalid_menu_option = "<pre>Неизвестная опция меню!</pre>"
        self.invalid_number = "<pre>Плохое число!</pre>"

        # aim percent

        self.ap_prompt_today_weight = 'Введите ваш вес сегодня в кг:'
        self.ap_prompt_weight_err = 'Должно быть число от 40 до 500!'
        self.ap_drop_weight = lambda delta: f'Вы похудели на {delta:0.2f} кг со вчера.\n'
        self.ap_gain_weight = lambda delta: f'Вы поправились на {delta:0.2f} кг со вчера.\n'
        self.ap_same_weight = 'Ваш вес не изменился со вчера.\n'
        self.ap_progress = lambda percent: f'\nВаш прогресс:\n<b>{percent:.2f} %</b>\n'
        self.ap_prompt_start_weight = 'Введите ваш начальный вес в кг. Это будет 0 % цели:'
        self.ap_prompt_aim_weight = 'Введите ваш целевой вес в кг. Это будет 100 % цели:'
        self.ap_menu = "Мы посчитаем процент вашего прогресса:"
        self.ap_enter_today = 'Внести вес сегодня'
        self.ap_change_start = lambda s: f'Изменить старт ({s:.1f} кг)'
        self.ap_change_aim = lambda s: f'Изменить цель ({s:.1f} кг)'

        # best weight

        self.bw_prompt_height = 'Ваш рост в сантиметрах?'
        self.bw_prompt_height_err = 'Должно быть число от 50 до 300!'
        self.bw_result = lambda result: f'Ваш идеальный вес: {result} кг'
        self.bw_prompt_sex = "Какой ваш пол?"
        self.bw_male = 'Мужской'
        self.bw_female = 'Женский'
