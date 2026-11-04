"""Two existing-topic graphic corrections; no narration/video generation or integration."""
import sys,json,copy
from pathlib import Path
from fractions import Fraction
from contract import ROOT,load,branded,rendered_texts
sys.path.insert(0,str(ROOT/'video-agent/production-v2'))
from graphics import draw,text,TEAL
from PIL import Image,ImageDraw

def main():
 load();db=json.loads((ROOT/'docs/video-quality-audit-35.json').read_text());out=ROOT/'docs/video-quality-evidence/visual-corrections';out.mkdir(exist_ok=True)
 for number,index in [(14,5),(15,6)]:
  r=db['records'][number-1];l=json.loads((ROOT/r['script']).read_text());c=copy.deepcopy(l['beats'][index]);assert not any(branded(s) for s in rendered_texts(c))
  if number==14:
   c['board']=[];c['equation']=[[1,2],'=','0.5','=','50%'];c['line']={'d':2,'maximum':1,'points':[1]};assert Fraction(1,2)==Fraction('0.5');name='14-midpoint';c['note']='The same position: one half = 0.5 = 50%'
  else:
   c['board']=['50% ? 40%'];c['rows']=[{'n':5,'d':10,'label':'One half: 5 tenths = 50%','colour':'teal'},{'n':4,'d':10,'label':'0.4: four tenths = 40%','colour':'gold'}];assert Fraction(5,10)>Fraction(4,10);name='15-equal-bars';c['note']='Equal wholes and equal tenths make the comparison fair.'
  draw(l,c,out/(name+'.png'),1)
  if number==14:
   im=Image.open(out/(name+'.png'));pen=ImageDraw.Draw(im);pen.rectangle((900,640,1020,740),fill='white');text(pen,'0.5 = 50%',960,690,42,TEAL,True);im.save(out/(name+'.png'))
  (out/(name+'.json')).write_text(json.dumps({'number':number,'scene':index,'status':'Graphic draft only; not integrated or released','changes':c,'mathematics':'Independent Fraction arithmetic checked; reuse existing stacked-fraction/number-line/bar primitives'},indent=2)+'\n')
 print('Two confirmed missing-model corrections prepared with existing primitives; no MP4/narration generation.')
if __name__=='__main__':main()
