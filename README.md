# gallreader
![img](gallreader_logo.png)

갤리더 - 간단 디시인사이드 글수집, 결산 (갤창랭킹) 프로그램

## Usage
```
.\gallreader.py savename gallid startnum endnum
.\gallreader.py -r savename gallid startnum endnum
.\gallreader.py -p savename gallid startpage endpage 
.\gallreader.py -p savename gallid startpage endpage starttime endtime autostop=True/False
.\gallreader.py -pa savename gallid startpage endpage starttime endtime
.\gallreader.py -a filename savename

  savename      저장 파일명
  gallid        갤러리 ID
  startnum      글 ID 시작 번호
  endnum        글 ID 끝 번호
  startpage     조회 시작 페이지 (페이지 모드시, 필수)
  endpage       조회 끝 페이지 (페이지 모드시, 필수)
  starttime     조회 시작 시간값 (UNIX)
  endtime       조회 끝 시간값 (UNIX)
  -r            갤러리 글 조회 모드 (속도 느림, 정확함)
  -ra           글 조회 + 글 집계 모드 (기본값)
  -p            갤러리 페이지 조회 모드 (속도 빠름, 부정확)
  -pa           페이지 조회 + 글 집계 모드
  -a            조회 글 집계 모드
  ```
