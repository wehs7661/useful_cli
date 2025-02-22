
import matplotlib.pyplot as plt
from matplotlib import rc


def configure_matplotlib():
    rc('font', **{
       'family': 'sans-serif',
       'sans-serif': ['DejaVu Sans'],
       'size': 10
    })
    # Set the font used for MathJax - more on this later
    rc('mathtext', **{'default': 'regular'})
    plt.rc('font', family='serif')


def get_conversions():
    """
    Returns a dictionary mapping conversion keys to a tuple of
    (conversion_function, target_unit_label).
    The conversion_function may require the temperature value as a parameter.
    """
    return {
        'ps to ns': (lambda x, temp=None: x / 1000, 'ns'),
        'ns to ps': (lambda x, temp=None: x * 1000, 'ps'),
        'kT to kJ/mol': (lambda x, temp: x * (1.38064852 * 6.02 * temp / 1000), 'kJ/mol'),
        'kJ/mol to kT': (lambda x, temp: x / (1.38064852 * 6.02 * temp / 1000), 'kT'),
        'kT to kcal/mol': (lambda x, temp: x * (1.38064852 * 6.02 * temp / 1000) * 0.239005736, 'kcal/mol'),
        'kcal/mol to kT': (lambda x, temp: x / ((1.38064852 * 6.02 * temp / 1000) * 0.239005736), 'kT'),
        'kJ/mol to kcal/mol': (lambda x, temp=None: x * 0.239005736, 'kcal/mol'),
        'kcal/mol to kJ/mol': (lambda x, temp=None: x / 0.239005736, 'kJ/mol'),
        'degree to radian': (lambda x, temp=None: x * (np.pi / 180), 'radian'),
        'radian to degree': (lambda x, temp=None: x / (np.pi / 180), 'degree')
    }


def apply_conversion(data, conversion=None, temp=None):
    """
    Apply unit conversion on data if conversion is specified.
    The conversion parameter should be one of the keys in the dictionary returned by get_conversions().
    """
    if conversion is None:
        return data, None
    conversions = get_conversions()
    func, unit_label = conversions[conversion]

    try:
        new_data = func(data, temp)
    except TypeError:
        new_data = func(data)
    return new_data, unit_label

