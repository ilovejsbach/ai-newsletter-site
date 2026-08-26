# AI 주간 뉴스레터 — 내부망 깃랩 Pages 운영 매뉴얼

게시판(나모웹에디터, JS 불가)에 iframe으로 뉴스레터 HTML을 게시하기 위한 절차.
이 폴더 전체가 배포 단위이며, 외부 CDN 참조 없이 자체 서빙되도록 만들어져 있다.

## 폴더 구조

```
.gitlab-ci.yml     ← push하면 Pages로 자동 배포하는 CI 설정 (깃랩 전용)
index.html         ← 전체 호 아카이브 목록
latest/            ← 최신 호로 자동 이동 (게시판 고정 글용)
fonts/             ← Pretendard 폰트 (전 주차 공유, 1회만 존재)
2026-06-25/ …      ← 주차별 뉴스레터 (index.html + articles/ + assets/)
```

## 1회 초기 구축 (내부망)

1. **선결 확인**: 사내 깃랩 관리자에게 "GitLab Pages 기능이 켜져 있는지" 확인.
2. 깃랩에 새 프로젝트 생성 (예: `ai-newsletter-site`).
3. 이 폴더 내용물을 통째로 풀어 넣고 push:
   ```
   git init && git add -A && git commit -m "init"
   git remote add origin <깃랩 프로젝트 URL>
   git push -u origin main
   ```
4. push 후 CI(pages job)가 자동 실행된다. 프로젝트의 **배포 > Pages** 메뉴에서
   사이트 URL 확인 (형태: `https://<pages-도메인>/<그룹>/ai-newsletter-site/`).
5. 러너가 외부 이미지를 못 받아 CI가 실패하면 `.gitlab-ci.yml`의 `image:` 줄을
   사내 레지스트리 이미지로 바꾸거나 삭제 (파일 안 주석 참고).

## 게시판 게시 (나모웹에디터)

HTML 소스 모드에 아래 한 줄. JS 불필요, iframe 안에서 기사 이동·복귀 네비게이션 동작.

```html
<iframe src="https://<Pages주소>/2026-08-18/" width="100%" height="1600" style="border:0"></iframe>
```

- **주차별 글**: 매주 새 글에 해당 주차 URL.
- **고정 글 운용**: `…/latest/`를 걸면 글 하나로 항상 최신 호 표시.
- 높이는 고정값이므로 1600~1800 권장 (내용이 길면 iframe 내부 스크롤).

## 매주 운영 (화요일)

**외부망** — 세 명령:
```
uv run ai-newsletter build --selection-mode heat
uv run ai-newsletter humanize outputs/<이번주 폴더> --capture
uv run python scripts/build_site.py outputs/<이번주 폴더> ~/workspace/ai-newsletter-site
```

**망간 이동** — 델타 zip 하나만 옮기면 됨:
```
uv run python scripts/make_delta_zip.py ~/workspace/ai-newsletter-site
```
(외부망에서 실행 — 새 주차 폴더 + index.html + latest/ 에 더해, 직전 주 이후
바뀐 그 외 파일까지 git 이력으로 자동 감지해 담는다. 보통 5~10MB.)
zip 안 경로가 저장소 루트 기준이라, 내부망 git 작업 폴더에 **그대로 풀면 끝**.

**내부망** — 깃랩 저장소에 복사 후:
```
git add -A && git commit -m "2026-08-25 호" && git push
```
push하면 Pages가 자동 갱신된다. 게시판에 새 글(iframe) 등록으로 마무리.

## 문제 해결

| 증상 | 원인/조치 |
|---|---|
| iframe이 빈 화면 | 저장소 파일 뷰어 URL을 쓴 경우 — 반드시 **Pages URL** 사용 |
| 폰트가 고딕으로 나옴 | `fonts/` 폴더 누락 — 사이트 루트에 있는지 확인 |
| CI 실패 (image pull) | `.gitlab-ci.yml`의 `image:` 줄 조정 (파일 내 주석) |
| 구형 6/25호 히어로 빈 이미지 | 원본 CDN 소실로 로컬화 불가 — 해당 호만 알려진 제약 |
