from bs4 import BeautifulSoup
import requests, lxml, time, requests, reprlib
from datetime import datetime, timedelta
import csv

re = reprlib.Repr()
re.maxstring = 20    # max characters displayed for strings

def midReturn(val, s, e):
    if s in val:
        val = val[val.find(s)+len(s):]
        if e in val: val = val[:val.find(e)]
    return val

taskdone = False
trial = 0

# 갤러리ID
gid = input('갤러리 ID: ')
filename = input('저장 파일명: ')
start = input('시작 페이지(PC버전기준, 기본값=0): ')

# 탐색 날짜 범위 (ex. days=1 : 1일 이내, 0:측정 시작순간 이후)
# 설정 날짜의 딱 자정으로 설정됩니다 (ex. 8.18 1:45AM -> 8.18 00:00AM)
drange = int(input('탐색 날짜 범위 (ex. 1=1일 이내): '))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}


f = open(filename + '.csv', 'w', encoding='utf-8-sig', newline='')
wr = csv.writer(f)

if (start==''): i=0
else: i=int(start)


# 갤러리 링크
link = 'https://gall.dcinside.com/board/lists/?id=' + gid


ystday = (datetime.now() - timedelta(days=drange)).replace(hour=0, minute=0, second=0, microsecond=0)
print(ystday, '이후의 게시글을 수집합니다.')
        
taskdone = False
trial = 0

postidlist = []

while not taskdone and trial < 10:

    # 마이너, 정식갤러리 판별
    r = requests.get('https://gall.dcinside.com/board/lists/?id=' + gid, headers = headers).text
    print('갤러리 형식:', end=' ')

    # 마이너 갤러리일 경우
    if 'location.replace' in r:
        link = link.replace('board/','mgallery/board/')    
        print('마이너')
    else:
        print('정식')

    # data = 'Post ID\tTitle\tNickname\tIPID\tDate\tViewcount\tUpvoteCount\n'
    # 글 ID, 제목, 닉네임, IPID, 작성일자, 조회수, 추천수, 계정유무
    wr.writerow(['Post ID', 'Title', 'Nickname', 'IPID', 'Date', 'Views', 'Upvotes', 'HasAccount'])
    fin = False
    r = None

    while not fin:
        time.sleep(0.5)
        
        i += 1
        print('===== 페이지 읽는 중... [{}번째...] ====='.format(i))#, end='\r')
        titleok = False

        while not titleok:
            r = requests.get(link + '&page=' + str(i) + '&list_num=100', headers = headers).text
            bs = BeautifulSoup(r, 'lxml')

            posts = bs.find_all('tr', class_='ub-content us-post')

            for p in posts:
                title = p.find('td', class_='gall_tit ub-word')

                # 공지 제외 (볼드태그 찾을때 str 처리 해줘야 찾기가능)
                if not '<b>' in str(title):
                    titleok = True
                    pid = p.find("td", {"class", "gall_num"}).text.strip()
                    title = midReturn(str(title), '</em>', '</a>')
                    IPID = ''
                    hasaccount = '0'

                    # 유동일 경우
                    if p.find('td', class_='gall_writer ub-writer').get('data-uid') == '':
                        IPID = p.find('td', class_='gall_writer ub-writer').get('data-ip')        
                    else: # 고닉일 경우
                        IPID = p.find('td', class_='gall_writer ub-writer').get('data-uid')
                        hasaccount = '1'
                                            
                    nick = p.find('td', class_='gall_writer ub-writer').get('data-nick')
                    date = datetime.strptime(p.find('td', class_='gall_date').get('title'), "%Y-%m-%d %H:%M:%S")
                    view = p.find("td", {"class", "gall_count"}).text.strip()
                    recom = p.find("td", {"class", "gall_recommend"}).text.strip()
                    
                    print(pid + "\t" + str(date) + "\t" + re.repr(nick) + "\t\t" + re.repr(title))

                    # 이미 읽은 글은 읽지 않기
                    if not pid in postidlist:
                        
                        #초 단위까지는 안 가도록 함
                        if date >= ystday:
                            # data += pid + "\t" + title + "\t" + nick + "\t" + IPID + "\t" + str(date) + "\t" + view + "\t" + recom + "\n"
                            wr.writerow([pid, title, nick, IPID, str(date), view, recom, hasaccount])
                        else:
                            ask = input('중지하시겠습니까? [Y/n]: ')
                            if ask == 'y' or ask == 'Y':
                                print('[NO]' + title)
                                print('기간 초과:', date)
                                fin = True
                                date = ystday
                                break
                            else:
                                # data += pid + "\t" + title + "\t" + nick + "\t" + str(date) + "\t" + view + "\t" + recom + "\n"
                                wr.writerow([pid, title, nick, IPID, str(date), view, recom, hasaccount])

                        postidlist.append(pid)
                        
                    else:
                        print(pid + '\t이미 조회된 글입니다 - 무시하고 계속 읽습니다.')
                    
            if not titleok:
                print('게시글 크롤링 실패. 5초 후 다시 시도해 봅니다.')
                #i -= 1
                time.sleep(5)
                     

    print('저장 완료')
    taskdone = True

print("파일 쓰는 중...")
f.close()
print("쓰기 완료.")
