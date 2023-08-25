def test_sentiment():
    from ekonlpy.sentiment import MPKO

    mpko = MPKO(kind=1)
    text = "금통위는 따라서 물가안정과 병행, 경기상황에 유의하는 금리정책을 펼쳐나가기로 했다고 밝혔다."
    tokens = mpko.tokenize(text)
    score = mpko.get_score(tokens)
    print(tokens)
    print(score)
    # {'Positive': 1, 'Negative': 0, 'Polarity': 0.9999990000010001, 'Subjectivity': 0.9999990000010001}
    assert score["Positive"] == 1 and score["Negative"] == 0

    from ekonlpy.sentiment import MPCK

    mpck = MPCK()
    tokens = mpck.tokenize(text)
    ngrams = mpck.ngramize(tokens)
    score = mpck.classify(tokens + ngrams, intensity_cutoff=1.5)
    print(tokens)
    print(score)
    # {'Polarity': -0.972986080355786, 'Intensity': 73.03049854822524, 'Pos score': 0.013506959822107319, 'Neg score': 0.9864930401778934}
    assert score["Polarity"] < 0


if __name__ == "__main__":
    test_sentiment()
