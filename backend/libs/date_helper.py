from datetime import date, timedelta


class DateHelper:

    @classmethod
    def last_month1to31(cls):
        '''
        :return: (date, date)
        '''
        today = date.today()
        last_month = date(today.year, today.month-1, 1) if today.month != 1 else date(today.year-1, 12, 1)

        return last_month, cls.last_day_of_month(last_month)

    @classmethod
    def last_day_of_month(self, any_day):
        '''
        user
        '''
        next_month = any_day.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)
