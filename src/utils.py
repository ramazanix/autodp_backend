from pathlib import Path
import shutil
from hashlib import shake_256
from datetime import datetime


def hash_file_name(filename: str):
    return shake_256(
        (filename + datetime.now().strftime("%m/%d/%Y, %H:%M:%S:%f")).encode()
    ).hexdigest(8)


def clear_dir(dir_path: str) -> None:
    dir_path = Path(dir_path)
    if dir_path.exists() and dir_path.is_dir():
        shutil.rmtree(dir_path)
