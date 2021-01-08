import re,requests,sys,time,html,random
from bs4 import BeautifulSoup
from base64 import b64encode
from hashlib import sha256
import csv
                
def get_app_id(): #공앱에서 사용하는 app_id 값 받아오기. 주기적으로 새로 발급해야함
    while True:
        try:
            date = session.post('http://json2.dcinside.com/json0/app_check_A_rina.php').json()[0]['date']
            value_token = sha256(('dcArdchk_%s' % date).encode('ascii')).hexdigest()
            app_id = session.post('https://dcid.dcinside.com/join/mobile_app_key_verification_3rd.php',headers={'User-Agent': "dcinside.app"},
                                  data={"value_token": value_token,"signature":'ReOo4u96nnv8Njd7707KpYiIVYQ3FlcKHDJE046Pg6s=','client_token':'a'*2000}).json()[0]['app_id'].encode('ascii')
            return app_id.decode('utf-8')
        except Exception as e:e = str(e)

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

# 갤러리ID
gall = input('갤러리 ID: ')
filename = input('저장 파일명 (.csv는 자동으로 포함): ')

while True:
    start = int(input('시작 글번호: '))
    end = int(input('끝 글번호: '))
    if (start > end):
        print('시작 값이 끝 값보다 클 수 없습니다')
        continue
    break

print('작업 시작\n')
time.sleep(1)

f = open(filename + '.csv', 'w', encoding='utf-8-sig', newline='')
wr = csv.writer(f)

# wr.writerow(['no', 'time', 'nick', 'title', 'comment', 'count', 'upvote_count', 'upvote_nick_count', 'downvote_count', 'mobile', 'recom', 'postdata'])
wr.writerow(['Post ID', 'Title', 'Nickname', 'IPID', 'Date', 'Views', 'Upvotes', 'GonicUpvotes', 'Downvotes', 'Comments', 'Recommended', 'Mobile', 'HasAccount', 'PostData'])
# 글번호 제목 닉네임 IPID 날짜 조회수 추천수 고닉추 비추수 댓글수 념글여부 모바일여부 고닉여부 글내용

session = requests.Session()
app_id=get_app_id()

readtime = -1
timeout = 30    # 오류 발생 시 대기할 시간

for no in range(start, end+1):

    starttime = time.time()

    url = "http://m.dcinside.com/api/gall_view_new.php?id="+gall+"&no="+str(no)+"&app_id="+app_id

    while True:
        try:
            a = session.get('http://m.dcinside.com/api/redirect.php?hash='+b64encode(url.encode('utf-8')).decode('utf-8'),headers={"User-Agent": "dcinside.app"},timeout=30)
            break
        except:
            for i in range(timeout):
                print('오류 발생... ',(timeout-i),'초 뒤 다시 시도합니다     ', end='\r')
                time.sleep(1)
            print()

    if r'\uae00\uc5c6\uc74c' in a.text:
        #print(no, '삭제/조회할 수 없는 글')
        state = 'PASS'
    else:
        isgonic = False
        intro = a.json(strict=False)[0]['view_info']
        view = a.json(strict=False)[0]['view_main']
        
        if len(intro['ip'])==0:
            isgonic = True
            postIP = intro['user_id']
        else: postIP = intro['ip'] # 작성자 IP

        nick = intro['name'] # 작성자 닉네임
        title = intro['subject'] # 작성글 제목
        mobile = False if intro['write_type']=='W' else True # 모바일 체크
        recom = False if intro['recommend_chk'] == 'N' else True # 개념글 체크
        count = intro['hit'] #조회수
        comment = intro['total_comment']
        date_time = intro['date_time']

        upvote_count = view['recommend']
        upvote_nick_count = view['recommend_member']
        downvote_count = view['nonrecommend']

        postdata = BeautifulSoup(html.unescape(view['memo']), 'lxml').text # 글 내용

        # 번호, 닉네임, 제목, 댓글, 조회수, 추천수, 고닉추, 비추수, 모바일여부, 개념글여부, 글내용
        # 글번호 제목 닉네임 IPID 날짜 조회수 추천수 고닉추 비추수 댓글수 념글여부 모바일여부 고닉여부 글내용
        wr.writerow([no, title, nick, postIP, date_time, count, upvote_count, upvote_nick_count, downvote_count, comment, recom, mobile, isgonic, postdata])
        #print(no, '기록 성공')
        state = 'SAVE'

    time.sleep(0.1)
    readtime = (time.time() - starttime)

    print('['+state+'/'+str(no)+']',
          (no - start) , '/' , (end - start + 1), '('+str(round((no-start)/(end-start+1)*100))+'%)', '\t|\t' ,
          round(1 / readtime, 2) , '글/sec\t|\t',
          timetostring(round(readtime * (end - no))), '남음')

f.close()
