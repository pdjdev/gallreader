import pandas as pd

# 통피 리스트
SKTip = ['203.226', '211.234', '223.32', '223.33', '223.34', '223.35', '223.36', '223.37', '223.38', '223.39', '223.40','223.41', '223.42', '223.43', '223.44', '223.45', '223.46', '223.47', '223.48', '223.49', '223.50', '223.51', '223.52', '223.53', '223.54', '223.55', '223.56', '223.57', '223.58', '223.59', '223.60', '223.61', '223.62', '223.63']
KTip = ['39.7', '110.70', '175.223', '175.252', '211.246', '118.235']
LGTip = ['61.43', '211.234', '117.111', '211.36', '106.102']

filename = input('처리한 파일명? (.csv):')
savename = input('처리후 저장할 파일명? (.csv):')

# 기존 CSV 불러옴
data = pd.read_csv(filename + '.csv', dtype={'IPID':str})

gonic = data[data['HasAccount']==1] # 고닉과
udong = data[data['HasAccount']==0] # 유동글

# 새로운 데이터 생성
res = pd.DataFrame(columns=['Nick', 'IPID', 'Posts', 'Upvotes', 'Downvotes', 'Comments', 'Views', 'HasAccount'])

idList = gonic.IPID.unique().tolist() # ID 값 모으기 (고닉)
ipList = udong.IPID.unique().tolist() # IP 값 모으기 (유동)
unickList = udong.Nickname.unique().tolist() # 유동닉 값 모으기 (유동)

# 고닉 다중이 목록 불러오기
tmp = open('dup_list_id.txt', 'r', encoding='utf-8')
dup_list_id = tmp.read().split('\n')
tmp.close()

# 유동 다중ip 목록 불러오기
tmp = open('dup_list_ip.txt', 'r', encoding='utf-8')
dup_list_ip = tmp.read().split('\n')
tmp.close()

# 유동 다중닉 목록 불러오기
tmp = open('dup_list_nick.txt', 'r', encoding='utf-8')
dup_list_nick = tmp.read().split('\n')
tmp.close()

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



################### 고닉 글 집계 ###################
        
for ids in idList:    
    col = gonic[gonic['IPID'].isin(ids.split('\t'))]
    col2 = udong[udong['IPID'].isin(ids.split('\t'))] # 유동 아이피도 넣기
    col = pd.concat([col, col2])

    nicks = ' '.join(col.Nickname.unique().tolist())
    ids2 = ' '.join(col.IPID.unique().tolist())
    
    counts = col.shape[0] # 글 수
    upvotes = col.Upvotes.sum() # 추천수
    downvotes = col.Downvotes.sum() # 비추수
    comments = col.Comments.sum() # 받은댓글수
    views = col.Views.sum() # 조회수
        
    nd = {'Nick' : nicks, 'IPID' : ids2, 'Posts' : counts, 'Upvotes' : upvotes, 'Downvotes' : downvotes, 'Comments' : comments, 'Views' : views, 'HasAccount' : 1}
    res = res.append(nd, ignore_index=True)




################### 유동 글 집계 ###################
    
# 닉네임이 ㅇㅇ이고 통피인놈들을 일단 묶어서 통계내기
for ips in [SKTip, KTip, LGTip]:   
    col = udong[(udong['IPID'].isin(ips)) & (udong['Nickname']=='ㅇㅇ')]
    if col.shape[0] > 0:
        nicks = 'ㅇㅇ(통피)'
        ids2 = ' '.join(col.IPID.unique().tolist())
        counts = col.shape[0] # 글 수
        upvotes = col.Upvotes.sum() # 추천수
        downvotes = col.Downvotes.sum() # 비추수
        comments = col.Comments.sum() # 받은댓글수
        views = col.Views.sum() # 조회수
            
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
        downvotes = col.Downvotes.sum() # 비추수
        comments = col.Comments.sum() # 받은댓글수
        views = col.Views.sum() # 조회수
            
        nd = {'Nick' : nicks, 'IPID' : ids2, 'Posts' : counts, 'Upvotes' : upvotes, 'Downvotes' : downvotes, 'Comments' : comments, 'Views' : views, 'HasAccount' : 0}
        res = res.append(nd, ignore_index=True)
        udong = udong.drop(col.index)
        
    
# 닉네임이 ㅇㅇ가 아닌 유동닉글들 수집
for nicks in unickList:
    col = udong[udong['Nickname'].isin(nicks.split('\t'))]
    if col.shape[0] > 0:
        nicks = ' '.join(col.Nickname.unique().tolist())
        ids2 = ' '.join(col.IPID.unique().tolist())
        counts = col.shape[0] # 글 수
        upvotes = col.Upvotes.sum() # 추천수
        downvotes = col.Downvotes.sum() # 비추수
        comments = col.Comments.sum() # 받은댓글수
        views = col.Views.sum() # 조회수
            
        nd = {'Nick' : nicks, 'IPID' : ids2, 'Posts' : counts, 'Upvotes' : upvotes, 'Downvotes' : downvotes, 'Comments' : comments, 'Views' : views, 'HasAccount' : 0}
        res = res.append(nd, ignore_index=True)


res.to_csv(savename + '.csv', encoding='utf-8-sig', index=False)
