import logging
import os
import shutil
import subprocess
import sys
from collections import namedtuple
from collections.abc import Iterator
from pathlib import Path
from typing import Optional

import mecab_ko_dic
import pandas as pd

logger = logging.getLogger(__name__)

DicEntry = namedtuple(
    "DicEntry",
    [
        "surface",
        "left_id",
        "right_id",
        "cost",
        "pos",
        "semantic",
        "has_jongseong",
        "reading",
        "type",
        "start_pos",
        "end_pos",
        "expression",
    ],
    defaults=[None, None, None, None, "NNP", "*", "T", None, "*", "*", "*", "*"],
)

ContextEntry = namedtuple(
    "ContextEntry",
    [
        "id",
        "pos",
        "semantic",
        "has_jongseong",
        "reading",
        "type",
        "start_pos",
        "end_pos",
        "expression",
    ],
    defaults=[None, "*", "*", "*", "*", "*", "*", "*"],
)


def iternamedtuples(  # type: ignore[no-any-unimported]
    df: pd.DataFrame,
) -> Iterator[DicEntry]:
    """Iterate over the rows of a DataFrame as DicEntry namedtuples.

    :param df: A DataFrame whose columns match the DicEntry fields
    :return: An iterator of DicEntry namedtuples
    """
    for row in df.itertuples():
        yield DicEntry(*row[1:])


def has_jongseong(c: str) -> bool:
    """Check whether the last character of the given string has a final consonant (jongseong).

    :param c: The string to check
    :return: True if the last character has jongseong, False otherwise
    """
    return int((ord(c[-1]) - 0xAC00) % 28) != 0


