# ./source/service/file_svc.py

"""
    Utility module for handling file IO
"""

# Standard library
from hashlib import sha256
import logging
import os
from pathlib import Path
import shutil

# Local imports
from source.constants import *

# Third-party packages
from tqdm import tqdm


def dir_is_empty(path: Path) -> bool:
    if not path.is_dir():
        raise NotADirectoryError("'path' must be a pathlib Path object that points to a directory")
    return not any(path.iterdir())


def file_write(path: Path, data: str, overwrite=False) -> None:
    """
    Attempts to write data to the file at the specified path, raising
    an exception if the file already exists.

    :param path: (str) Path to file.
    :param data: (str) Data to write to the file.
    :param overwrite: (bool) Overwrite if file exists
    :return : None
    :raises FileExistsError: if the file already exists
    :raises IOError: if an error occurs with the write function
    """
    if path.exists() and not overwrite:
        raise FileExistsError(f"The file '{path}' already exists")
    with path.open('w') as file:
        file.write(data)


def file_write_bytes(path: Path, data: bytes, overwrite=False) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"The file '{path}' already exists")
    with path.open('wb') as file:
        file.write(data)


def file_read(path: Path) -> str:
    """
    Reads data from file at 'path'
    :param path: Path of file to be read
    :return: string containing file data
    """
    if not path.exists():
        raise FileNotFoundError(f"The file '{path}' cannot be found")
    with path.open('r') as file:
        return file.read()


def file_read_bytes(path: Path) -> bytes:
    if not path.exists():
        raise FileNotFoundError(f"The file '{path}' cannot be found")
    with path.open('rb') as file:
        return file.read()


def get_files_from_path(root: Path, recursive: bool = False, glob_pattern: str = '*') -> list[Path]:
    if recursive:
        return list(root.rglob(glob_pattern))
    else:
        return list(root.glob(glob_pattern))


def get_file_type(path: Path) -> str:
    if not path.is_file():
        raise TypeError(f"'{path}' is not recognized as a valid file")
    if path.suffix in VIDEO_EXTENSIONS:
        return 'video'
    else:
        return ''


def hash_sha256(path: Path):
    hasher = sha256()
    file_size = os.path.getsize(path)

    with path.open('rb') as file:
        chunk_size = 65536  # 64kb
        with tqdm(total=file_size, unit='MB', unit_scale=True, position=0) as progress_bar:
            max_desc_width = 80 - len(' [Hashing]')
            file_name = os.path.basename(path)
            file_name = file_name[:max_desc_width].ljust(max_desc_width)
            progress_bar.set_description(f'[Hashing] {file_name}')
            for chunk in iter(lambda: file.read(chunk_size), b''):
                hasher.update(chunk)
                progress_bar.update(len(chunk))
    sha256_hash = hasher.hexdigest()
    return sha256_hash


def make_dir(path: Path):
    if not path.exists():
        path.mkdir()
        logging.info(f"Directory '{path}' created")
    else:
        logging.info(f"Directory '{path}' already exists")


def make_dirs(dest_dir: Path) -> list[Path]:
    dirs = []
    while not dest_dir.exists():
        dirs.append(dest_dir)
        dest_dir = dest_dir.parent
    for directory in reversed(dirs):
        make_dir(directory)
    return dirs


def mimic_folder(src_tree: Path, dest_tree: Path) -> None:
    def integer_generator():
        num = 0
        while True:
            yield num
            num += 1
    gen = integer_generator()
    for dirpath, _, filenames in os.walk(src_tree):
        relative_to_src = Path(dirpath).relative_to(src_tree)
        Path(dest_tree, relative_to_src).mkdir(exist_ok=True)
        for name in filenames:
            dest_file_path = dest_tree / relative_to_src / name
            dummy_file_data = str(next(gen))
            file_write(dest_file_path, dummy_file_data, overwrite=False)


def move_file(src: Path, dst: Path, overwrite=False) -> None:
    if dst.exists():
        if not overwrite:
            msg = f"Cannot move file: '{dst}' already exists"
            logging.error(msg)
            raise FileExistsError(msg)
        logging.warning(f"Overwriting '{dst}' with '{src}'")
    shutil.move(src, dst)
    logging.info(f"Moved '{src}' to '{dst}'")


def parse_glob_string(path_string: str) -> (Path, str):
    path = Path(path_string)
    if '*' in path_string:
        return path.parent, path.name
    else:
        return path, '*'


def path_is_writable(path: Path) -> bool:
    return os.access(path, os.W_OK)


def path_is_readable(path: Path) -> bool:
    return os.access(path, os.R_OK)


def remove_dirs(dirs: list[Path]):
    for directory in dirs:
        try:
            directory.rmdir()
        except FileNotFoundError:
            msg = f"Cannot remove directory: '{directory}' does not exist"
            logging.info(msg)
            raise
        except OSError:
            msg = f"Cannot remove directory: '{directory}' is not empty"
            logging.info(msg)
            raise
