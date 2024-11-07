from nbformat import NotebookNode
from papermill.engines import NBClientEngine
from nbconvert.preprocessors.base import Preprocessor
from traitlets import List
from urnc.logger import log


class ExecutePreprocessor(Preprocessor):
    supported_kernels = List(["python3"], help="List of supported kernels").tag(
        config=True
    )

    def execute_notebook(self, nb: NotebookNode):
        metadata = nb.get("metadata", {})
        kernelspec = metadata.get("kernelspec", {})
        kernel_name = kernelspec.get("name", "python3")
        if kernel_name not in self.supported_kernels:
            log(f"Kernel {kernel_name} not supported. Skipping execution of notebook.")
            return nb
        nb["metadata"]["papermill"] = {}
        engine = NBClientEngine()
        ex_nb = engine.execute_notebook(nb, "python3")
        return ex_nb

    def preprocess(self, nb, resources):
        filename = resources.get("filename", None)
        if filename:
            log(f"Executing notebook {filename}")

        ex_nb = self.execute_notebook(nb)
        return ex_nb, resources
