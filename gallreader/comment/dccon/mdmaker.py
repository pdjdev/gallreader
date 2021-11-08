# 디시콘 랭킹 표를 마크다운 문법에 맞춰 생성하는 스크립트
# ./out 폴더에 저장된 디시콘 이미지들과 디시콘 사용횟수(Count)가 줄바꿈 문자로 구분된 텍스트 파일이 있어야 합니다.

import os.path

listfilename = input('Count 텍스트 파일?(.txt):')
content = open(listfilename + '.txt', 'r').read()

c = content.split('\n')
clist = []

for i in c:
    clist.append(i)

totalnum = 200    # 총 갯수
width = 3         # 열 갯수
prevnum = -1
lastnum = -1

pg = '|순위|이미지|사용횟수' * width
pg += '|\n'
pg += '|-|-|-' * width
pg += '|\n'

fname = []
for i in range(1, totalnum + 1, 1):
    if os.path.isfile('out\\' + str(i) + '.png'):
        fname.append(str(i) + '.png')
    else:
        fname.append(str(i) + '.gif')
    
    # pg += '|' + str(i) + '|' + '|' + str(i) + '|' + 



for i in range(totalnum):
    nst = i+1

    if (clist[i] == prevnum):
        nst = lastnum
    else:
        lastnum = nst

    pg += '|**' + str(nst) + '**|![' + str(i+1) + '](img/'+ fname[i] + ')|' + clist[i]

    prevnum = clist[i]

    if ((i+1) % width == 0):
        pg += '|\n'

pg += '|'

print(pg)
