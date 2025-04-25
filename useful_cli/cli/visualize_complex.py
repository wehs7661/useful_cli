import os
import sys
import pymol
import argparse


def initialize(args):
    parser = argparse.ArgumentParser(
        description="This CLI visualises protein-ligand complexes using PyMOL. "
    )
    parser.add_argument(
        "-f",
        "--files",
        type=str,
        nargs="+",
        required=True,
        help="List of files (that can be read by PyMOL) to visualize.",
    )
    parser.add_argument(
        "-a",
        "--align",
        type=str,
        nargs="+",
        help="The align commands to use. Note that the input structures files will be \
            automatically named as 'structure_1', 'structure_2', etc."
    )
    parser.add_argument(
        "-z",
        "--zoom_obj",
        type=str,
        help="The object to zoom in on.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="complex.png",
        help="The output file name.",
    )
    args = parser.parse_args()
    return args

def main():
    args = initialize(sys.argv[1:])
    cmd = pymol.cmd
    for i, file in enumerate(args.files):
        cmd.load(file, f"structure_{i+1}")

    if args.align:
        for i, align in enumerate(args.align):
            align_obj = [i.strip() for i in align.split("align")[1].split(",")]
            cmd.do(align)
        cmd.orient()
        if args.zoom_obj:
            cmd.orient(args.zoom_obj)
            cmd.zoom(args.zoom_obj, buffer=5)

    cmd.bg_color("white")
    cmd.set("ray_opaque_background", "off")
    cmd.ray()
    cmd.png(args.output, width=800, height=800, dpi=600)
