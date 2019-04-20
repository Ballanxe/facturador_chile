from django import template

register = template.Library()

@register.filter(name='format_mil')
def formatSeparadorMiles(value, separador = '.'):
    """
    """
    cadena = float(value)
    if separador == '.':
        lista_decimal = "{0:,}".format(cadena).replace(',','.').split('.')[-1:]
        lista_num = "{0:,}".format(cadena).replace(',','.').split('.')[:-1]
        return '.'.join(lista_num)+","+ lista_decimal[0]
    elif separador == ',':
        return "{0:,}".format(cadena)
    else:
        lista_decimal = "{0:,}".format(cadena).replace(',',separador).split('.')[-1:]
        lista_num = "{0:,}".format(cadena).replace(',', separador).split('.')[:-1]
        return '.'.join(lista_num)+","+ lista_decimal[0]