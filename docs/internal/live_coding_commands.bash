# 0. Install URNC
# ==========================
pip install --upgrade urnc

# 1. Initialize a New Course
# ==========================
urnc init --help
urnc init --template=full --url=.git_admin --student=.git_student 'My Course'
## Look at the ipynb files: source and gui --> Solution exists


# 2. Create the Student Version
# =============================
cd my_course
urnc student --help
urnc student
## Change git.student in config.yaml to ../student_local
rm -rf out
urnc student
## Compare the changes in Beyond Compare
cd ../student_local
git add .
git commit -m "Initial commit"
git push


# 3. Publish the Student Version
# ==============================

## Create two new repos on GitHub: a private one and a public one
## Set the remote for the private
## Run `urnc ci` locally to update the student repo

# 4. Convert Notebooks to other targets
# =====================================
cd lectures/week1/
urnc convert lecture1.ipynb -o stud.ipynb
urnc convert lecture1.ipynb -o stud.ipynb -s sol.ipynb
urnc convert lecture1.ipynb -t student:stud.ipynb -t solution:sol.ipynb
urnc convert --help


# 5. Check Notebooks
# =====================================
urnc check
urnc check --quiet
urnc check --quiet --image


# 6. Pull the Student Version
# ===========================

git clone https://github.com/toscm/urnc-showcase-public
## modify a file in the student repo
## modify the same file in the admin repo
## modify another file in the admin repo
cd urnc-showcase-public
git pull # error
urnc pull


# 7. Create a Github Action to publish the course automatically
# =============================================================

## Generate a personal access token with contents and workflow permissions
