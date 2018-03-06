# eKoNLPy
extended KoNLPy

# Usage

### Part of speech tagging

KoNLPy와 동일하게 Mecab.pos(phrase)를 입력합니다.
먼저 KoNLPy의 Mecab 형태소 분석기로 처리한 후,
템플릿에 등록된 연속된 토큰의 조합이 사용자 사전에 등록되어 있으면
복합명사로 어절을 분리합니다.

    mecab.pos('금통위는 따라서 물가안정과 병행, 경기상황에 유의하는 금리정책을 펼쳐나가기로 했다고 밝혔다.')

    > [('금통위', 'NNG'), ('는', 'JX'), ('따라서', 'MAJ'), ('물가', 'NNG'), ('안정', 'NNG'), ('과', 'JC'), ('병행', 'NNG'), (',', 'SC'), ('경기', 'NNG'), ('상황', 'NNG'), ('에', 'JKB'), ('유의', 'NNG'), ('하', 'XSV'), ('는', 'ETM'), ('금리정책', 'NNG'), ('을', 'JKO'), ('펼쳐', 'VV+EC'), ('나가', 'VX'), ('기', 'ETN'), ('로', 'JKB'), ('했', 'VV+EP'), ('다고', 'EC'), ('밝혔', 'VV+EP'), ('다', 'EF'), ('.', 'SF')]

### Add words to dictioanry

ekonlpy.tag의 Mecab은 add_dictionary를 통하여 str 혹은 list of str 형식의 사용자 사전을 추가할 수 있습니다.

    from ekonlpy.tag import Mecab

    mecab.add_dictionary('금통위', 'NNG')

## Install

    $ git clone https://github.com/entelecheia/eKoNLPy.git

    $ pip install eKoNLPy

## Requires

- KoNLPy >= 0.4.4
