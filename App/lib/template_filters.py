import logging
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode

from App.core import db

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


def get_page_url(url, page):
    """ E.g. first, last or page3 """
    pu = urlsplit(url)
    qs = parse_qs(pu.query)

    if qs is None:
        qs = {'page':page}
    else:
        qs.update({'page':page})

    query = urlencode(qs, doseq=True)
    page_url = urlunsplit((pu.scheme, pu.netloc, pu.path, query, pu.fragment))

    return page_url


def prev_page_url(url):
    pu = urlsplit(url)
    qs = parse_qs(pu.query)

    if qs is None:
        qs = {'page':1}
    elif not qs.get('page'):
        qs.update({'page':1})
    else:
        try:
            p = int(qs['page'][0], base=10)
            if p > 0:
                p -= 1
            qs['page'] = str(p)
        except Exception as E:
            msg = 'Inavlid page url because {}'.format(E)
            logging.warning(msg)
            return url

    query = urlencode(qs, doseq=True)
    prev_url = urlunsplit((pu.scheme, pu.netloc, pu.path, query, pu.fragment))

    return prev_url


def next_page_url(url):
    """ returns current url with
        next page or page 1 
    """
    pu = urlsplit(url)
    qs = parse_qs(pu.query)

    if qs is None:
        qs = {'page':1}
    elif not qs.get('page'):
        qs.update({'page':1})
    else:
        try:
            p = int(qs['page'][0], base=10)
            p += 1
            qs['page'] = str(p)
        except Exception as E:
            msg = 'Inavlid page url because {}'.format(E)
            logging.warning(msg)
            return url

    query = urlencode(qs, doseq=True)
    next_url = urlunsplit((pu.scheme, pu.netloc, pu.path, query, pu.fragment))

    return next_url


def get_images(series):
    """ Because series.images is loaded dynamically and 
        is thus a query object, return a list
    """
    db.session.add(series)
    return series.images.all()
