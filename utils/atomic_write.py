"""
Utility for atomic file writing.
"""

import contextlib
import os
import tempfile
from pathlib import Path


@contextlib.contextmanager
def atomic_write(filepath: str | Path, mode: str = "w", encoding: str | None = "utf-8"):
    """Context manager for atomic file writes.

    Args:
        filepath (str | Path): The destination path for the file.
        mode (str, optional): The file open mode. Defaults to "w".
        encoding (str | None, optional): The file encoding. Defaults to "utf-8".

    Yields:
        io.TextIOWrapper | io.BufferedWriter: The temporary file object to write to.

    Raises:
        Exception: Re-raises any exception encountered during the file write.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(dir=path.parent, prefix=f".tmp_{path.name}_")

    try:
        if "b" in mode:
            with open(fd, mode) as f:
                yield f
        else:
            with open(fd, mode, encoding=encoding) as f:
                yield f

        os.replace(temp_path, path)
    except Exception as e:
        os.remove(temp_path)
        raise e
