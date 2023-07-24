def test_tagger():
    from ekonlpy.mecab import Mecab

    mecab = Mecab()
    text = "금통위는 따라서 물가안정과 병행, 경기상황에 유의하는 금리정책을 펼쳐나가기로 했다고 밝혔다."
    tokens = mecab.pos(text)
    print(tokens)
    ans = [
        ("금", "MAJ"),
        ("통", "MAG"),
        ("위", "NNG"),
        ("는", "JX"),
        ("따라서", "MAJ"),
        ("물가", "NNG"),
        ("안정", "NNG"),
        ("과", "JC"),
        ("병행", "NNG"),
        (",", "SC"),
        ("경기", "NNG"),
        ("상황", "NNG"),
        ("에", "JKB"),
        ("유의", "NNG"),
        ("하", "XSV"),
        ("는", "ETM"),
        ("금리", "NNG"),
        ("정책", "NNG"),
        ("을", "JKO"),
        ("펼쳐", "VV+EC"),
        ("나가", "VX"),
        ("기", "ETN"),
        ("로", "JKB"),
        ("했", "VV+EP"),
        ("다고", "EC"),
        ("밝혔", "VV+EP"),
        ("다", "EF"),
        (".", "SF"),
    ]
    assert tokens == ans


if __name__ == "__main__":
    test_tagger()
