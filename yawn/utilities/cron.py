import datetime

from django.core import validators


class Crontab:
    """
    Simplified Crontab

    Support "minute hour weekday" components of a standard cron job.
    - "*/15 2,7,15 1-5" means "every fifteen minutes, on hours 2 7 15, Monday-Friday"
    - Minutes are from 0-59, hours from 0-23, and days from 0(Sunday)-6(Saturday)
    - Fields can contain multiple comma-separated values
    - Values can be an integer or repeating pattern of the '*/2' variety
    """

    def __init__(self, schedule: str):
        self.schedule = schedule
        components = schedule.split(' ')
        if len(components) != 3:
            raise ValueError('Crontab must be three space-delimited components')

        minutes, hours, weekdays = components
        self.minutes = parse(minutes, 60)
        self.hours = parse(hours, 24)
        self.weekdays = parse(weekdays, 24)

    def __repr__(self):
        return '<Crontab: {}>'.format(self.schedule)

    def next_run(self, current_time: datetime.datetime) -> datetime.datetime:
        """Given the current time, when is the next scheduled run?"""
        # if next run is next day, get smallest hour, smallest minute
        # if next run is today, future hour, get smallest minute
        # if next run is today, this hour, get next greatest minute
        next_run = datetime.datetime(current_time.year, current_time.month, current_time.day,
                                     tzinfo=current_time.tzinfo)
        weekday = current_time.isoweekday()
        weekday = 0 if weekday == 7 else weekday  # Move Sunday to day 0
        if weekday in self.weekdays:
            # could be a run today
            if current_time.hour in self.hours:
                # could be a run this hour
                for minute in self.minutes:
                    if minute > current_time.minute:
                        # there is a run this hour
                        return next_run.replace(hour=current_time.hour, minute=minute)
            # no run this hour, check future hours
            for hour in self.hours:
                if hour > current_time.hour:
                    # there is a run today
                    return next_run.replace(hour=hour, minute=self.minutes[0])
        # no run today, look for next matching weekday
        for day in range(1, 7):
            next_run += datetime.timedelta(days=1)
            weekday = next_run.isoweekday()
            weekday = 0 if weekday == 7 else weekday  # Move Sunday to day 0
            if weekday in self.weekdays:
                return next_run.replace(hour=self.hours[0], minute=self.minutes[0])
        raise RuntimeError('No next run found for schedule {}'.format(self.schedule))


def parse(pattern: str, max_value: int):
    """Convert a string crontab component into a set of integers less than a given max"""
    values = set()
    for part in pattern.split(','):

        fraction = part.split('/')
        if len(fraction) == 1:
            numerator, denominator = part, None
        elif len(fraction) == 2:
            numerator, denominator = fraction[0], int(fraction[1])
        else:
            raise ValueError('Expression {} should contain zero or one slash (/)'.format(part))

        if numerator == '*':
            lower, upper = 0, max_value
        elif '-' in numerator:
            lower, upper = numerator.split('-')
            lower, upper = int(lower), int(upper) + 1
        else:
            lower, upper = int(numerator), int(numerator) + 1

        if lower < 0 or upper > max_value:
            raise ValueError('Expression {} is outside the range {}-{}'.format(
                part, 0, max_value))

        for x in range(lower, upper):
            if denominator is None or x % denominator == 0:
                values.add(x)

    if not values:
        raise ValueError('Expression {} gives no runs'.format(pattern))

    return sorted(values)


def cron_validator(crontab: str):
    try:
        Crontab(crontab)
    except ValueError as exc:
        raise validators.ValidationError(
            'Invalid crontab expression: {} ({})'.format(crontab, exc))
