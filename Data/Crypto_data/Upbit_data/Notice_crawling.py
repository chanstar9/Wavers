import re
import requests
import pandas as pd
from datetime import datetime


def find_ICO():
    # 공지사항 1페이지 제목들만 불러옴
    url = 'https://api-manager.upbit.com/api/v1/notices?page=1&per_page=20&thread_name=general'
    resp = requests.get(url).json()
    # 연결실패시 Exit
    if not resp['success']:
        print('Crawling has failed.')
        return 0

    titles = [(data['title'], data['created_at'][:10]) for data in resp['data']['list']]
    df = pd.DataFrame(titles, columns=['titles', 'date'])

    # [거래] 표시되어 있는 놈들로 필터1 그중에 첫번째 가장 최신
    df = df[df['titles'].str.startswith('[거래]')].reset_index(drop=True)

    # 오늘 날짜 공시자료 여부
    today = datetime.now().date()
    strtime = lambda x: datetime.strptime(x['date'], '%Y-%m-%d').date()
    df['date'] = df.apply(strtime, axis=1)
    update = df[df['date'] == today]
    if update.empty:
        print('There Is No Update Until Now.')
        return 0
    else:
        print('Find Update For Today')

    recent_title = update['titles'].values[0]  # ICO 추정 제목
    words = recent_title.split(' ')
    if '자산' in words and '추가' in words:  # ICO인지 다시 체크
        print('ICO happens')

        # 코인 이름 추출 전처리
        korean = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')
        letters = "\(.*\)|\s-\s.*"
        non_korean = re.sub(korean, '', recent_title)  # 한국어 제거
        first = re.sub('[()]', '', non_korean)
        second = re.sub('[[]]', '', first).strip()
        third = re.sub('[KRW BTC]', '', second).split(',')
        coin_names = ' '.join(third).split()
    else:
        print('No ICO')
        return 0

    return coin_names
