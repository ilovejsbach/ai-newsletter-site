#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministically render projection-backed, Korean-first detail pages."""
import html, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'gartner-observed-catalog-20260910/projection.json'
OUT=ROOT/'gartner-observed-catalog-20260910/articles'
PROV=ROOT/'gartner-observed-catalog-20260910/reconstruction-provenance.json'
TITLES={'7453226':'2026 AI 리더 우선순위: 기업 AI 가치 실현을 규모 있게 가속하기','8342617':'기업용 AI 어시스턴트를 위한 매직 쿼드런트','8343317':'이노베이션 인사이트: 음성 AI 에이전트','8350517':'퍼스트 테이크: Salesforce의 AI 전면 개편, 비용과 종속 위험의 확대','8358749':'감사 2030: 내부감사를 재편할 8가지 동력'}
KO={'Overview':'개요','Key Findings':'핵심 발견','Recommendations':'권고사항','Analysis':'분석','Market Overview':'시장 개요','Description':'설명','Architecture Tiers':'아키텍처 계층','Production Mechanics':'생산 메커니즘','Benefits and Uses':'효익과 활용','Risks':'위험','Adoption Rate':'도입률','Alternatives':'대안','Representative Providers':'대표 공급자','Issue':'이슈','Impact':'영향','More Detail':'상세 내용','Technological Forces':'기술 동력','External Environment Forces':'외부 환경 동력','Talent Forces':'인재 동력','Strategic Planning Assumption':'전략적 계획 가정','Evolving Insights History':'진화하는 인사이트 이력','PERENNIAL PRIORITIES':'상시 우선순위','Insights at a Glance':'인사이트 한눈에 보기'}
TERMS={'AI':'인공지능: 업무와 의사결정을 지원하는 기술 범주','Automation':'자동화: 반복 작업을 시스템이 수행하는 방식','Voice':'음성: 말소리 입력과 대화형 출력을 쓰는 인터페이스','Salesforce':'Salesforce: 기업용 영업·서비스 플랫폼','Enterprise':'기업용: 조직 단위 운영과 통제를 전제로 하는 범주','Audit':'감사: 위험·통제·거버넌스를 평가하는 기능','Value':'가치: 투자에서 측정 가능한 사업 성과로 이어지는 결과'}
CSS='body{font:16px/1.6 system-ui,sans-serif;max-width:1080px;margin:auto;padding:28px 20px;color:#17212b;background:#f5f8fa}a{color:#075985}.card{background:#fff;border:1px solid #d8e2e8;border-radius:14px;padding:16px;margin:12px 0}.finding{border-left:4px solid #38bdf8;background:#f8fafc;padding:15px;font-size:18px}.unknown{color:#92400e;background:#fff7ed;border:1px solid #fed7aa;padding:2px 6px;border-radius:5px}.observed{color:#166534;background:#f0fdf4;border:1px solid #bbf7d0;padding:2px 6px;border-radius:5px}.muted,small{color:#667684}.chip{display:inline-block;border:1px solid #d8e2e8;border-radius:99px;padding:3px 8px;margin:3px}.ko{font-size:17px}.original{color:#667684}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}@media(max-width:720px){.grid{grid-template-columns:1fr}}'
def e(x): return html.escape(str(x or ''),quote=True)
def clean(x): return re.sub(r'\s+',' ',str(x or '')).strip()
def flat(xs):
 out=[]
 for x in xs or []: out += [x]+flat(x.get('children',[]))
 return out
def ex(s):
 vals=[]
 for x in s.get('excerpts',[]):
  t=clean(x.get('text'))
  if t and t not in vals: vals.append(t)
 return ' '.join(vals)
def kind(title):
 return 'Magic Quadrant' if 'Magic Quadrant' in title else 'Innovation Insight' if title.startswith('Innovation Insight') else 'First Take' if title.startswith('First Take') else 'Audit outlook' if title.startswith('Audit') else 'Priority analysis'
