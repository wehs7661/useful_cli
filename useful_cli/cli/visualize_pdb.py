import os
import sys
import time
import pymol
import argparse

def initialize(args):
    parser = argparse.ArgumentParser(
        description="This CLI visualizes protein structures using PyMOL."
    )
    parser.add_argument(
        "-p",
        "--pdb_files",
        nargs="+",
        type=str,
        required=True,
        help="The paths to the PDB files to visualize."
    )
    parser.add_argument(
        "-r",
        "--ref",
        type=str,
        help="The path to the reference PDB file to align the input PDB files to."
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="+",
        type=str,
        help="The path to the output PNG file(s). Note that if the --align_all flag is set, \
            only one output will be generated since all input PDB files will be aligned to the reference PDB file.\
            The default is aligned.structures.png in this case. In the case where the --align_all flag is not set, \
            the number of output files must match the number of input PDB files. The default is the input PDB file name \
            with the .png extension in this case."
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
    parser.add_argument(
        "-a",
        "--align_all",
        default=False,
        action="store_true",
        help="Align all input PDB files to the reference PDB file. Default is False, \
            in which case each input PDB file is aligned to the reference PDB file. \
            Note that this requires a reference PDB file to be provided with the -r flag."
    )
    args = parser.parse_args()
    return args

def load_and_align(pdb_file, ref=None):
    """
    Load a PDB file into PyMOL and align it to a reference structure (if provided).

    Parameters
    ----------
    pdb_file : str
        Path to the PDB file.
    ref : str, optional
        Path to the reference PDB file. If provided, the input PDB file will be aligned to this structure.
    """
    cmd = pymol.cmd
    cmd.load(pdb_file, obj_name)
    if ref:
        cmd.align(obj_name, ref)


def render_image(output, width, height, dpi):
    """
    Render the current PyMOL scene and save it as a PNG image.

    Parameters
    ----------
    output : str
        Path to the output PNG file.
    width : int
        Width of the output image in pixels.
    height : int
        Height of the output image in pixels.
    dpi : int
        DPI (dots per inch) of the output image.
    """
    cmd = pymol.cmd
    cmd.bg_color("white")
    cmd.orient()
    cmd.set("ray_opaque_background", "off")
    cmd.ray()
    cmd.png(output, width=width, height=height, dpi=dpi)


def main():
    t0 = time.time()
    args = initialize(sys.argv[1:])

    # 1. Check input arguments
    for pdb_file in args.pdb_files:
        if not os.path.exists(pdb_file):
            raise FileNotFoundError(f"The file {pdb_file} does not exist.")
    if args.ref is not None and not os.path.exists(args.ref):
        raise FileNotFoundError(f"The file {args.ref} does not exist.")
    if args.align_all:
        if args.ref is None:
            raise ValueError("The --align_all flag requires a reference PDB file to be provided with the -r flag.")
        else:
            if args.outputs is not None:
                if len(args.outputs) != 1:
                    raise ValueError("The --align_all flag requires a single output file to be provided.")
            else:
                args.outputs = ["aligned_structures.png"]
    else:
        if args.outputs is not None:
            if len(args.outputs) != len(args.pdb_files):
                raise ValueError("The number of output files must match the number of input PDB files.")
        else:
            args.outputs = [pdb_file.split(".")[0] + ".png" for pdb_file in args.pdb_files]

    # 2. Load, align and save structures
    cmd = pymol.cmd
    if args.align_all:
        if args.ref:
            cmd.load(args.ref, "reference")
        for i, pdb_file in enumerate(args.pdb_files):
            load_and_align(f"structure_{i}", pdb_file, "reference" if args.ref else None)
        render_image(args.outputs[0])
    else:
        for pdb_file, output in zip(args.pdb_files, args.outputs):
            load_and_align("structure", pdb_file, args.ref)
            render_image(output)
            cmd.delete("all")
