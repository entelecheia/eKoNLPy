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
        MecabDicConfig._build_dict_path(config.dicdir),
        "-u",
        MecabDicConfig._build_dict_path(str(built_path)),
        MecabDicConfig._build_dict_path(str(csv_path)),
    ]
    assert run.call_args[1].get("check") is True


def test_build_dict_executable_falls_back_to_sys_executable_dir():
    from ekonlpy.mecab import _userdic

    with mock.patch.object(_userdic.shutil, "which", return_value=None):
        executable = _userdic.MecabDicConfig._build_dict_executable()

    expected_dir = os.path.dirname(sys.executable)
    assert os.path.dirname(executable) == expected_dir
    assert os.path.basename(executable).startswith("fugashi-build-dict")


@pytest.mark.skipif(os.name != "nt", reason="Windows-only path normalization")
def test_build_dict_path_uses_forward_slashes_on_windows():
    assert (
        MecabDicConfig._build_dict_path("C:\\Users\\test\\dicdir")
        == "C:/Users/test/dicdir"
    )


@pytest.mark.skipif(os.name == "nt", reason="POSIX paths pass through unchanged")
def test_build_dict_path_passes_posix_through():
    assert MecabDicConfig._build_dict_path("/usr/lib/dicdir") == "/usr/lib/dicdir"


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

    assert run.call_args[0][0][-1] == MecabDicConfig._build_dict_path(str(csv_path))


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


def test_load_userdic_from_csv_file(tmp_path):
    csv_path = tmp_path / "user.csv"
    csv_path.write_text(USERDIC_ROW, encoding="utf-8")
    config = MecabDicConfig(userdic_path=str(csv_path))

    entry = config.userdic["한국은행"]
    assert entry.pos == "NNP"
    assert int(entry.left_id) == 1795
    assert entry.cost == 1000


def test_load_userdic_from_directory(tmp_path):
    (tmp_path / "a.csv").write_text(USERDIC_ROW, encoding="utf-8")
    (tmp_path / "b.csv").write_text(
        "금통위,1795,3558,1000,NNP,*,T,금통위,*,*,*,*\n", encoding="utf-8"
    )
    config = MecabDicConfig(userdic_path=str(tmp_path))

    assert set(config.userdic) == {"한국은행", "금통위"}


def test_add_entry_to_userdic_resolves_context_ids_and_jongseong():
    config = MecabDicConfig()

    config.add_entry_to_userdic("한국은행", pos="NNP")
    config.add_entry_to_userdic("사과", pos="NNG", reading="사과")

    bank = config.userdic["한국은행"]
    assert bank.has_jongseong == "T"
    assert bank.reading == "한국은행"
    assert bank.left_id is not None
    assert bank.right_id is not None
    assert config.userdic["사과"].has_jongseong == "F"


def test_adjust_context_ids_recomputes_ids(tmp_path):
    csv_path = tmp_path / "user.csv"
    csv_path.write_text(USERDIC_ROW, encoding="utf-8")
    config = MecabDicConfig(userdic_path=str(csv_path))

    config.adjust_context_ids()

    entry = config.userdic["한국은행"]
    assert entry.left_id == config.find_left_context_id(entry)
    assert entry.right_id == config.find_right_context_id(entry)


def test_adjust_costs_replaces_all_costs(tmp_path):
    csv_path = tmp_path / "user.csv"
    csv_path.write_text(USERDIC_ROW, encoding="utf-8")
    config = MecabDicConfig(userdic_path=str(csv_path))

    config.adjust_costs(cost=500)

    assert config.userdic["한국은행"].cost == 500


def test_save_userdic_without_entries_logs_warning(tmp_path, caplog):
    config = MecabDicConfig()
    save_path = tmp_path / "empty.csv"

    with caplog.at_level("WARNING"):
        config.save_userdic(str(save_path))

    assert "No user dictionary entries to save." in caplog.text
    assert not save_path.exists()
