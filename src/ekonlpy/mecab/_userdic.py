import logging
import os
import subprocess
from collections import namedtuple
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

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


def iternamedtuples(df):
    Row = namedtuple("Row", df.columns)
    for row in df.itertuples():
        yield Row(*row[1:])


def has_jongseong(c):
    return int((ord(c[-1]) - 0xAC00) % 28) != 0


class MecabDicConfig:
    userdic: Dict[str, DicEntry] = {}
    dicdir: str = mecab_ko_dic.DICDIR
    left_ids: List[ContextEntry] = []
    right_ids: List[ContextEntry] = []

    def __init__(self, userdic_path: Optional[str] = None):
        if userdic_path:
            self.load_userdic(userdic_path)
        else:
            self.userdic = {}
        self.dicdir = mecab_ko_dic.DICDIR
        self.left_ids = self.load_context_ids("left-id.def")
        self.right_ids = self.load_context_ids("right-id.def")

    def load_context_ids(self, id_file: str) -> List[ContextEntry]:
        id_file = os.path.join(self.dicdir, id_file)
        context_ids = []
        with open(id_file, "r", encoding="utf-8") as f:
            for line in f:
                id, vals = line.split()
                entry = ContextEntry(id, *vals.split(","))
                context_ids.append(entry)
        return context_ids

    def find_left_context_id(self, search: DicEntry) -> Optional[str]:
        for entry in self.left_ids:
            if entry.pos == search.pos and entry.semantic == search.semantic:
                return entry.id

    def find_right_context_id(self, search: DicEntry) -> Optional[str]:
        for entry in self.right_ids:
            if (
                entry.pos == search.pos
                and entry.semantic == search.semantic
                and entry.has_jongseong == search.has_jongseong
            ):
                return entry.id

    def load_userdic(self, userdic_path: str):
        userdic_path_ = Path(userdic_path)

        if userdic_path_.is_dir():
            self.userdic = {}
            for f in userdic_path_.glob("*.csv"):
                df = pd.read_csv(f, names=DicEntry._fields)
                dic = {e.surface: DicEntry(*e) for e in iternamedtuples(df)}
                self.userdic = {**self.userdic, **dic}
        else:
            df = pd.read_csv(userdic_path_, names=DicEntry._fields)
            self.userdic = {e.surface: DicEntry(*e) for e in iternamedtuples(df)}
        logger.info("No. of user dictionary entires loaded: %d", len(self.userdic))

    def add_entry_to_userdic(
        self,
        surface: str,
        pos: str = "NNP",
        semantic: str = "*",
        reading: Optional[str] = None,
        cost: int = 1000,
    ):
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

    def adjust_context_ids(self):
        for entry in self.userdic.values():
            entry = entry._replace(
                left_id=self.find_left_context_id(entry),
                right_id=self.find_right_context_id(entry),
            )
            self.userdic[entry.surface] = entry

    def adjust_costs(self, cost: int = 1000):
        for surface, entry in self.userdic.items():
            self.userdic[surface] = entry._replace(cost=cost)

    def save_userdic(self, save_path: str):
        if len(self.userdic) > 0:
            df = pd.DataFrame(self.userdic.values())
            df.to_csv(save_path, header=False, index=False)
            self.userdic_path = save_path
            logger.info("No. of user dictionary entires saved: %d", len(self.userdic))
            logger.info("User dictionary saved to %s", save_path)
        else:
            logger.warning("No user dictionary entries to save.")

    def build_userdic(
        self, built_userdic_path: str, userdic_path: Optional[str] = None
    ):
        if userdic_path:
            self.userdic_path = userdic_path
        args = f'-d "{self.dicdir}" -u "{built_userdic_path}" {self.userdic_path}'
        # print(args)
        subprocess.run(["fugashi-build-dict", args])
