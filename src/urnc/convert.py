#!/usr/bin/env python3

from traitlets.config import Config
from nbconvert.preprocessors.base import Preprocessor
from nbconvert.preprocessors.clearoutput import ClearOutputPreprocessor
from nbconvert.exporters.notebook import NotebookExporter
from nbconvert.writers.files import FilesWriter
import nbformat
import re
import os
import sys
import enum

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
    input_folder = "."
    if(len(sys.argv) > 1):
        input_folder = sys.argv[1]

    paths = []
    if(os.path.isfile(input_folder)):
        paths.append(input_folder)
    else:
        for root, dirs, files in os.walk(input_folder, topdown= True):
            dirs[:] = [d for d in dirs if not d[0] == '.']
            for file in files:
                if(file.lower().endswith('.ipynb')):
                    paths.append(os.path.join(root, file))
    
    if (len(paths) == 0):
        print("No Notebooks found in input_folder %s" % input_folder)
        return

    c = Config()
    c.NotebookExporter.preprocessors = [CheckAndAddTags, RemoveSolutions, ClearOutputPreprocessor]
    c.FilesWriter.build_directory = "exercises"
    converter = NotebookExporter(config = c)

    for file in paths:
        print("Processing %s" % file)
        notebook = nbformat.read(file, as_version=4)
        (output, resources) = converter.from_notebook_node(notebook)
        writer = FilesWriter(config=c)
        (_, filename) = os.path.split(file)
        (basename, _) = os.path.splitext(filename)
        writer.write(output, resources, notebook_name=basename)

if __name__ == "__main__":
    main()


