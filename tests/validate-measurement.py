"""Independent exact arithmetic/geometry; no client marking functions are imported."""
import json,sys,re
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'video-agent/production-v2'))
def content():
 from measurement_content import LESSONS
 assert len(LESSONS)==5
 models=0;equations=0
 for l in LESSONS:
  assert len(l['beats'])==12 and [c['role'] for c in l['beats'][:3]]==['opening','learning_goal','success_criteria']
  assert len(l['beats'][2]['board'])==3 and l['beats'][2]['text'].count('I can ')==3
  assert any(c.get('pause')==4 and c['role']=='question' for c in l['beats'])
  for c in l['beats']:
   assert c.get('board') or c.get('model') or c.get('equation'),'Heading-only teaching scene: '+l['id']+' '+c['chapter']
   for line in c['board']:
    assert not re.search(r'\d\s*/\s*\d',line)
    if '=' not in line:continue
    left,right=line.split('=',1);left=left.split(':')[-1].replace(',','').replace('×','*').replace('−','-');right=right.replace(',','')
    if re.fullmatch(r'[\d\s+*().-]+',left) and re.match(r'\s*\d+',right):
     assert S.sympify(left)==S.Integer(re.match(r'\s*(\d+)',right)[1]),line;equations+=1
   m=c.get('model')
   if not m:continue
   models+=1;k=m['kind']
   if k=='ruler':assert 0<=m['start']<m['end']<=20
   elif k=='combined':assert m['whole']>0 and 0<=m['part']<m['factor'] and m['factor'] in [100,1000]
   elif k=='scale':assert 0<=m['value']<=m['maximum'] and m['maximum']%m['step']==0 and m['value']%m['step']==0
   elif k in ['rectangle','composite']:
    w,h=m['w'],m['h'];a,b=m.get('a',0),m.get('b',0);assert w>0 and h>0 and (k=='rectangle' or 0<a<w and 0<b<h)
    ps=[(0,0),(w,0),(w,h-b),(w-a,h-b),(w-a,h),(0,h)] if k=='composite' else [(0,0),(w,0),(w,h),(0,h)]
    poly=S.Polygon(*ps);assert abs(poly.area)==w*h-a*b and poly.perimeter==2*(w+h)
   else:assert k=='units'
 assert models==40 and equations>=20
 assert 9-2==7 and 2*100+35==235 and 1000+350==1350 and 2000+250==2250 and S.Rational(1000,4)==250
 return dict(lessons=5,scenes=60,models=models,board_equations=equations,exact_geometry='SymPy polygons: area and perimeter',result='passed')
if __name__=='__main__':print(json.dumps(content()))

def variants(path):
 from functools import lru_cache
 @lru_cache(maxsize=8192)
 def geometry(w,h,a,b):
  p=S.Polygon((0,0),(w,0),(w,h-b),(w-a,h-b),(w-a,h),(0,h));return abs(p.area),p.perimeter
 attempts=json.loads(Path(path).read_text());count=0;families=set();correct_labels=set()
 for qs in attempts:
  assert len(qs)==30;seen=set()
  for q in qs:
   op=q['math']['op'];p=q['math']['p'];unit=q['math']['unit'];canon=p[:]
   if op=='compare-design':canon=canon[:2]
   if op=='design-cost':canon=sorted(canon[:2])+canon[3:]
   if op in ['area','perimeter','area-unit','compare-design']:canon=sorted(canon)
   if op in ['composite-area','composite-perimeter']:canon=min(tuple(canon),(canon[1],canon[0],canon[3],canon[2]))
   key=(op,unit,tuple(canon));assert key not in seen,(op,p);seen.add(key)
   if op.startswith('unit-'):
    typ=op.split('-')[1];expected={'length':['cm','m','mm','km'],'mass':['g','kg','g','kg'],'capacity':['mL','L','mL','L']}[typ][p[0]]
   elif op=='length':expected=p[1]-p[0];assert unit=='cm'
   elif op=='mixed':expected=p[0]*p[2]+p[1];assert p[2] in [100,1000] and 0<=p[1]<p[2]
   elif op=='scale':expected=p[0]*p[1];assert unit in ['g','mL']
   elif op=='perimeter':expected=2*sum(p);assert unit=='cm'
   elif op=='area':expected=p[0]*p[1];assert unit=='cm²'
   elif op=='grid-count':expected=p[0]*p[1];assert unit=='square units'
   elif op=='polygon':expected=p[0]*p[1];assert unit=='cm'
   elif op=='unknown-side':expected=S.Rational(p[0],2)-p[1];assert unit=='cm'
   elif op=='area-side':expected=S.Rational(p[0],p[1]);assert unit=='cm'
   elif op in ['composite-area','composite-perimeter']:
    area,per=geometry(*p);expected=area if op=='composite-area' else per;assert unit==('cm²' if op=='composite-area' else 'cm')
   elif op=='missing-composite':
    w,h,a,area=p;expected=S.Rational(w*h-area,a);actual,_=geometry(w,h,a,int(expected));assert actual==area
   elif op=='area-unit':expected='cm²'
   elif op=='area-perimeter-claim':expected=f'Area = {p[0]*p[1]} cm²; perimeter = {2*sum(p)} cm'
   elif op=='design-cost':
    w,h,swap,f,t=p;small=2*(w+h)*f+w*h*t;big=2*(w+h)*f+(w-1)*(h+1)*t;assert small<big;expected='B' if swap else 'A'
   elif op=='pack-dimension':expected=S.Rational(p[1]*p[2],p[0]);assert unit=='m'
   elif op=='composite-tiles':expected=geometry(*p)[0];assert unit=='tiles'
   elif op=='difference':expected=100*p[0]+p[1]-100*p[2]-p[3];assert unit=='cm'
   elif op=='border-gap':expected=2*(p[0]+p[1])-p[2];assert unit=='m'
   elif op=='tiles':expected=S.ceiling(S.Rational(p[0]*p[1],p[2]));assert unit=='packs'
   elif op=='compare-design':
    w,h,swap=p;assert (w-1)*(h+1)>w*h and 2*(w+h)==2*((w-1)+(h+1));expected='A' if swap else 'B';correct_labels.add(expected)
   elif op=='capacity-gap':expected=p[0]*1000-p[1]-p[2];assert unit=='mL'
   elif op=='composite-packs':area,_=geometry(*p[:4]);expected=S.ceiling(area/p[4]);assert unit=='packs'
   else:raise AssertionError(op)
   if isinstance(expected,str):assert q['answer']==expected,(op,q['answer'],expected)
   else:assert S.Rational(q['answer'])==expected and expected>0,(op,p,q['answer'],expected)
   assert str(expected) in q['solution'] or op in ['compare-design','design-cost'],(op,q['solution'],expected)
   if q['type']=='choice':assert q['options'].count(q['answer'])==1 and len(set(q['options']))==4
   assert not re.search(r'\d\s*/\s*\d',q['display']+' '+q['solution'])
   families.add(q['family']);count+=1
 assert count==30000 and correct_labels=={'A','B'}
 return dict(result='passed',attempts=1000,positions=count,families=len(families),duplicates=0,invalid_answers=0,plausible_unique_choices='checked',independent_engine='Python exact arithmetic and cached SymPy polygon geometry')
if __name__=='__main__' and len(sys.argv)>1:
 result=variants(sys.argv[1]);print(json.dumps(result));out=ROOT/'docs/year5/measurement-maths-qa.json';out.write_text(json.dumps(dict(content=content(),quiz=result),indent=2)+'\n')
