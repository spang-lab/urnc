# Put help target first so that "make" without argument is like "make help".
help:
	sphinx-build -M help source build

.PHONY: help Makefile

# The % and $@ are used in Makefile for pattern matching and automatic variable
# substitution, respectively. They provide a way to write generic rules for
# targets. For example, if you have two targets html and latexpdf that you
# usually build, you could write:
#
# html: Makefile
#     sphinx-apidoc -o ./source ../urnc
#     @sphinx-build -M html "source" "build"
# latexpdf: Makefile
#     sphinx-apidoc -o ./source ../urnc
#     @sphinx-build -M latexpdf "source" "build"
#
# However, this approach requires you to write a new rule for each new target,
# which can become tedious if you have many targets. The % and $@ approach is
# more flexible and requires less maintenance.
%: Makefile
	sphinx-apidoc -o ./source ../urnc
	sphinx-build -b $@ source build
