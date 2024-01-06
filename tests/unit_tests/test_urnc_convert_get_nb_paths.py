import urnc

def test_get_nb_paths():
    nbs = urnc.convert.get_nb_paths(input="tests/inputs/minimal-course")
    nb_names = [nb.name for nb in nbs]
    assert all([len(nbs) >= 2,
                "urnc.ipynb" in nb_names,
                "fibonacci.ipynb" in nb_names])