def render(a):
 aid=str(a['article_id']); title=clean(a.get('title')); fs=a.get('fidelity') or {}
 sections=[s for s in flat(a.get('sections',[])) if clean(s.get('heading')) and clean(s.get('heading')) not in {'Evidence','We use cookies to improve your experience'}]
 contexts=[ex(s) for s in sections if ex(s)]; core=max(contexts,key=len)[:720] if contexts else '관측된 bounded context 발췌가 없습니다.'
 pub=next((x for x in contexts if re.search(r'\b\d{1,2} \w+ 2026\b',x)),'발행 문맥은 별도로 관측되지 않았습니다.')
 topics=[]
 for x in (a.get('terms') or []):
  t=clean(x.get('term') if isinstance(x,dict) else x)
  if t and t not in topics: topics.append(t)
 for x in a.get('links',[]):
  t=clean(x.get('link_text_raw'))
  if t and len(t)<80 and re.search('AI|Automation|Audit|Salesforce|Enterprise|Voice|Value|Platform|Technology|Procurement',t,re.I) and t not in topics: topics.append(t)
 topics=topics[:12]
 rows=[]
 for s in sections:
  h=clean(s.get('heading')); text=ex(s); ko=KO.get(h,'한국어 제목이 별도로 관측되지 않음')
  rows.append(f'<article class="card"><b>{e(s.get("level","section"))}</b> <span class="unknown">경계 unknown</span><h3>{e(ko)}</h3><p class="original">원문 섹션: {e(h)}</p><p class="ko">이 섹션은 {e(ko)} 주제를 다루는 것으로 관측되었습니다. 아래는 확인된 짧은 원문 맥락입니다.</p><p class="original">{e(text[:620] or "발췌 없음")}{"…" if len(text)>620 else ""}</p><small>bounded context 관측 · 섹션 본문 전문의 복사가 아님</small></article>')
 chips=''.join(f'<span class="chip">{e(t)}</span>' for t in topics) or '<span class="muted">별도 주제·용어 필드 없음</span>'
 termrows=[]
 for t in topics:
  for k,v in TERMS.items():
   if k.lower() in t.lower(): termrows.append(f'<li><b>{e(k)}</b> — {e(v)}</li>'); break
 assets=a.get('assets') or []; table='표/이력 context 관측' if any(re.search('table|history',ex(s),re.I) for s in sections) else '표 context 미관측'
 orig=next((x for x in a.get('links',[]) if 'document' in x.get('href_raw','')),None)
 rec=next((ex(s) for s in sections if clean(s.get('heading'))=='Recommendations'),None)
 rec_html=f'<p class="finding original">{e(rec[:620])}</p>' if rec else '<p class="muted">Recommendations 제목은 별도로 관측되지 않았습니다.</p>'
 asset_html=''.join(f'<li>{e(x.get("kind","asset"))} · {e((x.get("metadata") or {}).get("alt") or "alt text 미관측")} <span class="unknown">확보 unknown</span></li>' for x in assets[:14]) or '<li class="muted">이미지·그림 레코드 없음</li>'
 return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(TITLES.get(aid,title))} · Observed Gartner</title><style>{CSS}</style></head><body><a href="../index.html">← 관측 카탈로그로 돌아가기</a><p><small>관측 연구 아티클 · article_id {e(aid)}</small></p><h1>{e(TITLES.get(aid,title))}</h1><p class="original">원문 제목: {e(title)}</p><p><b>유형</b> <span class="observed">{e(kind(title))}</span></p><p class="ko">공개 projection의 제한된 관측값으로 만든 내부용 재구성입니다. 한국어 설명은 관측 본문 전문 번역이 아닌 파생 설명이며 unknown을 유지합니다.</p><section class="card"><b>관측 발행 문맥</b><p>{e(pub)}</p><b>출처 모드</b> <span class="observed">observed_raw</span>　<b>충실도</b> <span class="unknown">{e(fs.get('status','unknown'))}</span></section><h2>핵심 관측 내용</h2><p class="ko">이 문서는 위 제목과 관련된 맥락을 보여주며, 아래는 실제 projection에서 확인된 짧은 원문 발췌입니다.</p><p class="finding original">{e(core)}{"…" if contexts and len(max(contexts,key=len))>720 else ""}</p><small>context observation · 전문 복사·전문 번역 아님 · full-body fidelity <span class="unknown">false</span></small><h2>관측된 섹션과 한국어 요약</h2><div class="grid">{"".join(rows)}</div><h2>주제·키워드·용어 설명</h2><div>{chips}</div><ul>{''.join(termrows) or '<li class="muted">관측된 용어 정의 없음</li>'}</ul><h2>권고사항(관측 범위)</h2><p class="ko">Recommendations 제목이 관측된 경우에만 아래 내용을 권고 섹션으로 표시합니다. 한국어 설명은 파생 설명이고 발췌는 원문 표현입니다.</p>{rec_html}<h2>이미지·그림·표 상태</h2><p>자산 레코드: {len(assets)}건 · 이미지/그림 확보: <span class="unknown">unknown</span> · {e(table)}</p><ul>{asset_html}</ul><section class="card"><b>충실도 경계</b><p>관측 본문 길이: {e(fs.get('body_length_observed','unknown'))}자. 섹션 경계·링크 위치·자산 확보·날짜 의미·전체 주장 관계는 <span class="unknown">unknown</span>입니다. 한국어 요약은 관측 본문 전문 번역이 아닌 파생 설명입니다.</p></section>{f'<p><a href="{e(orig.get("href_raw"))}" target="_blank" rel="noopener">원문 보조 링크 ↗</a></p>' if orig else '<p class="muted">원문 링크 미관측</p>'}<footer><small>Projection 기반 · raw/session 자료와 credentials 제외</small></footer></body></html>'''
def main():
 data=json.loads(DATA.read_text()); expected={'7453226','8342617','8343317','8350517','8358749'}
 assert {str(a['article_id']) for a in data.get('articles',[])}==expected
 for a in data['articles']:(OUT/f"{a['article_id']}.html").write_text(render(a),encoding='utf-8')
 PROV.write_text(json.dumps({'schema':'gartner.observed.reconstruction/v1','generator':'scripts/rebuild_gartner_observed_articles.py','input':'projection.json','provenance_mode':'observed_raw','model':None,'prompt':None,'translation':'deterministic Korean label and summary map; no LLM call','fidelity_policy':'preserve partial/unknown values; context excerpts are not copied bodies','excluded':['raw/session files','credentials']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('rendered',len(data['articles']))
if __name__=='__main__':main()
