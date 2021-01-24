import re,requests,sys,time,html,random
from bs4 import BeautifulSoup
from base64 import b64encode
from hashlib import sha256
import csv

embedmode = '-embed' in sys.argv


def arrange(filename, savename):
    print('글 정렬 작업 준비중...')
    sys.stdout.flush()
    from pandas import DataFrame, read_csv, concat

    if not ('.csv' in filename): filename += '.csv'


    # 통피 리스트
    SKTip = ['203.226', '211.234', '223.32', '223.33', '223.34', '223.35', '223.36', '223.37', '223.38', '223.39', '223.40','223.41', '223.42', '223.43', '223.44', '223.45', '223.46', '223.47', '223.48', '223.49', '223.50', '223.51', '223.52', '223.53', '223.54', '223.55', '223.56', '223.57', '223.58', '223.59', '223.60', '223.61', '223.62', '223.63']
    KTip = ['39.7', '110.70', '175.223', '175.252', '211.246', '118.235']
    LGTip = ['61.43', '211.234', '117.111', '211.36', '106.102']

    # 기존 CSV 불러옴
    data = read_csv(filename, dtype={'IPID':str})

    if len(sys.argv) > 4 and (sys.argv[1] == "-a" or sys.argv[1] == "--a"):
        print('2개 이상의 데이터가 발견되었습니다')
        sys.stdout.flush()

        savename = sys.argv[len(sys.argv) - 1]

        for i in range(3, len(sys.argv) - 1):
            print(i-1, '번째 파일 병합중...')
            sys.stdout.flush()

            fname = sys.argv[i]
            if not ('.csv' in fname): fname += '.csv'
            newd = read_csv(fname, dtype={'IPID':str})
            data = concat([data, newd])
            
    
    if not ('.csv' in savename): savename += '.csv'

    gonic = data[data['HasAccount']==1] # 고닉과
    udong = data[data['HasAccount']==0] # 유동글

    # 새로운 데이터 생성
    res = DataFrame(columns=['Nick', 'IPID', 'Posts', 'Upvotes', 'Downvotes', 'Comments', 'Views', 'HasAccount'])

    idList = gonic.IPID.unique().tolist() # ID 값 모으기 (고닉)
    ipList = udong.IPID.unique().tolist() # IP 값 모으기 (유동)
    unickList = udong.Nickname.unique().tolist() # 유동닉 값 모으기 (유동)

    # 고닉 다중이 목록 불러오기
    dup_list_id = []
    try:
        tmp = open('dup_list_id.txt', 'r', encoding='utf-8')
        dup_list_id = tmp.read().split('\n')
        tmp.close()
    except:
        print('dup_list_id.txt 불러오기 실패')      

    # 유동 다중ip 목록 불러오기
    dup_list_ip = []
    try:
        tmp = open('dup_list_ip.txt', 'r', encoding='utf-8')
        dup_list_ip = tmp.read().split('\n')
        tmp.close()
    except:
        print('dup_list_ip.txt 불러오기 실패')        

    # 유동 다중닉 목록 불러오기
    dup_list_nick = []
    try:
        tmp = open('dup_list_nick.txt', 'r', encoding='utf-8')
        dup_list_nick = tmp.read().split('\n')
        tmp.close()
    except:
        print('dup_list_nick.txt 불러오기 실패')


    # 고닉 다중이 id목록에서 이미 있던놈은 미리 지우기
    for ml in dup_list_id:
        if not ml == '': # 첫 문자가 #면 주석처리, 아무것도 없을시 무시
            if not ml[0] == '#':
                # 맨 처음 값은 무시
                rmlist = ml[ml.find('\t')+1:]
                idList = [e for e in idList if e not in rmlist.split('\t')]
                idList.append(rmlist)

    # 유동 다중ip 목록에서 이미 있던놈은 미리 지우기
    for ml in dup_list_ip:
        if not ml == '': # 첫 문자가 #면 주석처리, 아무것도 없을시 무시
            if not ml[0] == '#':
                # 맨 처음 값은 무시
                rmlist = ml[ml.find('\t')+1:]
                ipList = [e for e in ipList if e not in rmlist.split('\t')]
                ipList.append(rmlist)

    # 유동 다중닉 목록에서 이미 있던놈은 미리 지우기
    for ml in dup_list_nick:
        if not ml == '': # 첫 문자가 #면 주석처리, 아무것도 없을시 무시
            if not ml[0] == '#':
                # 맨 처음 값은 무시
                rmlist = ml[ml.find('\t')+1:]
                unickList = [e for e in unickList if e not in rmlist.split('\t')]
                unickList.append(rmlist)


    print('고닉 글 집계중...')
    sys.stdout.flush()

    ################### 고닉 글 집계 ###################
            
    for ids in idList:    
        col = gonic[gonic['IPID'].isin(ids.split('\t'))]
        col2 = udong[udong['IPID'].isin(ids.split('\t'))] # 유동 아이피도 넣기
        col = concat([col, col2])

        nicks = ' '.join(col.Nickname.unique().tolist())
        ids2 = ' '.join(col.IPID.unique().tolist())
        
        counts = col.shape[0] # 글 수
        upvotes = col.Upvotes.sum() # 추천수
        
        if 'Downvotes' in data.columns:
            downvotes = col.Downvotes.sum() # 비추수
        else:
            downvotes = None
        
        if 'Comments' in data.columns:
            comments = col.Comments.sum() # 받은댓글수
        else:
            comments = None

        if 'Views' in data.columns: 
            views = col.Views.sum() # 조회수
        else:
            views = None

            
        nd = {'Nick' : nicks, 'IPID' : ids2, 'Posts' : counts, 'Upvotes' : upvotes, 'Downvotes' : downvotes, 'Comments' : comments, 'Views' : views, 'HasAccount' : 1}
        res = res.append(nd, ignore_index=True)


    print('유동 글 집계중...')
    sys.stdout.flush()

    ################### 유동 글 집계 ###################
        
    # 닉네임이 ㅇㅇ이고 통피인놈들을 일단 묶어서 통계내기
    for ips in [SKTip, KTip, LGTip]:   
        col = udong[(udong['IPID'].isin(ips)) & (udong['Nickname']=='ㅇㅇ')]
        if col.shape[0] > 0:
            nicks = 'ㅇㅇ(통피)'
            ids2 = ' '.join(col.IPID.unique().tolist())
            counts = col.shape[0] # 글 수
            upvotes = col.Upvotes.sum() # 추천수

            if 'Downvotes' in data.columns:
                downvotes = col.Downvotes.sum() # 비추수
            else:
                downvotes = None
            
            if 'Comments' in data.columns:
                comments = col.Comments.sum() # 받은댓글수
            else:
                comments = None

            if 'Views' in data.columns: 
                views = col.Views.sum() # 조회수
            else:
                views = None
                
            nd = {'Nick' : nicks, 'IPID' : ids2, 'Posts' : counts, 'Upvotes' : upvotes, 'Downvotes' : downvotes, 'Comments' : comments, 'Views' : views, 'HasAccount' : 0}
            res = res.append(nd, ignore_index=True) 
            udong = udong.drop(col.index) # 조건에 맞게 쓴 글들은 없애기 -> 또 세지 않도록

    # ㅇㅇ(123.45), ㅇㅇ(56.789) -> 다른 놈으로 취급 (단, ip가 리스트에 있으면 같은놈)
    # 파이썬(123.45), 루비(123.45) -> 다른 놈으로 취급 (단, 닉네임이 리스트에 있으면 같은놈)

    # ip가 다른 ㅇㅇ닉글들 수집
    for ips in ipList:
        col = udong[(udong['IPID'].isin(ips.split('\t'))) & (udong['Nickname']=='ㅇㅇ')]
        if col.shape[0] > 0:
            nicks = 'ㅇㅇ'
            ids2 = ' '.join(col.IPID.unique().tolist())
            counts = col.shape[0] # 글 수
            upvotes = col.Upvotes.sum() # 추천수
            
            if 'Downvotes' in data.columns:
                downvotes = col.Downvotes.sum() # 비추수
            else:
                downvotes = None
            
            if 'Comments' in data.columns:
                comments = col.Comments.sum() # 받은댓글수
            else:
                comments = None

            if 'Views' in data.columns: 
                views = col.Views.sum() # 조회수
            else:
                views = None
                
            nd = {'Nick' : nicks, 'IPID' : ids2, 'Posts' : counts, 'Upvotes' : upvotes, 'Downvotes' : downvotes, 'Comments' : comments, 'Views' : views, 'HasAccount' : 0}
            res = res.append(nd, ignore_index=True)
            udong = udong.drop(col.index)
            
 
    print('닉유동 글 집계중...')
    sys.stdout.flush()

    # 닉네임이 ㅇㅇ가 아닌 유동닉글들 수집
    for nicks in unickList:
        col = udong[udong['Nickname'].isin(nicks.split('\t'))]
        if col.shape[0] > 0:
            nicks = ' '.join(col.Nickname.unique().tolist())
            ids2 = ' '.join(col.IPID.unique().tolist())
            counts = col.shape[0] # 글 수
            upvotes = col.Upvotes.sum() # 추천수
            
            if 'Downvotes' in data.columns:
                downvotes = col.Downvotes.sum() # 비추수
            else:
                downvotes = None
            
            if 'Comments' in data.columns:
                comments = col.Comments.sum() # 받은댓글수
            else:
                comments = None

            if 'Views' in data.columns: 
                views = col.Views.sum() # 조회수
            else:
                views = None
                
            nd = {'Nick' : nicks, 'IPID' : ids2, 'Posts' : counts, 'Upvotes' : upvotes, 'Downvotes' : downvotes, 'Comments' : comments, 'Views' : views, 'HasAccount' : 0}
            res = res.append(nd, ignore_index=True)

    print('작업 마무리중...')
    sys.stdout.flush()

    # 결측치 제거
    res = res.dropna(axis=1)
    res = res[res['Posts']!=0]

    # 정렬
    res = res.sort_values(by='Posts', ascending=False)

    # 저장
    res.to_csv(savename, encoding='utf-8-sig', index=False)
    print(savename, '로 저장되었습니다.')
    sys.stdout.flush()


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

