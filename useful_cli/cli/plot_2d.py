import natsort
import argparse
import numpy as np
import matplotlib.pyplot as plt
from useful_cli import utils


def initialize():
    conversion_choices = list(utils.get_conversions().keys())
    parser = argparse.ArgumentParser(
        description="Plot 2D data from an XVG files."
    )
    parser.add_argument(
        "-f",
        "--xvg",
        nargs="+",
        required=True,
        help="The path(s) to the XVG file(s)."
    )
    parser.add_argument(
        "-l",
        "--legend",
        nargs="+",
        help="Legend for the plot(s). If omitted, file names are used."
    )
    parser.add_argument(
        "-x",
        "--xlabel",
        type=str,
        help='The name and units of the x-axis.'
    )
    parser.add_argument(
        "-y",
        "--ylabel",
        type=str,
        help="The name and units of the y-axis."
    )
    parser.add_argument(
        "-c",
        "--column", 
        type=int, 
        default=1,
        help="The column index of the data to be plotted."
    )
    parser.add_argument(
        "-t", 
        "--title", 
        type=str, 
        help="The title of the figure."
    )
    parser.add_argument(
        "-n",
        "--figname",
        type=str,
        default="plot.png",
        help="The path to save the figure."
    )
    parser.add_argument(
        "-cx",
        "--x_conversion",
        choices=conversion_choices,
        help="The unit conversion for the data in the x-axis."
    )
    parser.add_argument(
        "-cy",
        "--y_conversion",
        choices=conversion_choices,
        help="The unit conversion for the data in the y-axis."
    )
    parser.add_argument(
        "-fx",
        "--factor_x",
        type=float,
        help="The factor to be multiplied the x values."
    )
    parser.add_argument(
        "-fy",
        "--factor_y",
        type=float,
        help="The factor to be multiplied the y values."
    )
    parser.add_argument(
        "-T",
        "--temp",
        type=float,
        default=298.15,
        help="Temperature for unit convesion involving kT. The default is 298.15 K."
    )
    parser.add_argument(
        "-tr",
        "--truncate",
        help='Percentage (0-100) of the data to truncate from the beginning.'
    )
    parser.add_argument(
        "-r",
        "--retain",
        help='Percentage (0-100) of the data to retain from the beginning.'
    )
    parser.add_argument(
        '-lc',
        '--legend_col',
        type=int,
        default=1,
        help='The number of columns of the legend.'
    )
    
    args_parse = parser.parse_args()

    if args_parse.legend is None:
        args_parse.legend = args_parse.xvg

    return args_parse


def main():
    args = initialize()
    utils.configure_matplotlib()
    args.xvg = natsort.natsorted(args.xvg)

    plt.figure()  # ready to plot!
    for i in range(len(args.xvg)):
        print(f'Analyzing the file: {args.xvg[i]} ...')

        x, y = [], []
        file = open(args.xvg[i], 'r')
        lines = file.readlines()
        file.close()

        m = 0
        for line in lines:
            if line.startswith('#') or line.startswith('@'):
                m += 1  # number of parameter lines
                if 'xaxis  label "Time (ps)"' in line and args.x_conversion is None:
                    args.x_conversion = 'ps to ns'    

        # read in data starting from (m+1)-th line to the end
        n = m   # line number
        for line in lines[m:-1]:
            n += 1
            if '#' not in line and line[0] != '@':
                # Note that when extending MetaD, COLVAR might append #! FIELDS ... 
                x.append(float(line.split()[0]))
                y.append(float(line.split()[args.column]))
            elif '#' in line:  # the case the MetaD is extended
                x = np.array(x)
                x = x[x < float(lines[n].split()[0])]
                x = list(x)
                y = y[:len(x)]
        x, y = np.array(x), np.array(y)

        # Unit conversion
        if args.xlabel is not None:
            if '(' in args.xlabel:
                if '$' in args.xlabel.split('(')[1]:
                    x_unit = args.xlabel.split('$')[1].split('$')[0]
                else:
                    x_unit = args.xlabel.split('(')[1].split(')')[0]
                x_var = args.xlabel.split('(')[0].lower()
                if x_var[-1] == ' ':
                    x_var = x_var.split(' ')[0].lower()
            else:
                x_unit = ''
                x_var = args.xlabel.lower()
        else:
            x_unit = ''
            x_var = None 

        if args.ylabel is not None:
            if '(' in args.ylabel:
                if '$' in args.ylabel.split('(')[1]:
                    y_unit = args.ylabel.split('$')[1].split('$')[0]
                else:
                    y_unit = args.ylabel.split('(')[1].split(')')[0]
                y_var = args.ylabel.split('(')[0].lower()
                if y_var[-1] == ' ':
                    y_var = y_var.split(' ')[0].lower()
            else:
                y_unit = ''
                y_var = args.ylabel.lower()
        else:
            y_unit = ''
            y_var = None

        x, x_unit = utils.apply_conversion(x, args.x_conversion, args.temp)
        y, y_unit = utils.apply_conversion(y, args.y_conversion, args.temp)

        if args.factor_x is not None:
            x = x * args.factor_x
        if args.factor_y is not None:
            y = y * args.factor_y

        if args.truncate is not None:
            y = y[int(0.01 * float(args.truncate) * len(y)):]
            x = x[int(0.01 * float(args.truncate) * len(x)):]
            print(f"Truncated the first {args.truncate}% of the data.")
        if args.retain is not None:
            y = y[:int(0.01 * float(args.retain) * len(y))]
            x = x[:int(0.01 * float(args.retain) * len(x))]
            print(f"Retained only the first {args.retain}% of the data.")
        
        y_avg = np.mean(y)
        y2_avg = np.mean(np.power(y, 2))
        RMSF = np.sqrt((y2_avg - y_avg ** 2)) / y_avg
        print(f'The average of {y_var}: {y_avg:.3f} {y_unit} (RMSF: {RMSF:.3f} {y_unit} max: {np.max(y):.3f} {y_unit}, min: {np.min(y):.3f} {y_unit})')
        if x_unit == ' ns' or x_unit == ' ps':
            y = list(y)
            print(f'The maximum occurs at {x[y.index(max(y))]:5.4f} {x_unit}, while the minimum occurs at {x[y.index(min(y))]:5.4f} {x_unit}.')
            y = np.array(y)
            diff = np.abs(y - y_avg)
            t_avg = x[np.argmin(diff)]
            print('The configuration at %s%s has the %s (%s%s) that is cloest to the average volume.' % (t_avg, x_unit, y_var, y[np.argmin(diff)], y_unit))
        if args.legend is None:
            plt.plot(x, y)
        else:
            plt.plot(x, y, label=args.legend[i])

    if args.title is not None:
        plt.title(args.title, weight='bold')
    plt.xlabel(args.xlabel)
    plt.ylabel(args.ylabel)

    if max(abs(y)) >= 10000:
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    
    plt.grid()
    if args.legend is not None:
        if len(args.xvg) > 1:
            plt.legend(ncol=args.legend_col)

    plt.savefig(args.figname, dpi=600)
