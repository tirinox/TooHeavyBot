class LangEnglish:
    KEY = 'eng'

    def __init__(self):
        # common

        self.back = 'Back'
        self.cancel = 'Cancel'
        self.skip = 'Skip'

        # main menu

        self.hello = "Hi! I'm a trainer robot. I will help you to drop or gain body weight."

        self.mm_aim_percent = 'Weight progress'
        self.mm_settings = 'Settings'

        # settings

        self.s_title = 'Bot settings:'
        self.s_timezone = 'Time zone'
        self.s_notification = 'Notification'
        self.s_language = 'Language'
        self.s_best_weight = 'My perfect weight'

        self.s_lang_hi = 'Hi / Привет!'
        self.s_lang_set = 'English is set.'
        self.s_russian = '🇷🇺 Русский'
        self.s_english = '🇬🇧 English'

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

        # aim percent

        self.ap_prompt_today_weight = 'Enter your weight today in kg:'
        self.ap_prompt_weight_err = 'Have to be a number between 30 and 500!'
        self.ap_drop_weight = lambda delta: f'You have dropped {delta:0.2f} кг since yesterday.\n'
        self.ap_gain_weight = lambda delta: f'You have gained {delta:0.2f} кг since yesterday.\n'
        self.ap_same_weight = 'You weight has not changed.\n'
        self.ap_progress = lambda percent: f'\nYour progress is\n<b>{percent:.2f} %</b>\n'
        self.ap_prompt_start_weight = 'Please enter your start weight (it is 0 % of aim) kg:'
        self.ap_prompt_aim_weight = 'Please enter your target weight (it is 100 %) kg:'
        self.ap_menu = "I will calculate your grade of progress."
        self.ap_enter_today = 'Enter weight today'
        self.ap_change_start = lambda s: f'Edit the start ({s:.1f} kg)'
        self.ap_change_aim = lambda s: f'Edit the aim ({s:.1f} kg)'

        # best weight

        self.bw_prompt_height = 'What is your height in cm?'
        self.bw_prompt_height_err = 'Must be a number between 50 and 300!'
        self.bw_result = lambda result: f'Your perfect weight is {result} kg.'
        self.bw_prompt_sex = "What is your sex?"
        self.bw_male = 'Male'
        self.bw_female = 'Female'