def midReturn(val, s, e):
    if s in val:
        val = val[val.find(s)+len(s):]
        if e in val: val = val[:val.find(e)]
    return val

def gallreader(filename, gall, start, end):
    print('글 조회 작업 준비중...')
    sys.stdout.flush()
    
    # 시작이 끝보다 크면 바꿔치기
    if (start > end):
        temp = start
        start = end
        end = temp
  
    time.sleep(1)
    f = open(filename, 'w', encoding='utf-8-sig', newline='')
    wr = csv.writer(f)

    wr.writerow(['Post ID', 'Title', 'Nickname', 'IPID', 'Date', 'Views', 'Upvotes', 'GonicUpvotes', 'Downvotes', 'Comments', 'Recommended', 'Mobile', 'HasAccount', 'PostData'])
    # 글번호 제목 닉네임 IPID 날짜 조회수 추천수 고닉추 비추수 댓글수 념글여부 모바일여부 고닉여부 글내용

    session = requests.Session()
    while True:
        try:
            date = session.post('http://json2.dcinside.com/json0/app_check_A_rina.php').json()[0]['date']
            value_token = sha256(('dcArdchk_%s' % date).encode('ascii')).hexdigest()
            app_id = session.post('https://dcid.dcinside.com/join/mobile_app_key_verification_3rd.php',headers={'User-Agent': "dcinside.app"},
                                  data={"value_token": value_token,"signature":'ReOo4u96nnv8Njd7707KpYiIVYQ3FlcKHDJE046Pg6s=','client_token':'a'*2000}).json()[0]['app_id'].encode('ascii')
            app_id = app_id.decode('utf-8')
            break
        except:
            for i in range(10):
                print('오류 발생... ',(10-i),'초 뒤 다시 시도합니다     ')
                sys.stdout.flush()
                time.sleep(1)
            print()

    readtime = -1
    timeout = 30    # 오류 발생 시 대기할 시간

    print('글 조회 시작')
    sys.stdout.flush()

    for no in range(start, end+1):

        starttime = time.time()

        url = "http://m.dcinside.com/api/gall_view_new.php?id="+gall+"&no="+str(no)+"&app_id="+app_id

        while True:
            try:
                a = session.get('http://m.dcinside.com/api/redirect.php?hash='+b64encode(url.encode('utf-8')).decode('utf-8'),headers={"User-Agent": "dcinside.app"},timeout=30)
                break
            except:
                for i in range(timeout):
                    print('오류 발생... ',(timeout-i),'초 뒤 다시 시도합니다     ')
                    sys.stdout.flush()
                    time.sleep(1)
                print()

        try:
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

            if embedmode:
                smsg = '<smsg><state>' + state + '</state>'
                smsg += '<no>' + str(no) + '</no>'
                # smsg += '<total>' + (end - start + 1) + '</total>'
                smsg += '<title>' + title + '</title>'
                smsg += '<readtime>' + str(round(1 / readtime, 2)) + '</readtime>'
                smsg += '<lefttime>' + timetostring(round(readtime * (end - no))) + '</lefttime></smsg>'     
                print(smsg)
                sys.stdout.flush()

            print('['+state+'/'+str(no)+']',
                    (no - start + 1) , '/' , (end - start + 1), '('+str(round((no-start)/(end-start+1)*100))+'%)', '\t' ,
                    round(1 / readtime, 2) , '글/sec\t',
                    timetostring(round(readtime * (end - no))), '남음')
            sys.stdout.flush()   

        except:
            print('구문 분석/저장 오류')
            sys.stdout.flush()

    f.close()
    print(filename + '.csv 로 저장되었습니다.')
    sys.stdout.flush()


