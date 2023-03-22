#!/usr/bin/env python3
import nbformat
import re
import os
import sys
import enum
import argparse

from traitlets.config import Config
from nbconvert.preprocessors.base import Preprocessor
from nbconvert.preprocessors.clearoutput import ClearOutputPreprocessor
from nbconvert.exporters.notebook import NotebookExporter
from nbconvert.writers.files import FilesWriter

class Keywords(str, enum.Enum):
    EXERCISE_START = '### Exercise'
    SOLUTION = '### Solution'
    SKELETON = '### Skeleton'
    SOLUTION_END = '###'

class Tags(str, enum.Enum):
    SOLUTION = 'solution'
    EXERCISE = 'exercise'
    SKELETON = 'skeleton'


def has_tag(cell, tag):
    ltag = tag.lower()
    if ('tags' not in cell.metadata):
        return False
    for tag in cell.metadata.tags:
        if tag.lower() == ltag:
            return True
    return False

def set_tag(cell, tag):
    if(has_tag(cell, tag)):
       return
    if ('tags' not in cell.metadata):
        cell.metadata.tags = []
    cell.metadata.tags.append(tag)


def has_header(cell):
    if(cell.cell_type != 'markdown'):
        return False
    if(re.search('^#', cell.source)):
        return True
    if(re.search('\n#', cell.source)):
        return True
    return False

def process_comments(cell):
    text = cell.source
    lines = text.split('\n')

    last_tag = None
    found_tag = False
    tlines = []
    for line in lines:
        if(re.match(Keywords.SOLUTION, line,  re.IGNORECASE)):
            last_tag = Tags.SOLUTION
            found_tag = True
            continue  
        if(re.match(Keywords.SKELETON, line,  re.IGNORECASE)):
            last_tag = Tags.SKELETON
            found_tag = True
            continue
        if(re.match(Keywords.SOLUTION_END, line,  re.IGNORECASE)):
            last_tag = None
            continue
        tlines.append((line, last_tag))
    if(not found_tag):
        return None
    slines = []
    for (line, tag) in tlines:
        if(tag is None):
            slines.append(line)
        if(tag == Tags.SOLUTION):
            continue
        if(tag == Tags.SKELETON):
            uncom = re.sub(r'^#\s?', '', line) 
            slines.append(uncom)
    cell.source = '\n'.join(slines)

    return cell

class CheckAndAddTags(Preprocessor):
    def preprocess(self, notebook, resources):
        in_exercise = False
        for cell in notebook.cells:
            if(re.search(Keywords.EXERCISE_START, cell.source, re.IGNORECASE)):
                in_exercise = True
            elif(has_header(cell)):
               in_exercise = False
            if(not in_exercise):
                continue
            set_tag(cell, Tags.EXERCISE)
            

        return notebook, resources



class RemoveSolutions(Preprocessor):
    def preprocess(self, notebook, resources):
        cells = []
        for cell in notebook.cells:
            if(has_tag(cell, Tags.SOLUTION)):
                cell = process_comments(cell)
            if(cell is not None):
                cells.append(cell)
        notebook.cells = cells
        return notebook, resources
        


def main():
    parser = argparse.ArgumentParser(description="Convert Notebooks for UR FIDS Courses")
    parser.add_argument('input', type=str, help="The input folder, it will be searched recursively")
    parser.add_argument('-i', '--ext', type=str, help="The output file extension, use '' for inplace conversion", default=".out")
    parser.add_argument('-f', '--force', help="Overwrite existing files", action='store_true')

    args = parser.parse_args()
    print(args)

    paths = []
    if(os.path.isfile(args.input)):
        paths.append(args.input)
    else:
        for root, dirs, files in os.walk(args.input, topdown= True):
            dirs[:] = [d for d in dirs if not d[0] == '.']
            for file in files:
                if(file.lower().endswith('.ipynb')):
                    paths.append(os.path.join(root, file))
    
    if (len(paths) == 0):
        print("No Notebooks found in input %s" % args.input)
        return

    c = Config()
    c.NotebookExporter.preprocessors = [CheckAndAddTags, RemoveSolutions, ClearOutputPreprocessor]
    converter = NotebookExporter(config = c)

    for file in paths:
        (basepath, filename) = os.path.split(file)
        (basename, _) = os.path.splitext(filename)
        out_file = os.path.join(basepath, "%s%s.ipynb" % (basename, args.ext))
        if(os.path.isfile(out_file)):
            if(not args.force):
                print("Skipping %s because %s already exists" % (file, out_file))
                continue
            else:
                print("Overwriting %s" % out_file)

        print("Converting '%s' into '%s'" % (file, out_file))
        notebook = nbformat.read(file, as_version=4)
        (output, _) = converter.from_notebook_node(notebook)
        
        with open(out_file, "w") as f:
            f.write(output)




if __name__ == "__main__":
    main()


