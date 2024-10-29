from nbformat import NotebookNode
from papermill.engines import NBClientEngine


def execute_notebook(config: dict, nb: NotebookNode):
    engine = NBClientEngine()
    ex_nb = engine.execute_notebook(nb, "python3")
    return ex_nb
