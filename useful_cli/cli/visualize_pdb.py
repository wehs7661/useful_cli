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
        "--outputs",
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
    parser.add_argument(
        "-s",
        "--split",
        default=False,
        action="store_true",
        help="Split the input PDB file into separate models/frames and align all of them to the reference structure. \
            If the reference structure is not provided in this case, the first model will be used as the reference. \
            Default is False."
    )
    parser.add_argument(
        "-n",
        "--n_models",
        type=int,
        help="The number of models/frames to visualize in cases where the input PDB file is split into multiple \
            models/frames using the --split flag. If not provided, all models/frames will be aligned visualized."
    )
    parser.add_argument(
        "-sel",
        "--selection",
        type=str,
        help="The selection of atoms to align and visualize. If not provided, all atoms will be used."
    )
    parser.add_argument(
        "-z",
        "--zoom",
        type=float,
        help="The buffer (in Angstroms) around the selected atoms to zoom in on. The default is not to zoom in at all."
    )
    args = parser.parse_args()
    return args

def load_and_align(obj_name, pdb_file, ref=None, split=False, n_models=None, selection=None, zoom=None):
    """
    Load a PDB file into PyMOL and align it to a reference structure (if provided).

    Parameters
    ----------
    obj_name : str
        Name of the object to create in PyMOL.
    pdb_file : str
        Path to the PDB file.
    ref : str, optional
        Path to the reference PDB file. If provided, the input PDB file will be aligned to this structure.
    split : bool, optional
        For a PDB file containing multiple models/frames, whether to split them into separate objects
        and align all of them to the reference structure. If the reference structure is not provided in this case,
        the first model will be used as the reference. The default is False.
    n_models : int, optional
        The number of models/frames to visualize in cases where the input PDB file is split into multiple
        models/frames using the split flag. If not provided, all models/frames will be aligned visualized.
    selection : str, optional
        The selection of atoms to align and visualize. If not provided, all atoms will be used.
    zoom : float, optional
        The buffer (in Angstroms) around the selected atoms to zoom in on. The default is not to zoom in at all.
    """
    print(f"Loading {pdb_file}...")
    cmd = pymol.cmd
    cmd.load(pdb_file, obj_name)
    
    align_obj = obj_name
    if selection is not None:
        obj_name = f"{obj_name}_selected"
        cmd.select(obj_name, selection)
        if cmd.count_atoms(obj_name) == 0:
            raise ValueError(f"The selection {selection} does not contain any atoms.")
        cmd.hide("everything", f"not {obj_name}")

    if split:
        print("Splitting the models...")
        cmd.split_states(obj_name)
        if n_models is None:
            n_models = cmd.count_states(obj_name)
        else:
            if n_models > cmd.count_states(obj_name):
                raise ValueError(f"The input PDB file {pdb_file} contains only {cmd.count_states(obj_name)} models \
                    but n_models is set to {n_models}.")

        if ref is not None:
            cmd.load(ref, "reference")
            for i in range(1, n_models + 1):
                print(f"Aligning {align_obj}_{i:04d} to the reference...")
                cmd.align(f"{align_obj}_{i:04d}", "reference")
        else:
            for i in range(2, n_models + 1):
                print(f"Aligning {align_obj}_{i:04d} to {align_obj}_0001...")
                cmd.align(f"{align_obj}_{i:04d}", f"{align_obj}_0001")

        # Color the models
        # print("Coloring the models...")
        # cmd.spectrum("count", "green_white_yellow", f"{obj_name}_*")
        
    else:
        if ref is not None:
            cmd.load(ref, "reference")
            cmd.align(obj_name, "reference")

    cmd.orient()
    if zoom is not None:
        cmd.zoom(obj_name, buffer=zoom)


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
            load_and_align(
                f"structure_{i}",
                pdb_file,
                "reference" if args.ref else None,
                args.split,
                args.n_models,
                args.selection,
                args.zoom
            )

        print("Rendering the image...")
        render_image(args.outputs[0], args.width, args.height, args.dpi)
    else:
        for pdb_file, output in zip(args.pdb_files, args.outputs):
            load_and_align(
                "structure",
                pdb_file,
                args.ref,
                args.split,
                args.n_models,
                args.selection,
                args.zoom
            )
            render_image(output, args.width, args.height, args.dpi)
            cmd.delete("all")

    print(f"Elapsed time: {time.time() - t0:.2f} s.")
