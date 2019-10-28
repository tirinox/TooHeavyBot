class LangEnglish:
    KEY = 'eng'

    def __init__(self):
        self.hello = "Hi! I'm a trainer robot. I will help you to drop or gain body weight."

        self.time_zone_prompt = ("In order to send you notifications in time,"
                                 "I need to know your time zone.\n\n"
                                 "You can send me your location. You don't have to "
                                 "send me your exact address. Just send me where "
                                 "your city is.")

        self.back = 'Back'
        self.cancel = 'Cancel'

        self.mm_ideal_weight = 'My perfect weight'
        self.mm_aim_percent = 'Weight progress'
        self.mm_settings = 'Settings'

        self.invalid_menu_option = "<pre>Unknown menu option!</pre>"
        self.invalid_number = "<pre>Bad number!</pre>"
