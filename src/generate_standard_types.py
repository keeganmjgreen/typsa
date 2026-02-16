import csv
from pathlib import Path

import pydantic
import pypsa
from pydantic.alias_generators import to_pascal


class _StandardTypeRow(pydantic.BaseModel):
    name: str


def _write_literal_type(literal_name: str, literal_members: list[str]) -> str:
    return f"type {literal_name} = Literal[\n    {'\n    '.join([f'"{member}",' for member in literal_members])}\n]\n"


def main() -> None:
    text = "from typing import Literal"
    text += "\n\n"

    for component_name in ["line", "transformer"]:
        standard_types_csv_path = Path(
            pypsa.__file__.removesuffix("__init__.py"),
            "data",
            "standard_types",
            f"{component_name}_types.csv",
        )
        csv_reader = csv.DictReader(standard_types_csv_path.open())
        standard_types = [_StandardTypeRow.model_validate(row) for row in csv_reader]
        standard_type_names = [x.name for x in standard_types]

        text += _write_literal_type(
            f"Standard{to_pascal(component_name)}Type", standard_type_names
        )
        Path("standard_types.py").write_text(text)


if __name__ == "__main__":
    main()
