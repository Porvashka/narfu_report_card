from datetime import datetime, timedelta, time


def get_dates_schedule(now=datetime.now()):
    now = datetime.combine(now, time.min)
    day = datetime.isoweekday(now) % 10

    match day:
        case 1:
            first_day = now
            last_day = now + timedelta(days=6)
        case 2:
            first_day = now + timedelta(days=-1)
            last_day = now + timedelta(days=5)
        case 3:
            first_day = now + timedelta(days=-2)
            last_day = now + timedelta(days=4)
        case 4:
            first_day = now + timedelta(days=-3)
            last_day = now + timedelta(days=3)
        case 5:
            first_day = now + timedelta(days=-4)
            last_day = now + timedelta(days=2)
        case 6:
            first_day = now + timedelta(days=-5)
            last_day = now + timedelta(days=1)
        case 7:
            first_day = now + timedelta(days=-6)
            last_day = now
    first_day = f"{str(first_day).replace(' ', 'T')}Z"
    last_day = f"{str(last_day).replace(' ', 'T')}Z"
    return [first_day, last_day]
