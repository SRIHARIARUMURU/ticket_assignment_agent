from datetime import datetime


class ShiftService:

    def get_current_shift(self):

        current_hour = datetime.now().hour

        if 6 <= current_hour < 14:

            return "Morning"

        elif 14 <= current_hour < 22:

            return "Evening"

        else:

            return "Night"