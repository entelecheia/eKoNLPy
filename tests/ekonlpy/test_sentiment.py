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


def test_breakdown_api():
    """Test the new breakdown API for transparency in sentiment analysis."""
    from ekonlpy.sentiment import MPKO

    mpko = MPKO(kind=1)

    # Test with known hawkish n-gram from lexicon
    hawkish_text = "금리 상승이 예상된다"
    tokens = mpko.tokenize(hawkish_text)

    # Test basic breakdown functionality
    score_with_breakdown = mpko.get_score(tokens, return_breakdown=True)
    assert 'breakdown' in score_with_breakdown
    assert len(score_with_breakdown['breakdown']) == len(tokens)

    # Verify breakdown structure
    for item in score_with_breakdown['breakdown']:
        assert 'term' in item
        assert 'score' in item
        assert 'polarity' in item
        assert 'sentiment' in item
        assert item['sentiment'] in ['positive', 'negative', 'neutral']

    # Test phrase breakdown functionality
    phrase_breakdown = mpko.get_phrase_breakdown(tokens, mpko._tokenizer)
    assert len(phrase_breakdown) == len(tokens)

    # Verify phrase breakdown structure
    for item in phrase_breakdown:
        assert 'term' in item
        assert 'phrase' in item
        assert 'score' in item
        assert 'polarity' in item
        assert 'sentiment' in item

    # Test with known dovish n-gram
    dovish_text = "금리 인하가 필요하다"
    dovish_tokens = mpko.tokenize(dovish_text)
    dovish_score = mpko.get_score(dovish_tokens, return_breakdown=True)

    # Should have negative sentiment
    negative_terms = [item for item in dovish_score['breakdown'] if item['sentiment'] == 'negative']
    assert len(negative_terms) > 0, "Should detect dovish sentiment in '금리 인하가 필요하다'"

    print("Breakdown API test passed!")
    print(f"Hawkish text tokens: {tokens}")
    print(f"Hawkish breakdown: {score_with_breakdown['breakdown']}")
    print(f"Dovish text tokens: {dovish_tokens}")
    print(f"Dovish breakdown: {dovish_score['breakdown']}")


def test_phrase_recovery():
    """Test phrase recovery functionality with MPTokenizer."""
    from ekonlpy.sentiment import MPKO

    mpko = MPKO(kind=1)

    # Test text with known n-grams from lexicon
    test_text = "금리 상승 압력이 높다"
    tokens = mpko.tokenize(test_text)

    # Get phrase breakdown
    phrase_breakdown = mpko.get_phrase_breakdown(tokens, mpko._tokenizer)

    # Verify that phrases are human-readable
    for item in phrase_breakdown:
        assert isinstance(item['phrase'], str)
        assert len(item['phrase']) > 0
        # Phrase should not contain POS tags
        assert '/' not in item['phrase'] or ';' not in item['phrase']

    print("Phrase recovery test passed!")
    print(f"Original tokens: {tokens}")
    print(f"Recovered phrases: {[item['phrase'] for item in phrase_breakdown]}")


def test_lexicon_sensitivity():
    """Test sensitivity to subtle changes in policy statements."""
    from ekonlpy.sentiment import MPKO

    mpko = MPKO(kind=1)

    # Test hawkish statement
    hawkish_text = "금리 상승이 필요하다"
    hawkish_tokens = mpko.tokenize(hawkish_text)
    hawkish_score = mpko.get_score(hawkish_tokens, return_breakdown=True)

    # Test dovish statement (removing hawkish phrase)
    dovish_text = "금리 정책을 검토한다"
    dovish_tokens = mpko.tokenize(dovish_text)
    dovish_score = mpko.get_score(dovish_tokens, return_breakdown=True)

    # The breakdown should show different sentiment patterns
    hawkish_positive = sum(1 for item in hawkish_score['breakdown'] if item['sentiment'] == 'positive')
    dovish_positive = sum(1 for item in dovish_score['breakdown'] if item['sentiment'] == 'positive')

    # Hawkish text should have more positive sentiment terms
    assert hawkish_positive >= dovish_positive, "Hawkish text should show more positive sentiment"

    print("Lexicon sensitivity test passed!")
    print(f"Hawkish breakdown: {hawkish_score['breakdown']}")
    print(f"Dovish breakdown: {dovish_score['breakdown']}")


def test_known_ngram_polarity():
    """Test that known n-grams from lexicon are correctly identified."""
    from ekonlpy.sentiment import MPKO

    mpko = MPKO(kind=1)

    # Test with known hawkish n-gram from lexicon: "금리/NNG;상승/NNG"
    known_hawkish_ngram = "금리/NNG;상승/NNG"
    if known_hawkish_ngram in mpko._poldict:
        score = mpko._get_score(known_hawkish_ngram, by_count=False)
        polarity = mpko._poldict[known_hawkish_ngram]

        # Should be positive (hawkish)
        assert score > 0, f"Known hawkish n-gram {known_hawkish_ngram} should have positive score"
        assert polarity > 0, f"Known hawkish n-gram {known_hawkish_ngram} should have positive polarity"

        print(f"Known hawkish n-gram test passed: {known_hawkish_ngram} -> score: {score}, polarity: {polarity}")

    # Test with known dovish n-gram: "인하/NNG"
    known_dovish_ngram = "인하/NNG"
    if known_dovish_ngram in mpko._poldict:
        score = mpko._get_score(known_dovish_ngram, by_count=False)
        polarity = mpko._poldict[known_dovish_ngram]

        # Should be negative (dovish)
        assert score < 0, f"Known dovish n-gram {known_dovish_ngram} should have negative score"
        assert polarity < 0, f"Known dovish n-gram {known_dovish_ngram} should have negative polarity"

        print(f"Known dovish n-gram test passed: {known_dovish_ngram} -> score: {score}, polarity: {polarity}")


if __name__ == "__main__":
    test_sentiment()
    test_breakdown_api()
    test_phrase_recovery()
    test_lexicon_sensitivity()
    test_known_ngram_polarity()
