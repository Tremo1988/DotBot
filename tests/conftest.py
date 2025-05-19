import sys, pathlib

# Aggiunge la root del progetto al PYTHONPATH, così "import modules" funziona
root = pathlib.Path(__file__).parent.parent.resolve()
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
