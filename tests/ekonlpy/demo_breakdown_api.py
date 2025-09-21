#!/usr/bin/env python3
"""
Demonstration of the new breakdown API for hawkish/dovish tone classification.

This script demonstrates the robustness of the sentiment analysis components,
particularly their sensitivity to subtle changes in policy statements.
"""

from ekonlpy.sentiment import MPKO


def demonstrate_breakdown_api():
    """Demonstrate the new breakdown API functionality."""
    print("=" * 80)
    print("HAWKISH/DOVISH TONE CLASSIFICATION - BREAKDOWN API DEMONSTRATION")
    print("=" * 80)

    mpko = MPKO(kind=1)

    # Test cases demonstrating sensitivity to subtle changes
    test_cases = [
        {
            "text": "금리 상승이 필요하다",
            "description": "Hawkish statement - advocating for rate increases"
        },
        {
            "text": "금리 인하가 필요하다",
            "description": "Dovish statement - advocating for rate decreases"
        },
        {
            "text": "금리 정책을 검토한다",
            "description": "Neutral statement - no clear directional bias"
        },
        {
            "text": "물가 상승 압력이 높다",
            "description": "Hawkish statement - inflation pressure concerns"
        },
        {
            "text": "경기 둔화 우려가 있다",
            "description": "Dovish statement - economic slowdown concerns"
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   Text: '{case['text']}'")
        print("-" * 60)

        # Tokenize the text
        tokens = mpko.tokenize(case['text'])
        print(f"   Tokens: {tokens}")

        # Get standard score
        score = mpko.get_score(tokens)
        print(f"   Aggregate Score: {score}")

        # Get detailed breakdown
        breakdown = mpko.get_score(tokens, return_breakdown=True)
        print(f"   Detailed Breakdown:")
        for item in breakdown['breakdown']:
            print(f"     - Term: {item['term']}")
            print(f"       Score: {item['score']}, Polarity: {item['polarity']}, Sentiment: {item['sentiment']}")

        # Get phrase breakdown
        phrase_breakdown = mpko.get_phrase_breakdown(tokens, mpko._tokenizer)
        print(f"   Human-readable Phrases:")
        for item in phrase_breakdown:
            print(f"     - '{item['phrase']}' -> {item['sentiment']} (polarity: {item['polarity']})")


def demonstrate_lexicon_sensitivity():
    """Demonstrate sensitivity to known n-grams from the lexicon."""
    print("\n" + "=" * 80)
    print("LEXICON SENSITIVITY DEMONSTRATION")
    print("=" * 80)

    mpko = MPKO(kind=1)

    # Known n-grams from the lexicon
    known_ngrams = [
        ("금리/NNG;상승/NNG", "Known hawkish n-gram"),
        ("인하/NNG", "Known dovish n-gram"),
        ("완화/NNG", "Known dovish n-gram"),
        ("긴축/NNG", "Known hawkish n-gram")
    ]

    for ngram, description in known_ngrams:
        if ngram in mpko._poldict:
            score = mpko._get_score(ngram, by_count=False)
            polarity = mpko._poldict[ngram]
            sentiment = "hawkish" if score > 0 else "dovish" if score < 0 else "neutral"

            print(f"\n{description}:")
            print(f"  N-gram: {ngram}")
            print(f"  Score: {score}")
            print(f"  Polarity: {polarity}")
            print(f"  Classification: {sentiment}")


def demonstrate_phrase_recovery():
    """Demonstrate phrase recovery functionality."""
    print("\n" + "=" * 80)
    print("PHRASE RECOVERY DEMONSTRATION")
    print("=" * 80)

    mpko = MPKO(kind=1)

    test_text = "금리 상승 압력이 높아지고 있다"
    tokens = mpko.tokenize(test_text)

    print(f"Original text: '{test_text}'")
    print(f"Tokenized n-grams: {tokens}")

    phrase_breakdown = mpko.get_phrase_breakdown(tokens, mpko._tokenizer)

    print("\nRecovered phrases with sentiment analysis:")
    for item in phrase_breakdown:
        print(f"  '{item['phrase']}' -> {item['sentiment']} (polarity: {item['polarity']})")


if __name__ == "__main__":
    demonstrate_breakdown_api()
    demonstrate_lexicon_sensitivity()
    demonstrate_phrase_recovery()

    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nThe new breakdown API provides transparency in sentiment analysis by:")
    print("1. Showing individual token/ngram polarities and scores")
    print("2. Enabling phrase recovery for human-readable interpretation")
    print("3. Demonstrating sensitivity to subtle changes in policy language")
    print("4. Providing detailed breakdowns for transparency and review")
