
def fmt_datetime(dtime):
    """ returns formatted datetime for date_created
        fails silently
    """
    try:
        fmt = '%d/%m/%y at %H:%M'
        return dtime.strftime(fmt)
    except AttributeError:
        return ''

def none_as_str(value):
    if not value:
        return ''
    else:
        return value
