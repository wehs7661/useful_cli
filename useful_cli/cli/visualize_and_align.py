import os
import sys
import time
import pymol
import argparse

def initialize(args):
    parser = argparse.ArgumentParser(
        description="This CLI visualizes and aligns two protein structures using PyMOL."
    )
    parser.add_argument(
        "-p",
        "--pdb_files",
        nargs=2,
        type=str,
        required=True,
        help="The paths to the two PDB files to visualize and align."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="The path to the output image file. Default is [pdb_1]_[pdb_2].png, where [pdb_1] and [pdb_2] are the names of the input PDB files."
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=800,
        help="The width of the output image. Default is 800."
    )
    parser.add_argument(
        "-ht",
        "--height",
        type=int,
        default=800,
        help="The height of the output image. Default is 800."
    )
    parser.add_argument(
        "-d",
        "--dpi",
        type=int,
        default=600,
        help="The DPI of the output image. Default is 600."
    )

    args = parser.parse_args()
    return args

def main():
    t0 = time.time()
    args = initialize(sys.argv[1:])
    pdb_1, pdb_2 = args.pdb_files

    if not os.path.exists(pdb_1):
        raise FileNotFoundError(f"The file {pdb_1} does not exist.")
    if not os.path.exists(pdb_2):
        raise FileNotFoundError(f"The file {pdb_2} does not exist.")
    
    if args.output is None:
        prefix_1 = os.path.basename(pdb_1).split(".")[0]
        prefix_2 = os.path.basename(pdb_2).split(".")[0]
        args.output = f"{prefix_1}_{prefix_2}.png"

    cmd = pymol.cmd
    cmd.load(pdb_1, "model_1")
    cmd.load(pdb_2, "model_2")
    cmd.align("model_1", "model_2")
    cmd.bg_color("white")
    cmd.orient()
    cmd.set("ray_opaque_background", "off")
    cmd.ray()
    cmd.png(args.output, width=args.width, height=args.height, dpi=args.dpi)
    print(f"Output image saved to {args.output}.")
    print(f"Elapsed time: {time.time() - t0:.2f} seconds.")
