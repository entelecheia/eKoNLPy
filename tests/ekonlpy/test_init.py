from ekonlpy import get_version


def test_get_version() -> None:
    """
    Test the get_version function.

    version format: major.minor.patch[.devN+g<git hash>]
    """
    version = get_version()
    # check version format
    assert version.count(".") in range(2, 5)


def test_init() -> None:
    from ekonlpy import Mecab, MecabDicConfig, TermDictionary, installpath

    assert Mecab
    assert MecabDicConfig
    assert TermDictionary
    assert installpath

    mecab_fugashi = Mecab(use_original_tagger=True)
    print(mecab_fugashi.pos("안녕하세요"))
    assert mecab_fugashi.pos("안녕하세요") == [
        ("안녕", "NNG"),
        ("하", "XSV"),
        ("세요", "EP+EF"),
    ]

    mecab = Mecab(use_original_tagger=False)
    print(mecab.pos("안녕하세요"))
    assert mecab.pos("안녕하세요") == [("안녕", "NNG"), ("하", "XSV"), ("세요", "EP")]

    text = "금통위는 따라서 물가안정과 병행, 경기상황에 유의하는 금리정책을 펼쳐나가기로 했다고 밝혔다."
    mecab_fugashi = Mecab(use_original_tagger=True)
    print(mecab_fugashi.pos(text))
    assert mecab_fugashi.pos(text)[0] == ("금", "MAJ")

    mecab = Mecab(use_original_tagger=False)
    print(mecab.pos(text))
    assert mecab.pos(text)[0] == ("금통위", "NNG")


if __name__ == "__main__":
    test_init()
    test_get_version()
