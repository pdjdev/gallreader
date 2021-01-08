import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests, lxml, os, time, requests, json
from wordcloud import WordCloud
from base64 import b64encode
from datetime import datetime, timedelta


print('파일 읽는중...')
data = open('list.txt', 'r', encoding='UTF-8').read()

data = data.replace("\n", " ")

rmkeys = ['너무', '진짜', '이거', '근데', '님들', '오늘',
          '솔직히', '존나', '내가', '아니', '애니', '요즘',
          '그냥', '사실', '이제', '뭔가', '본인', 'ㅋㅋ',
          '지금', '이게', '여기', '있음', '있다', '없음',
          '없다', '뭔데', '왤케', '완전', '하는', 'ㄹㅇ',
          '나도', 'vs', '시발', '씨발', '이런', '보고',
          '같음', '갑자기', '다시', '그리고', '그래서',
          '이런', '보면', '내일', '오늘은', '좋음', '있어서',
          '무슨', '누가', '만든', '사람이', '가장', '많이',
          '이름', '이렇게', '어떻게', '같은', '나는', '제일', '좋은',
          '하고', '있는', '아님', '사람', '계속', '하면',
          '정말', '같이', '없는', '빨리', '이건', '있는데',
          '그렇게', '대체', '아니라', '아직도', '아니면']

print('불필요한 키워드 제거중...')
for d in rmkeys:
    data = data.replace(' ' + d + ' ', ' ')

data = data.replace('&gt;', ' ')
data = data.replace('&lt;', ' ')
data = data.replace('https://www.youtube.com/watch?v=', ' ')
data = data.replace('https://youtu.be/', ' ')
data = data.replace('- dc official App',' ')
data = data.replace('- 라하마갤 와주는데스http://gall.dcinside.com/loudhouse',' ')
data = data.replace('https://gall.dcinside.com/mgallery/board/view/?id=',' ')
data = data.replace('https://gall.dcinside.com/board/lists/?id=', ' ')
data = data.replace('https://', ' ')

print('워드클라우드 생성 중...')
wc_title = WordCloud(font_path='font.otf', width=2000, height=1800, background_color='white', collocations=False, max_words=2000).generate(data)

print('이미지 저장 중...')
wc_title.to_file('wordcloud.png')

hk = sorted(wc_title.words_.items(), key=(lambda x: x[1]), reverse = True)
#hotkey = hk[0][0] + ', ' + hk[1][0] + ', ' + hk[2][0] + ', ' + hk[3][0] + ', ' + hk[4][0]
#print('핵심 키워드:', hotkey)
#pkeys = ''
#for s in hk: pkeys += s[0] + '\n'

keys = ''

for k in hk:
    keys += str(k) + '\n'

open('lastkeys.txt', 'w', encoding='utf-8-sig').write(keys)

print('저장 완료')
