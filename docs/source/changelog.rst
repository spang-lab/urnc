Changelog
=========

v1.5.0
------
Added the option to provide an `"after"` and `"until"` value for every `git.exclude` config entry. I.e. something like `{pattern: assignments/sheet4.ipynb, after: 2023-12-04}` is now possible.

v1.4.0
------
Added support for environment variables inside config option `git.student`, i.e. a value like "https://urncbot:{URNC_ACCESS_TOKEN_STUDENT_REPO}@github.com/spang-lab/urnc-example-course-public.git" is now valid.
