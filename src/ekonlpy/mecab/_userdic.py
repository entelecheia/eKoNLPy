import os
import subprocess
from collections import namedtuple
from pathlib import Path

import pandas as pd

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
    def __init__(self, userdic_path=None):
        import mecab_ko_dic

        if userdic_path:
            self.load_userdic(userdic_path)
        else:
            self.userdic = {}
        self.dicdir = mecab_ko_dic.DICDIR
        self.left_ids = self.load_context_ids("left-id.def")
        self.right_ids = self.load_context_ids("right-id.def")

    def load_context_ids(self, id_file):
        id_file = os.path.join(self.dicdir, id_file)
        context_ids = []
        with open(id_file, "r", encoding="utf-8") as f:
            for line in f:
                id, vals = line.split()
                entry = ContextEntry(id, *vals.split(","))
                context_ids.append(entry)
        return context_ids

    def find_left_context_id(self, search):
        for entry in self.left_ids:
            if entry.pos == search.pos and entry.semantic == search.semantic:
                return entry.id

    def find_right_context_id(self, search):
        for entry in self.right_ids:
            if (
                entry.pos == search.pos
                and entry.semantic == search.semantic
                and entry.has_jongseong == search.has_jongseong
            ):
                return entry.id

    def load_userdic(self, userdic_path):
        userdic_path = Path(userdic_path)

        if userdic_path.is_dir():
            self.userdic = {}
            for f in userdic_path.glob("*.csv"):
                df = pd.read_csv(f, names=DicEntry._fields)
                dic = {e.surface: e for e in iternamedtuples(df)}
                self.userdic = {**self.userdic, **dic}
        else:
            df = pd.read_csv(userdic_path, names=DicEntry._fields)
            self.userdic = {e.surface: e for e in iternamedtuples(df)}
        print(" No. of user dictionary entires loaded: %d" % len(self.userdic))

    def add_entry_to_userdic(
        self, surface, pos="NNP", semantic="*", reading=None, cost=1000
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

    def adjust_costs(self, cost=1000):
        for surface, entry in self.userdic.items():
            self.userdic[surface] = entry._replace(cost=cost)

    def save_userdic(self, save_path):
        if len(self.userdic) > 0:
            df = pd.DataFrame(self.userdic.values())
            df.to_csv(save_path, header=False, index=False)
            self.userdic_path = save_path
            print("Saved the userdic to {}".format(save_path))
        else:
            print("No userdic to save...")

    def build_userdic(self, built_userdic_path, userdic_path=None):
        if userdic_path:
            self.userdic_path = userdic_path
        args = '-d "{}" -u "{}" {}'.format(
            self.dicdir, built_userdic_path, self.userdic_path
        )
        # print(args)
        subprocess.run(["fugashi-build-dict", args])
