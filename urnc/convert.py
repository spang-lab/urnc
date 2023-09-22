import click
import nbformat
import os
from traitlets.config import Config
from nbconvert.preprocessors.clearoutput import ClearOutputPreprocessor
from nbconvert.exporters.notebook import NotebookExporter

from urnc.preprocessor.add_tags import AddTags
from urnc.preprocessor.exercises import ProcessExercises
from urnc.preprocessor.remove_solutions import RemoveSolutions


@click.command(help="Convert Notebooks for UR FIDS Courses")
@click.argument(
    "input",
    type=click.Path(exists=True),
    default="."
)
@click.argument(
    "output",
    type=str,
    default="out"
)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-f", "--force", is_flag=True)
@click.pass_context
def convert(ctx, input, output, verbose, force):
    convert_fn(ctx, input, output, verbose, force)





def convert_fn(ctx, input, output, verbose, force):
    base = ctx.obj["ROOT"]
    if(not os.path.isabs(input)):
        input = os.path.join(base, input)
        input = os.path.abspath(input)
    if(not os.path.isabs(output)):
        output = os.path.join(base, output)
        output = os.path.abspath(output)
    print(f"Converting notebooks in {input} to {output}")
    paths = []
    folder = input
    if os.path.isfile(input):
        paths.append(input)
        folder = base
    else:
        for root, dirs, files in os.walk(input, topdown=True):
            dirs[:] = [d for d in dirs if not d[0] == "."]
            for file in files:
                if file.lower().endswith(".ipynb"):
                    paths.append(os.path.join(root, file))

    if len(paths) == 0:
        print("No Notebooks found in input %s" % input)
        return

    c = Config()
    c.verbose = verbose
    c.NotebookExporter.preprocessors = [
        AddTags,
        ProcessExercises,
        RemoveSolutions,
        ClearOutputPreprocessor,
    ]
    converter = NotebookExporter(config=c)


    for file in paths:
        opath = os.path.relpath(file, folder) 
        out_file = os.path.join(output, opath)
        out_dir = os.path.dirname(out_file)
        os.makedirs(out_dir, exist_ok=True)
        if os.path.isfile(out_file):
            if not force:
                print(f"Skipping {file} because {out_file} already exists")
                continue
            else:
                print(f"Overwriting {out_file}")

        print(f"Converting '{file}' into '{out_file}'")
        notebook = nbformat.read(file, as_version=4)
        resources = {}
        resources["verbose"] = verbose
        (output_text, _) = converter.from_notebook_node(notebook, resources)

        with open(out_file, "w") as f:
            f.write(output_text)