def gallreader_page(filename, gall, startpage, endpage, startdate=-1, enddate=-1, autostop=True):
    print('페이지 조회 작업 준비중...')
    sys.stdout.flush()

    from datetime import datetime, timedelta

    prevcount = 0
    readtime = -1
    tasktime = 0

    validdate = False

    if startdate > 0 and enddate > 0:
        startdate = datetime.fromtimestamp(startdate)
        enddate = datetime.fromtimestamp(enddate)
        # 끝 날짜가 나중일때 (입력범위가 반대일때)
        if startdate < enddate:
            tmp = startdate
            startdate = enddate
            enddate = startdate
    
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36' }

    drange = 0
    f = open(filename + '.csv', 'w', encoding='utf-8-sig', newline='')
    wr = csv.writer(f)

    if startpage == 0: startpage = 1 # 0일경우 자동으로 1로 고쳐주기
    i = startpage - 1
    link = 'https://gall.dcinside.com/board/lists/?id=' + gall

    if (startdate != -1 and enddate != -1):
        print(startdate, enddate, '사이의 글을 수집합니다.')
    else:
        print(startpage, '부터', endpage, '까지 페이지의 글을 수집합니다.')
    sys.stdout.flush()
            
    taskdone = False
    trial = 0

    postidlist = []

    while not taskdone and trial < 10:

        # 마이너, 정식갤러리 판별
        r = requests.get('https://gall.dcinside.com/board/lists/?id=' + gall, headers = headers).text
        print('갤러리 형식:', end=' ')

        # 마이너 갤러리일 경우
        if 'location.replace' in r:
            link = link.replace('board/','mgallery/board/')    
            print('마이너')
        else:
            print('정식')
        sys.stdout.flush()

        # data = 'Post ID\tTitle\tNickname\tIPID\tDate\tViewcount\tUpvoteCount\n'
        # 글 ID, 제목, 닉네임, IPID, 작성일자, 조회수, 추천수, 계정유무
        wr.writerow(['Post ID', 'Title', 'Nickname', 'IPID', 'Date', 'Views', 'Upvotes', 'HasAccount'])
        fin = False
        r = None

        while not fin:
            readstarttime = time.time()
            time.sleep(0.5)
            
            i += 1
            # print('===== 페이지 읽는 중... [{}번째...] ====='.format(i))#, end='\r')
            titleok = False

            while not titleok:
                r = requests.get(link + '&page=' + str(i) + '&list_num=100', headers = headers).text
                bs = BeautifulSoup(r, 'lxml')

                posts = bs.find_all('tr', class_='ub-content us-post')
                wroteonce = False

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
                        
                        # 이미 읽은 글은 읽지 않기
                        if not pid in postidlist:
                            
                            # 초 단위까지는 안 가도록 함
                            if i >= startpage and (i <= endpage or endpage == 0):
                                if (startdate == -1 and enddate == -1) or date >= enddate and date <= startdate:
                                    wroteonce = True
                                    wr.writerow([pid, title, nick, IPID, str(date), view, recom, hasaccount])
                                    postidlist.append(pid)
                                    # print(pid + "\t" + str(date) + "\t" + nick + "\t\t" + title)
                            
                        else:
                            print(pid + '\t이미 조회된 글입니다 - 무시하고 계속 읽습니다.')
                            sys.stdout.flush()
                        
                if not titleok:
                    print('게시글 크롤링 실패. 10초 후 다시 시도해 봅니다.')
                    sys.stdout.flush()
                    #i -= 1
                    time.sleep(10)

            if not wroteonce:       # 페이지에 읽을 수 있는 글이 단 하나도 없을시에
                if i> endpage:      # 끝 페이지를 넘겼을 경우
                    fin = True
                else:
                    if autostop:        # 자동 멈춤일 경우
                        # 날짜가 지정되어 있으며 아직 그 날짜에 다다르지 못하여서 글을 못 읽는거라면
                        if startdate != -1 and date > startdate:
                            # 암것도 안하기
                            print('시작 날짜로 페이지를 이동하는 중... (현재', i, '페이지)')
                        else:
                            fin = True
                            print('날짜 범위를 벗어나여 자동으로 중단합니다.')
                        sys.stdout.flush()
            else:

                # 여기서부터는 읽기속도/예상소요시간 계산

                c = len(postidlist) - prevcount
                if c > 0:
                    readtime = c / (time.time() - readstarttime)
                    prevcount = len(postidlist)

                    percent = 0

                    if (startdate != -1 and enddate != -1): # 날짜범위가 지정되어 있는 경우
                        current = startdate - date # 현재 읽고 있는 시간량
                        whole = startdate - enddate # 전체 시간량
                        percent = current / whole
                    else: # 아닌 경우
                        percent = (i - startpage) / (endpage - startpage)
                        
                    if percent > 1: percent = 1
                    
                    if percent > 0:
                        est_totalpost = round(len(postidlist)*(1/percent))
                        est_time = timetostring(round((len(postidlist)*(1/percent)-len(postidlist))/readtime))
                    else:
                        est_totalpost = '???'
                        est_time = '???'

                    if embedmode:
                        smsg = '<smsg><state>READ</state>'
                        smsg += '<page>' + str(i) + '</page>'
                        smsg += '<no>' + str(len(postidlist)) + '</no>'
                        smsg += '<total>' + str(est_totalpost) + '</total>'
                        smsg += '<title>' + title + '</title>'
                        smsg += '<readtime>' + str(round(readtime, 2)) + '</readtime>'
                        smsg += '<lefttime>' + est_time + '</lefttime></smsg>'     
                        print(smsg)
                        sys.stdout.flush()
                    
                    print('[PAGE '+str(i)+']',
                    len(postidlist) , '/', est_totalpost, '('+str(round(percent*100))+'%)', '\t' ,
                    round(readtime, 2) , '글/sec\t', est_time, '남음')
                    sys.stdout.flush()  
                        

        print('저장 완료')
        sys.stdout.flush()
        taskdone = True

    print("파일 쓰는 중...")
    sys.stdout.flush()
    f.close()
    print("쓰기 완료.")
    sys.stdout.flush()
    pass


