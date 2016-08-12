import re
import string

import colour

from wtforms.validators import (ValidationError, UUID)

def strong_password(password=None, field=None):
    """
    min len 8 chars
    max len 45 chars
    must contain:
        upper and lower case letters
        digits
        punctuation

    this should work with forms as well as Manager input
    """

    if not password:
        password = field.data

    if len(password) < 8:
        raise ValidationError('The password is too short')
    if len(password) > 67:
        raise ValidationError('The password is too long')

    sp_char_str = '[{}]'.format(re.escape("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"))
    caps = re.compile('[A-Z]')
    low = re.compile('[a-z]')
    nums = re.compile('[0-9]')
    has_sp_chars = re.search(sp_char_str, password)
    has_caps = re.search(caps, password)
    has_lower = re.search(low, password)
    has_num = re.search(nums, password)
    valid_chars = (has_sp_chars, has_caps, has_lower, has_num)

    if not valid_chars:
        raise ValidationError("""The password must contain upper and lower case letters
        and at least one number and special character""")


def no_html(form, field):
    """
        field data cannot contain any html tags
        escaping is handled by jinja
    """
    tag_re = re.compile('(<[a-zA-Z ]+>*)(</)*')
    has_tags = re.search(tag_re, field.data)
    if has_tags:
        raise ValidationError(message='html tags are not allowed')


def valid_email(_email):
    """ just determines whether an email address looks valid """

    if '@' not in _email:
        raise ValidationError('>>the email must contain @')

    if len(_email) > 255:
        raise ValidationError('>>max length is 255')

    name, domain = _email.split('@')
    allowed_chars = string.ascii_letters+string.digits+'.-_'
    valid_chars = lambda i: i in allowed_chars
    valid_name = all([valid_chars(i) for i in name])
    valid_domain = all([valid_chars(i) for i in domain])

    if not valid_domain or not valid_name:
        raise ValidationError('>>the email contains invalid characters')

    dots = domain.count('.')
    if dots < 1:
        raise ValidationError('>>the domain is not valid')


def valid_color(form, field):
    """
    raise ValidationError or return None
    """
    if isinstance(field.data, colour.Color) is False:
        raise ValidationError('Invalid color')

    as_hex = field.data.get_hex_l()
    valid_hex = re.match('#[a-zA-Z0-9]{6}', as_hex)

    if valid_hex is None:
        raise ValidationError('{} is not a valid color value'.format(as_hex))


def exor(*fields):
    """
    Exactly one element in current field + fields is allowed.
    This should only be declared on one of the fields.
    """
    message = 'exactly one of {} is required'

    def _exor(form, field):
        field_names = [field.label.text]
        data = [field.data]
        for i in fields:
            fld = getattr(form, i)
            field_names.append(fld.label.text)
            data.append(fld.data)

        one = [i for i in data if i]
        if len(one) != 1:
            field_str = ', '.join(field_names)
            raise ValidationError(message.format(field_str))

    return _exor


class valid_uuid(UUID):
    def __call__(self, form, field):
        message = self.message
        field.data = str(field.data)
        if message is None:
            message = field.gettext('Invalid UUID.')

        super(UUID, self).__call__(form, field, message)

