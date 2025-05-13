# Collection of ideas for urnc v3.0.0

## 1. Hide internal functions

We should hide internal functions, e.g. by prefixing them with an underscore `_`.

Yes, I know, you don't like it.
And yes, I also think it's ugly.
But it's the convention in Python and we want others to use the package.
I don't want a package like [datascience](https://github.com/data-8/datascience) with tousands of undocumented functions where noone knows which ones are important and which ones are not.

Alternative: we make all our submodules private, e.g. by moving them into `_libs` or `_internal`. This is how `pandas` or `scipy` do it.

## 2. Use verbs for function names

Example: `urnc.config.default_config()` should be `urnc.config.get_default_config()` or `urnc.config.init_default_config()`.

This prevents the annoying scenario where `default_config = default_config()` causes the language server to complain about "unbound variables".

## 3. Export API functions flat at the toplevel

Currently, using urnc as python package looks like this:

```py
import urnc
urnc.init.init()
urnc.convert.convert()
urnc.version.version()
```

or this

```py
from urnc.init import init
from urnc.convert import convert
from urnc.version import version
init()
convert()
version()
```

That's ugly and autocompletion after typing `urnc.SUBMODULE.` is bad, because we have so many internal functions. I would propose to do it as follows:

```py
import urnc
urnc.init()
urnc.convert()
urnc.version()
```

or like this:

```py
from urnc import init, convert, version
init()
convert()
version()
```

I.e. `urnc.` holds our public API and all submodules are private (see [1. Hide internal functions](#1-hide-internal-functions)).

## 4. Remove jupyter libs and treat notebooks as jsons

This whole Notebook-Processor subclassing is incredible ugly and hard to read.
It would be so much nicer to just have a few converions functions, like

- `clear_outputs(Notebook) -> Notebook`
- `remove_solutions(Notebook) -> Notebook`
- `uncomment_skeletons(Notebook) -> Notebook`
- `remove_skeletons(Notebook) -> Notebook`
- `fix_image_paths(Notebook) -> Notebook`
- `execute_solutions(Notebook) -> Notebook`

And call them in the right order.

Then we could even think about providing an interface for specifying conversion-steps directly, e.g. as:

```
urnc convert --steps='remove_solutions,uncomment_skeletons,clear_outputs'
```

And we could even allow the definition of custom targets in the config.yaml, e.g. like this:

```yaml
targets:
  student2:
    steps: 'remove_solutions,uncomment_skeletons' # outputs not removed
```