# 코드 시작
def main():
    if len(sys.argv) < 4:
        execname = sys.argv[0]
        if execname.rfind('\\') != -1: execname = execname[execname.rfind('\\')+1:]

        print('Usage:\t', execname, 'savename gallid startnum endnum')
        print('\t', execname, '-r savename gallid startnum endnum')
        print('\t', execname, '-p savename gallid startpage endpage starttime endtime autostop=True/False')
        print('\t', execname, '-a filename savename\n')

        print('  savename', '저장 파일명', sep='\t')
        print('  gallid', '갤러리 ID', sep='\t')
        print('  startnum', '글 ID 시작 번호', sep='\t')
        print('  endnum', '글 ID 끝 번호', sep='\t')
        print('  startpage', '조회 시작 페이지 (페이지 모드시, 필수)', sep='\t')
        print('  endpage', '조회 끝 페이지 (페이지 모드시, 필수)', sep='\t')
        print('  starttime', '조회 시작 시간값 (UNIX)', sep='\t')
        print('  endtime', '조회 끝 시간값 (UNIX)', sep='\t')
        print('  -r', '', '갤러리 글 조회 모드 (속도 느림, 정확함)', sep='\t')
        print('  -ra', '', '글 조회 + 글 집계 모드 (기본값)', sep='\t')
        print('  -p', '', '갤러리 페이지 조회 모드 (속도 빠름, 부정확)', sep='\t')
        print('  -pa', '', '페이지 조회 + 글 집계 모드', sep='\t')
        print('  -a', '', '조회 글 집계 모드\n', sep='\t')

    else:
        # 모드 선택
        # -a : arrange - 정렬 모드
        if (sys.argv[1] == "-a" or sys.argv[1] == "--a"):
            arrange(sys.argv[2], sys.argv[3])
            sys.exit()

        # -ra : read arrange - 읽기 + 정렬
        if (sys.argv[1] == "-ra" or sys.argv[1] == "--ra"):
            gallreader(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
            arrange(sys.argv[2], sys.argv[2] + '-arranged')

        # -r : read - 읽기 모드
        if (sys.argv[1] == "-r" or sys.argv[1] == "--r"):
            gallreader(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
            sys.exit()

        # -p : page - 페이지 읽기 모드
        if (sys.argv[1] == "-p" or sys.argv[1] == "--p" or sys.argv[1] == "-pa" or sys.argv[1] == "--pa"):
            if (len(sys.argv) == 6) or (len(sys.argv) == 7 and embedmode): # 페이지 범위만 있을 경우
                gallreader_page(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))

            elif len(sys.argv) >= 8:
                autostop = True
                if len(sys.argv) == 9: autostop != (sys.argv[8]=='false' or sys.argv[8]=='False' or sys.argv[8]=='FALSE')
                gallreader_page(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), autostop)

            # -pa : page arrange - 페이지 읽기 + 정렬 모드
            if(sys.argv[1] == "-pa" or sys.argv[1] == "--pa"): arrange(sys.argv[2], sys.argv[2] + '-arranged')
            sys.exit()


        filename = sys.argv[1]
        gall = sys.argv[2]
        start = int(sys.argv[3])
        end = int(sys.argv[4])

        gallreader(filename, gall, start, end)
        arrange(filename, filename + '-arranged')


if __name__ == '__main__':
    main()


