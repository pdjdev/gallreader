# gallreader - 댓글 수집 스크립트
# 글 ID가 줄바꿈으로 구분되어 나열된 텍스트 파일이 필요합니다
# (tip. 페이지별 글 수집을 통해 빠르게 글 목록을 수집한 뒤 csv 파일을 스프레드시트 에디터로 열어 Post ID 행을 복사하여 txt 파일을 생성하면 됩니다)

listfilename = input('글 리스트 텍스트 파일?(.txt):')
content = open(listfilename + '.txt', 'r').read()

c = content.split('\n')
postlist = []

for i in c:
    try:
        postlist.append(int(i))
    except:
        print('not right type:', i)

postlist.sort()

import requests, time, re, lxml, sys, csv
from bs4 import BeautifulSoup

def timetostring(t):
    if (t <= 0): return '1초 미만'    
    s = ''; hour = 0; mini = 0    
    while(t >= 3600): t -= 3600; hour += 1
    while(t >= 60): t -= 60; mini += 1
    sec = t
    if hour > 0: s += ' ' + str(hour) + '시간'
    if mini > 0: s += ' ' + str(mini) + '분'
    if sec > 0: s += ' ' + str(sec) + '초'
    return s[1:]

# 오류시 대기시간 (초)
timeout = 30

# 갤러리ID
gallid = input('갤러리 ID: ')
filename = input('저장 파일명 (.csv는 자동으로 포함): ')

f = open(filename + '.csv', 'w', encoding='utf-8-sig', newline='')


wr = csv.writer(f)
wr.writerow(['Post ID', 'Cmt ID', 'Nickname', 'IPID', 'Date', 'HasAccount', 'IsReply', 'RefCID', 'IsDccon', 'PostData'])

print('작업 시작\n')
time.sleep(1)

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.104 Mobile Safari/537.36'
}

for postid in postlist:

    starttime = time.time()

    # print(postid, '번 글 조회...')
    cpage = 1

    while True:    
        # print(cpage, '번째 페이지 조회...')
        time.sleep(0.2)

        data = {
        'id': gallid,
        'no': postid,
        'cpage': cpage,
        }

        while True:
            try:
                r = requests.post('https://m.dcinside.com/ajax/response-comment', headers=headers, data=data).text
                break
            except:
                for i in range(timeout):
                    print('접속 오류 발생... ',(timeout-i),'초 뒤 다시 시도합니다     ')
                    sys.stdout.flush()
                    time.sleep(1)
                print()

        bs = BeautifulSoup(r, 'lxml')

        comments = bs.find_all("li", {"class" : re.compile('comment.*')})

        isreply = False
        corgcid = -1

        for c in comments:

            # 삭제된 댓글 표시는 넘어가기
            if not c.has_attr('no'): continue

            cid = c['no']
            cnick = c.a.text
            ctext = c.p.text
            cgonic = not 'ip' in c.span['class']

            # 고닉일시
            if cgonic:
                cipid = c.a['href'][c.a['href'].rfind('/')+1:]
            else:
            # 유동일시
                cipid = cnick[cnick.rfind('(')+1:cnick.rfind(')')]
                cnick = cnick[:cnick.rfind('(')]
                pass

            # 답글여부
            isreply = ('comment-add' in c['class'])

            if not isreply:
                corgcid = c['no']

            # 디시콘여부
            isdccon = (not c.img == None)
            if isdccon:
                ctext = c.img['data-original']

            cdate_time = c.find('span', class_='date').text

            # 데이터(csv)쓰기
            if isreply:
                wr.writerow([postid, cid, cnick, cipid, cdate_time, cgonic, isreply, corgcid, isdccon, ctext])
            else:
                wr.writerow([postid, cid, cnick, cipid, cdate_time, cgonic, isreply, '', isdccon, ctext])

        cpg = bs.find('span', {'class' : 'pgnum'})

        if (not cpg == None):
            if (cpage >= int(cpg.text.split('/')[1])):
                break
            else:
                cpage += 1
        else:
            break

    readtime = (time.time() - starttime)

    print('['+str(postid)+']',
            (postid - postlist[0] + 1) , '/' , (postlist[-1] - postlist[0] + 1), '('+str(round((postid-postlist[0])/(postlist[-1]-postlist[0]+1)*100))+'%)', '\t|\t' ,
            round(1 / readtime, 2) , '글/sec\t|\t',
            timetostring(round(readtime * (postlist[-1] - postid))), '남음')

f.close()
