def format_number(number):
    if number > 1e10:
        return '{:e}'.format(number)
    else:
        return '{:,}'.format(number)


def format_seconds(seconds):
    units = [
        (31536000, 'years'),
        (2592000, 'months'),
        (604800, 'weeks'),
        (86400, 'days'),
        (3600, 'hours'),
        (60, 'minutes'),
    ]

    for s, unit in units:
        if seconds >= s:
            x = int(seconds // s)
            return '{} {}'.format(format_number(x), unit)

    if seconds > 1:
        return '%d seconds' % seconds
    else:
        return '%f seconds' % seconds
