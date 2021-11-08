# 디시콘 url이 저장된 txt 파일을 읽어 일괄 다운로드하는 스크립트
# ./out 디렉토리가 있어야 합니다

from requests import get
import re, time

listfilename = input('url 리스트 텍스트 파일?(.txt):')
content = open(listfilename + '.txt', 'r').read()

c = content.split('\n')
postlist = []

for i in c:
    postlist.append(i)

def download(url, file_name):
    response = get(url)
    d = response.headers['content-disposition']
    fname = re.findall("filename=(.+)", d)[0]

    file_name += fname[fname.rfind('.'):]

    with open(file_name, "wb") as file:
        file.write(response.content)

count = 0

for l in postlist:
    count += 1
    print(count, '번째 다운로드중...')
    download(l, 'out/'+str(count))
    time.sleep(0.2)