class MecabDicConfig:
    """Configuration and management of a MeCab user dictionary."""

    userdic: dict[str, DicEntry]
    dicdir: str = mecab_ko_dic.DICDIR
    left_ids: list[ContextEntry]
    right_ids: list[ContextEntry]
    userdic_path: Optional[str] = None

    def __init__(self, userdic_path: Optional[str] = None):
        """Initialize the configuration and load context IDs and the user dictionary.

        :param userdic_path: Path to a user dictionary CSV file or a directory of CSV files, if any
        """
        self.userdic_path = userdic_path
        if userdic_path:
            self.load_userdic(userdic_path)
        else:
            self.userdic = {}
        self.dicdir = mecab_ko_dic.DICDIR
        self.left_ids = self.load_context_ids("left-id.def")
        self.right_ids = self.load_context_ids("right-id.def")

    def load_context_ids(self, id_file: str) -> list[ContextEntry]:
        """Load a context ID definition file from the system dictionary.

        :param id_file: Name of the context ID file (e.g. "left-id.def")
        :return: A list of ContextEntry namedtuples
        """
        id_file = os.path.join(self.dicdir, id_file)
        context_ids = []
        with open(id_file, encoding="utf-8") as f:
            for line in f:
                entry_id, vals = line.split()
                entry = ContextEntry(entry_id, *vals.split(","))
                context_ids.append(entry)
        return context_ids

    def find_left_context_id(self, search: DicEntry) -> Optional[str]:
        """Find the left context ID matching the given dictionary entry.

        :param search: The dictionary entry to match
        :return: The matching left context ID, or None if not found
        """
        for entry in self.left_ids:
            if entry.pos == search.pos and entry.semantic == search.semantic:
                return entry.id
        return None

    def find_right_context_id(self, search: DicEntry) -> Optional[str]:
        """Find the right context ID matching the given dictionary entry.

        :param search: The dictionary entry to match
        :return: The matching right context ID, or None if not found
        """
        for entry in self.right_ids:
            if (
                entry.pos == search.pos
                and entry.semantic == search.semantic
                and entry.has_jongseong == search.has_jongseong
            ):
                return entry.id
        return None

    def load_userdic(self, userdic_path: str) -> None:
        """Load user dictionary entries from a CSV file or a directory of CSV files.

        :param userdic_path: Path to a user dictionary CSV file or a directory containing CSV files
        """
        userdic_path_ = Path(userdic_path)

        if userdic_path_.is_dir():
            self.userdic = {}
            for f in userdic_path_.glob("*.csv"):
                df = pd.read_csv(f, names=DicEntry._fields)
                dic = {e.surface: e for e in iternamedtuples(df)}
                self.userdic = {**self.userdic, **dic}
        else:
            df = pd.read_csv(userdic_path_, names=DicEntry._fields)
            self.userdic = {e.surface: e for e in iternamedtuples(df)}
        logger.info("No. of user dictionary entires loaded: %d", len(self.userdic))

    def add_entry_to_userdic(
        self,
        surface: str,
        pos: str = "NNP",
        semantic: str = "*",
        reading: Optional[str] = None,
        cost: int = 1000,
    ) -> None:
        """Add a new entry to the user dictionary, resolving its context IDs.

        :param surface: The surface form of the entry
        :param pos: The part-of-speech tag of the entry
        :param semantic: The semantic field of the entry
        :param reading: The reading of the entry; defaults to the surface form
        :param cost: The word-occurrence cost of the entry
        """
        entry = DicEntry(
            surface=surface,
            cost=cost,
            pos=pos,
            semantic=semantic,
            has_jongseong={True: "T", False: "F"}.get(has_jongseong(surface)),
            reading=surface if reading is None else reading,
        )
        entry = entry._replace(
            left_id=self.find_left_context_id(entry),
            right_id=self.find_right_context_id(entry),
        )
        self.userdic[surface] = entry

    def adjust_context_ids(self) -> None:
        """Recompute the left and right context IDs of all user dictionary entries."""
        for entry in self.userdic.values():
            entry = entry._replace(
                left_id=self.find_left_context_id(entry),
                right_id=self.find_right_context_id(entry),
            )
            self.userdic[entry.surface] = entry

    def adjust_costs(self, cost: int = 1000) -> None:
        """Set the word-occurrence cost of all user dictionary entries.

        :param cost: The cost to assign to every entry
        """
        for surface, entry in self.userdic.items():
            self.userdic[surface] = entry._replace(cost=cost)

    def save_userdic(self, save_path: str) -> None:
        """Save the user dictionary entries to a CSV file.

        :param save_path: Path of the CSV file to write
        """
        if len(self.userdic) > 0:
            df = pd.DataFrame(self.userdic.values())
            df.to_csv(save_path, header=False, index=False)
            self.userdic_path = save_path
            logger.info("No. of user dictionary entires saved: %d", len(self.userdic))
            logger.info("User dictionary saved to %s", save_path)
        else:
            logger.warning("No user dictionary entries to save.")

    @staticmethod
    def _build_dict_executable() -> str:
        executable = shutil.which("fugashi-build-dict")
        if executable:
            return executable
        binary = "fugashi-build-dict.exe" if os.name == "nt" else "fugashi-build-dict"
        return os.path.join(os.path.dirname(sys.executable), binary)

    @staticmethod
    def _build_dict_path(path: str) -> str:
        # The MeCab dictionary compiler eats backslashes as escape characters
        # in its arguments, so Windows paths must use forward slashes.
        return path.replace("\\", "/") if os.name == "nt" else path

    def build_userdic(
        self, built_userdic_path: str, userdic_path: Optional[str] = None
    ) -> None:
        """Compile the user dictionary CSV into a binary MeCab user dictionary.

        :param built_userdic_path: Path of the compiled user dictionary to create
        :param userdic_path: Path to the user dictionary CSV; defaults to the path set by save_userdic()
        :raises ValueError: If no user dictionary path is set
        """
        if userdic_path:
            self.userdic_path = userdic_path
        if not self.userdic_path:
            raise ValueError(  # noqa: TRY003
                "userdic_path is not set; call save_userdic() first or pass userdic_path."
            )
        cmd = [
            self._build_dict_executable(),
            "-d",
            self._build_dict_path(self.dicdir),
            "-u",
            self._build_dict_path(built_userdic_path),
            self._build_dict_path(self.userdic_path),
        ]
        subprocess.run(cmd, check=True)  # noqa: S603
