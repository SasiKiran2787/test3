from django import template

register = template.Library()

@register.filter
def currency(value):
    try:
        # Convert the value to a float for formatting
        value = float(value)
        return "${:,.2f}".format(value)  # Format as currency
    except (ValueError, TypeError):
        return value  # Format value as currency

@register.filter
def get_item(dictionary, key):
    """Retrieve an item from a dictionary safely."""
    return dictionary.get(key)

@register.filter
def mul(value, arg):
    """Multiply value by arg."""
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0

@register.filter(name='multiply')
def multiply(number, number1):
    return number * number1
