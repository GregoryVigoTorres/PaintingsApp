import colour

from wtforms_components import ColorField


class HexColorField(ColorField):
    """
    subclassed to return actually usable color value
    """

    def _value(self):
        """
        I think default_value can also be an HTML color name
        """
        self.default_value = '#ffffff'

        if isinstance(self.data, colour.Color):
            return self.data.get_hex_l()
        else:
            col = colour.Color(self.default_value)
            return col.get_hex_l()

