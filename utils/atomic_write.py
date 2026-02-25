import contextlib
import os
import tempfile
from pathlib import Path


@contextlib.contextmanager
def atomic_write(filepath: str | Path, mode: str = "w", encoding: str | None = "utf-8"):
    """
    Context manager for atomic file writes.
    Yields a temporary file; on success, atomically replaces the target file.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create temp file in the same directory to ensure they are on the same filesystem
    # (os.replace across different filesystems is not atomic)
    fd, temp_path = tempfile.mkstemp(dir=path.parent, prefix=f".tmp_{path.name}_")

    try:
        if "b" in mode:
            with open(fd, mode) as f:
                yield f
        else:
            with open(fd, mode, encoding=encoding) as f:
                yield f

        # Atomic replace
        os.replace(temp_path, path)
    except Exception as e:
        os.remove(temp_path)
        raise e
