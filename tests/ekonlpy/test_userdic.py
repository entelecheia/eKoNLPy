import os
import subprocess
import sys
from unittest import mock

import pytest

from ekonlpy import MecabDicConfig

USERDIC_ROW = "한국은행,1795,3558,1000,NNP,*,T,한국은행,*,*,*,*\n"


def test_build_userdic_invokes_fugashi_build_dict_with_split_args(tmp_path):
    csv_path = tmp_path / "user.csv"
    csv_path.write_text(USERDIC_ROW, encoding="utf-8")
    built_path = tmp_path / "user.dic"
    config = MecabDicConfig()

    with mock.patch("ekonlpy.mecab._userdic.subprocess.run") as run:
        config.build_userdic(str(built_path), userdic_path=str(csv_path))

    run.assert_called_once()
    cmd = run.call_args[0][0]
    assert os.path.basename(cmd[0]).startswith("fugashi-build-dict")
    assert cmd[1:] == [
        "-d",
        config.dicdir,
        "-u",
        str(built_path),
        str(csv_path),
    ]
    assert run.call_args[1].get("check") is True


def test_build_dict_executable_falls_back_to_sys_executable_dir():
    from ekonlpy.mecab import _userdic

    with mock.patch.object(_userdic.shutil, "which", return_value=None):
        executable = _userdic.MecabDicConfig._build_dict_executable()

    expected_dir = os.path.dirname(sys.executable)
    assert os.path.dirname(executable) == expected_dir
    assert os.path.basename(executable).startswith("fugashi-build-dict")


def test_build_userdic_requires_userdic_path(tmp_path):
    config = MecabDicConfig()

    with pytest.raises(ValueError, match="userdic_path"):
        config.build_userdic(str(tmp_path / "user.dic"))


def test_build_userdic_uses_path_from_constructor(tmp_path):
    csv_path = tmp_path / "user.csv"
    csv_path.write_text(USERDIC_ROW, encoding="utf-8")
    config = MecabDicConfig(userdic_path=str(csv_path))

    with mock.patch("ekonlpy.mecab._userdic.subprocess.run") as run:
        config.build_userdic(str(tmp_path / "user.dic"))

    assert run.call_args[0][0][-1] == str(csv_path)


def test_build_userdic_builds_real_dictionary(tmp_path):
    config = MecabDicConfig()
    config.add_entry_to_userdic("한국은행", pos="NNP")
    csv_path = tmp_path / "user.csv"
    config.save_userdic(str(csv_path))
    built_path = tmp_path / "user.dic"

    config.build_userdic(str(built_path))

    assert built_path.exists()
    with pytest.raises(subprocess.CalledProcessError):
        config.build_userdic(
            str(tmp_path / "out.dic"), userdic_path=str(tmp_path / "missing.csv")
        )
