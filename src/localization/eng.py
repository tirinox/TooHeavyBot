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
        self.time_zone_err_bad_loc = ('We was not able to detect time zone for your location. '
                                      'Enter the name of your city:')
        self.time_zone_ok = lambda tz_name: f'I detected your time zone: <b>{tz_name}</b>. Correct?\n'
        self.time_zone_unknown_city = "Don't know this city..."
        self.send_location = '📍 Send my location'

        # setting -> notification

        self.s_not_dont = "Don't notify me"
        self.s_not_ask_1 = 'Please enter the time in HH:MM or HH MM format. For an instance 8:05 or 10 30:'
        self.s_not_ask = f"Let's set up a notification. So you don't forget to add your weight everyday." \
                         f" {self.s_not_ask_1}"
        self.s_not_off = 'Notification is turned off!'
        self.s_not_on = lambda d_hh, d_mm: f'Notification is turned on! You will get it in {d_hh} h. {d_mm} min.'
        self.s_not_err = f'It seems you did not get what I say. {self.s_not_ask_1}'

        self.notification_weight = "Hey! It's hight time to enter your weight today!"

        # service

        self.invalid_menu_option = "<pre>Unknown menu option!</pre>"
        self.invalid_number = "<pre>Bad number!</pre>"

        # aim percent

        self.ap_prompt_today_weight = 'Enter your weight today in KG:'
        self.ap_prompt_weight_err = 'Have to be a number between 30 and 500!'
        self.ap_aim_eq_start_err = 'Start weight must not be equal to target weight.'
        self.ap_drop_weight = lambda delta: f'You have dropped {delta:0.2f} KG since yesterday.'
        self.ap_gain_weight = lambda delta: f'You have gained {delta:0.2f} KG since yesterday.'
        self.ap_same_weight = "You weight has not changed."
        self.ap_you_forgot = "It seems, you didn't enter your weight yesterday."
        self.ap_progress = lambda percent: f'\nYour progress is\n<b>{percent:.2f} %</b>'
        self.ap_prompt_start_weight = 'Please enter your start weight (it is 0 % of aim) KG:'
        self.ap_prompt_aim_weight = 'Please enter your target weight (it is 100 %) KG:'
        self.ap_menu = "I will calculate your grade of progress."
        self.ap_enter_today = 'Enter weight today'
        self.ap_change_start = lambda s: f'Edit the start ({s:.1f} KG)'
        self.ap_change_aim = lambda s: f'Edit the aim ({s:.1f} KG)'
        self.ap_chart_name = 'Weight chart ☝️'
        self.ap_weight_label = 'Weight, KG'
        self.ap_percent_label = 'Progress, %'

        # best weight

        self.bw_prompt_height = 'What is your height in cm?'
        self.bw_prompt_height_err = 'Must be a number between 50 and 300!'
        self.bw_result = lambda result: f'Your perfect weight is {result} KG.'
        self.bw_prompt_sex = "What is your sex?"
        self.bw_male = 'Male'
        self.bw_female = 'Female'
