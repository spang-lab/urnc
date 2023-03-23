#!/usr/bin/env python3
import nbformat
import re
import os
import sys
import enum
import argparse
import inspect
from traitlets.config import Config
from nbconvert.preprocessors.base import Preprocessor
from nbconvert.preprocessors.clearoutput import ClearOutputPreprocessor
from nbconvert.exporters.notebook import NotebookExporter


class Keywords(str, enum.Enum):
    EXERCISE_START = r'^### Exercise `([\w-]+)`'
    SOLUTION = '### Solution'
    SKELETON = '### Skeleton'
    SOLUTION_END = '###'

class Tags(str, enum.Enum):
    SOLUTION = 'solution'
    EXERCISE = 'exercise'
    EXERCISE_START = 'exercise-start'
    SKELETON = 'skeleton'

def critical_error(text):
    RED   = "\033[1;31m"  
    RESET = "\033[0;0m"
    print("%sCritical Error: %s %s" %(RED, text, RESET))
    sys.exit(1)


def cell_preview(cell):
    short = cell.source[0:100]
    text = re.sub(r'[\s\n]+', ' ', short)
    return "'%s...'" % text[0:50]

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
    if(len(slines) == 0):
        return None
    cell.source = '\n'.join(slines)

    return cell

def end_exercise(exercise_id, has_solution):
    if(exercise_id is None):
        return
    if(not has_solution):
        critical_error("Exercise '%s' has no solution" % exercise_id)



class CheckAndAddTags(Preprocessor):
    def preprocess(self, notebook, resources):
        verbose = resources['verbose']
        
        exercise_ids = set() 
        exercise_id = None 
        has_solution = False
        
        for cell in notebook.cells:
            if(match := re.search(Keywords.EXERCISE_START, cell.source, re.IGNORECASE)):
                end_exercise(exercise_id, has_solution)
                has_solution = False
                exercise_id = match.group(1)
                set_tag(cell, Tags.EXERCISE_START)
                if(exercise_id in exercise_ids):
                    critical_error("Duplicate Exercise id '%s'" % exercise_id)
                else:
                    exercise_ids.add(exercise_id)
                if(verbose):
                    print("Detected Exercise '%s'" % exercise_id)
            elif(has_header(cell) and exercise_id is not None):
                end_exercise(exercise_id, has_solution)
                exercise_id = None 
            if(exercise_id is None):
                continue
            set_tag(cell, Tags.EXERCISE)
            if(re.search(Keywords.SOLUTION, cell.source, re.IGNORECASE) or has_tag(cell, Tags.SOLUTION)):
                if(verbose):
                    print(" Detected Solution cell %s" % cell_preview(cell))
                set_tag(cell, Tags.SOLUTION)
                has_solution = True
        end_exercise(exercise_id, has_solution)
        return notebook, resources



class RemoveSolutions(Preprocessor):
    def preprocess(self, notebook, resources):
        verbose = resources['verbose']
        cells = []
        for cell in notebook.cells:
            if(has_tag(cell, Tags.SOLUTION)):
                cell = process_comments(cell)
            if(cell is not None):
                cells.append(cell)
        notebook.cells = cells
        return notebook, resources

class ProcessExercises(Preprocessor):
    def preprocess(self, notebook, resources):
        for cell in notebook.cells:
            if(has_tag(cell, Tags.EXERCISE_START)):
                html = """
                    <div class="alert alert-block alert-info">
                        <b>Tip:</b> Use blue boxes (alert-info) for tips and notes. 
                        If it’s a note, you don’t have to include the word “Note”.
                    </div>
                """
                cell.source = inspect.cleandoc(html)
        return notebook, resources
        


def main():
    parser = argparse.ArgumentParser(description="Convert Notebooks for UR FIDS Courses")
    parser.add_argument('input', type=str, help="The input folder, it will be searched recursively")
    parser.add_argument('-i', '--ext', type=str, help="The output file extension, use '' for inplace conversion", default=".out")
    parser.add_argument('-f', '--force', help="Overwrite existing files", action='store_true')
    parser.add_argument('-v', '--verbose', help='Verbose Log output', action='store_true')

    args = parser.parse_args()

    paths = []
    if(os.path.isfile(args.input)):
        paths.append(args.input)
    else:
        for root, dirs, files in os.walk(args.input, topdown= True):
            dirs[:] = [d for d in dirs if not d[0] == '.']
            for file in files:
                if(file.lower().endswith("%s.ipynb" % args.ext)):
                   continue
                if(file.lower().endswith('.ipynb')):
                    paths.append(os.path.join(root, file))
    
    if (len(paths) == 0):
        print("No Notebooks found in input %s" % args.input)
        return

    c = Config()
    c.verbose = args.verbose
    c.NotebookExporter.preprocessors = [CheckAndAddTags, ProcessExercises, RemoveSolutions, ClearOutputPreprocessor]
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
        resources = {}
        resources['verbose'] = args.verbose
        (output, _) = converter.from_notebook_node(notebook, resources)
        
        with open(out_file, "w") as f:
            f.write(output)




if __name__ == "__main__":
    main()


