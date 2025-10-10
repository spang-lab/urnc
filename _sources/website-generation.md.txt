# Website Generation

urnc itself does not provide any functions for creating static websites; however, it can be easily used as a preprocessing step for other website generators, such as [jupyter-book](https://jupyterbook.org/en/stable/intro.html#) or [quarto](https://quarto.org/).

The following code snippet shows an example where urnc is used in combination with jupyter-book to produce a static course website, both with and without solutions.

```bash
# Initialize a new example course
urnc init --template=full --student=student.git 'Example Course'
cd example_course

# Create a homepage and table of contents for the website
echo "# Example Course"             >  lectures/index.md
echo "Homepage of Example Course"   >> lectures/index.md
echo "format: jb-book"              >  lectures/_toc.yml
echo "root: index.md"               >> lectures/_toc.yml
echo "chapters:"                    >> lectures/_toc.yml
echo "- file: week1/lecture1.ipynb" >> lectures/_toc.yml
echo "- file: week1/lecture2.ipynb" >> lectures/_toc.yml

# Create the student version in ./out
urnc student

# Install Jupyter Book
pip install -U jupyter-book

# Build the website from the admin version in: ./lectures/_build/html
jupyter-book build lectures

# Build the website from the student version in: ./out/lectures/_build/html
jupyter-book build out/lectures
```
