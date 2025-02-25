import sys
import cv2
import numpy as np
import argparse
import matplotlib.pyplot as plt 
from useful_cli import utils

def initialize():
    parser = argparse.ArgumentParser(
        description='This script combines multiple figures into a single figure.')
    parser.add_argument('-f',
                        '--figs',
                        nargs='+',
                        required=True,
                        help='The paths to the figures to be combined.')
    parser.add_argument('-d',
                        '--dimension',
                        type=int,
                        nargs='+',
                        help='The dimensions of the subplots (n_cols, n_rows). If not specified, \
                            the script will try to make the figure as square as possible.')
    parser.add_argument('-s',
                        '--size',
                        type=int,
                        nargs='+',
                        help='The size of the figure (width, height). The default size is (6.4, 4.8).')
    parser.add_argument('-t',
                        '--titles',
                        nargs='+',
                        help='The titles of the subplots.')
    parser.add_argument('-b',
                        '--border',
                        default=False,
                        action='store_true',
                        help='Whether to show the border lines of each subplot.')
    parser.add_argument('-n',
                        '--figname',
                        default='combined_figure.png',
                        help='The path to save the combined figure.')

    args_parse = parser.parse_args()

    return args_parse


def main():
    args = initialize()
    utils.configure_matplotlib()

    if args.size is None:
        fig = plt.figure()
    else:
        if len(args.size) != 2:
            print('Warning: wrong number of arguments for specifying the figure size.')
        else:
            fig = plt.figure(figsize=tuple(args.size))

    if args.dimension is None:
        n_cols, n_rows = utils.get_subplot_layout(len(args.figs))
    else:
        if len(args.dimension) != 2:
            raise ValueError('The number of dimensions should be 2.')
        else:
            n_cols = args.dimension[0]
            n_rows = args.dimension[1]

    if args.titles is not None:
        if len(args.figs) != len(args.titles):
            raise ValueError('The number of titles should match the number of figures.')

    for i in range(len(args.figs)):
        image = cv2.imread(args.figs[i], cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        fig.add_subplot(n_rows, n_cols, i + 1)
        plt.imshow(image_rgb)
        if args.border is True:
            plt.xticks([])
            plt.yticks([])
        elif args.border is False:
            plt.axis('off')  
        if args.titles is not None:
            plt.title(args.titles[i])
        
    plt.tight_layout(rect=[0, 0, 1, 1])
    plt.savefig(f'{args.figname}', dpi=600)
