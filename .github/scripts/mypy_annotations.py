"""Convert mypy diagnostics into GitHub Actions annotations."""

import re
import sys
from pathlib import Path


def escape(value: str, *, property_value: bool = False) -> str:
    value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    if property_value:
        value = value.replace(":", "%3A").replace(",", "%2C")
    return value


pattern = re.compile(r"^(.*?):(\d+):(\d+): (error|note|warning): (.*)$")
for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    match = pattern.match(line)
    if match:
        path, line_number, column, severity, message = match.groups()
        level = {"error": "error", "warning": "warning", "note": "notice"}[severity]
        print(f"::{level} file={escape(path, property_value=True)},line={line_number},col={column}::{escape(message)}")
