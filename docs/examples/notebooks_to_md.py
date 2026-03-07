import subprocess
from pathlib import Path

NB_FOLDERS_DIR = Path(__file__).parent

for path in NB_FOLDERS_DIR.iterdir():
    if not path.is_dir():
        continue
    for nb_file in path.iterdir():
        if nb_file.suffix != ".ipynb":
            continue
        print(f"Converting `{nb_file}`.")
        subprocess.run(
            [
                "uv",
                "run",
                "jupyter",
                "nbconvert",
                "--to=markdown",
                str(nb_file),
                "--TagRemovePreprocessor.enabled=True",
                "--TagRemovePreprocessor.remove_all_outputs_tags=remove_output",
            ],
            check=True,
        )
