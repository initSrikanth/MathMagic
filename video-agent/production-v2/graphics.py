"""1920×1080 geometry, with equal wholes and stacked fractions throughout."""
from PIL import Image, ImageDraw, ImageFont
import math
import re
W,H=1920,1080
BG='#FFF9EF'; INK='#183647'; TEAL='#087F7A'; GOLD='#A95704'; BLUE='#1768B2'; EMPTY='#DCECE6'; MUTED='#455D68'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(size): return ImageFont.truetype(FONT,size)
def width(s,size): return ImageDraw.Draw(Image.new('RGB',(1,1))).textlength(str(s),font=font(size))
def text(d,s,x,y,size=40,fill=INK,center=False,maxw=1670):
    while width(s,size)>maxw: size-=1
    d.text((x,y),str(s),font=font(size),fill=fill,anchor='mt' if center else 'lt')
def wrapped(d,s,y,size=38,maxw=1650,fill=MUTED):
    lines=[]; line=''
    for w in s.split():
        if width((line+' '+w).strip(),size)>maxw:
            lines.append(line); line=w
        else: line=(line+' '+w).strip()
    if line: lines.append(line)
    for l in lines:
        text(d,l,W/2,y,size,fill,True,maxw); y+=size*1.45
    return y

def frac_width(t,size):
    if len(t)==3: return width(t[0],size)+30+frac_width(t[1:],size)
    return max(width(t[0],size),width(t[1],size))+20

def fraction(d,t,x,y,size=64,fill=INK):
    if len(t)==3:
        text(d,t[0],x,y+size*.25,size,fill); x+=width(t[0],size)+30; t=t[1:]
    w=frac_width(t,size)
    text(d,t[0],x+w/2,y-size*.48,size,fill,True)
    d.line((x,y+size*.68,x+w,y+size*.68),fill=fill,width=4)
    text(d,t[1],x+w/2,y+size*.86,size,fill,True)

def equation(d,tokens,y=290):
    size=65; gap=32
    def tw(t): return frac_width(t,size) if isinstance(t,list) else width(t,size)
    while sum(tw(t) for t in tokens)+gap*(len(tokens)-1)>1620: size-=1
    x=(W-sum(tw(t) for t in tokens)-gap*(len(tokens)-1))/2
    for t in tokens:
        if isinstance(t,list): fraction(d,t,x,y,size)
        else: text(d,t,x,y+12,size,TEAL if t in ['=','>','<','≠'] else INK)
        x+=tw(t)+gap

def mathematical_board(line):
    # Keep the approved spoken wording, but typeset familiar fractions conventionally.
    for words,notation in [('three quarters','3/4'),('one quarter','1/4'),('one half','1/2'),('one fifth','1/5'),('one tenth','1/10')]:
        line=re.sub(r'\b'+words+r'\b',notation,line,flags=re.I)
    return line

def draw_column(d,m):
    w=m['width']; labels=['Ten\nthousands','Thousands','Hundreds','Tens','Ones'][-w:]; cw=1120/w; left=450
    a=str(m['a']).rjust(w,'0'); b=str(m['b']).rjust(w,'0'); result=str(m.get('result','')).rjust(w)
    for i,label in enumerate(labels):
        x=left+(i+.5)*cw
        for k,part in enumerate(label.split('\n')):text(d,part,x,(490+k*24) if '\n' in label else 514,26,INK,True,maxw=cw-12)
        annotation=m.get('regroup',m.get('carry',['']*w))[i]
        if annotation!='':text(d,str(annotation),x,555,33,GOLD,True)
        text(d,a[i],x,600,58,INK,True)
        if 'regroup' in m and int(a[i])!=annotation:d.line((x-23,628,x+23,628),fill=GOLD,width=3)
        text(d,b[i],x,670,58,INK,True)
        if result[i]!=' ':text(d,result[i],x,753,61,TEAL,True)
    text(d,m['op'],320,670,58,INK,True)
    d.line((360,738,1600,738),fill=INK,width=4)

def draw_part_bar(d,m,progress):
    values=m['values'];total=sum(values);left=300;span=1320;x=left
    for i,(v,label) in enumerate(zip(values,m['labels'])):
        width=span*v/total
        d.rectangle((x,570,x+width,690),fill=TEAL if i%2==0 else GOLD,outline='white',width=4)
        text(d,label,x+width/2,610,42,'white',True,maxw=width-24);x+=width
    d.line((left,730,left+span*progress,730),fill=INK,width=4)
    text(d,'Total: '+m['total'],960,770,44,INK,True)

def draw_array(d,m,progress):
    r,c=m['rows'],m['cols'];cell=min(90,1200/c,220/r);left=(W-c*cell)/2;top=560
    for row in range(r):
        for col in range(c):
            x=left+(col+.5)*cell;y=top+(row+.5)*cell;colour=TEAL if (col<m['split'] if 'split' in m else row%2==0) else GOLD
            d.ellipse((x-cell*.22,y-cell*.22,x+cell*.22,y+cell*.22),fill=colour if row*c+col<r*c*progress else EMPTY)
    if not m.get('hide_labels'):text(d,f'{r} equal rows of {c}',960,810,38,INK,True)

def draw_products(d,m,progress):
    n=len(m['parts']);cw=1500/n;results=[]
    text(d,'Divide each useful part' if m['operation']=='÷' else 'Multiply each useful part',960,500,31,INK,True)
    for i,part in enumerate(m['parts']):
        x=210+i*cw;value=part//m['other'] if m['operation']=='÷' else part*m['other'];results.append(value)
        d.rounded_rectangle((x,545,x+cw-20,750),radius=18,fill=EMPTY,outline=TEAL,width=3)
        a,b=(m['other'],part) if m['side']=='multiplier' else (part,m['other'])
        text(d,f'{a:,} {m["operation"]} {b:,}',x+(cw-20)/2,570,47,INK,True,maxw=cw-50)
        text(d,f'{value:,}' if i<m['reveal'] else '?',x+(cw-20)/2,650,65,TEAL,True,maxw=cw-50)
        if i<m['reveal']:d.line((x+25,740,x+25+(cw-70)*progress,740),fill=GOLD,width=5)
    total=' + '.join(f'{v:,}' for v in results)+' = '+f'{sum(results):,}' if m['reveal']==n else 'Total: ?'
    text(d,total,960,805,43,INK,True,maxw=1600)

def draw_groups(d,m,progress):
    q,r=divmod(m['total'],m['size']);n=q+bool(r and m['round_up']);size=m['size']
    for j in range(n):
        x=220+(j%5)*290;y=520+(j//5)*170
        d.rounded_rectangle((x,y,x+260,y+125),radius=14,fill=EMPTY,outline=INK,width=2)
        text(d,m.get('unit','Group')+' '+str(j+1),x+130,y+8,26,INK,True)
        for k in range(size):
            cx=x+40+(k%4)*55;cy=y+58+(k//4)*(27 if size>8 else 40);chosen=j*size+k<m['total'];col=(GOLD if j==q else TEAL) if chosen else 'white'
            d.ellipse((cx-10,cy-10,cx+10,cy+10),fill=col if j*size+k<m['total']*progress else 'white',outline=INK,width=1)
    if r and not m['round_up']:
        x=220+(q%5)*290;y=520+(q//5)*170
        text(d,str(r)+' left over',x+130,y+10,30,GOLD,True)
        for k in range(r):
            cx=x+45+k*55;cy=y+75;d.ellipse((cx-10,cy-10,cx+10,cy+10),fill=GOLD,outline=INK,width=1)

def draw_share(d,m,progress):
    q,r=divmod(m['total'],m['groups']);reveal=m['reveal']
    text(d,f'{r} litres shared equally between {m["groups"]} containers' if reveal else f'{r} litres still to share',960,495,32,INK,True)
    for j in range(m['groups']):
        x=200+j*400;d.rounded_rectangle((x,540,x+320,815),radius=15,fill=EMPTY,outline=TEAL,width=3)
        text(d,'Container '+str(j+1),x+160,560,32,INK,True)
        for i in range(q):
            left=x+20+i*45;d.rectangle((left,630,left+40,680),fill=TEAL,outline='white',width=2)
        if reveal:
            left=x+20+q*45;d.rectangle((left,630,left+40,680),fill='white',outline=INK,width=2);d.rectangle((left,630,left+40*r/m['groups']*progress,680),fill=GOLD)
            for k in range(1,m['groups']):d.line((left+40*k/m['groups'],630,left+40*k/m['groups'],680),fill=INK,width=1)
            notation=[q,r,m['groups']];fw=frac_width(notation,34);fraction(d,notation,x+145-fw/2,720,34,INK);text(d,'L',x+155+fw/2,740,30,INK)
        else:text(d,str(q)+' L each',x+160,735,38,INK,True)

def draw_family(d,m,progress):
    labels=m.get('labels',['Number of groups','In each group','Total']);values=['?' if m['unknown'] else f'{m["groups"]:,}',f'{m["each"]:,}',f'{m["total"]:,}']
    text(d,'Estimate' if m.get('approximate') else 'Equal-group relationship',960,500,32,INK,True)
    for i,(label,value) in enumerate(zip(labels,values)):
        x=210+i*500;d.rounded_rectangle((x,545,x+480,750),radius=18,fill=EMPTY,outline=TEAL,width=3)
        text(d,label,x+240,568,32,INK,True,maxw=450);text(d,('About ' if m.get('approximate') else '')+value,x+240,650,65,TEAL,True,maxw=450)
    equation_text=('?' if m['unknown'] else f'{m["groups"]:,}')+' × '+f'{m["each"]:,}'+' = '+f'{m["total"]:,}'
    text(d,equation_text,960,805,43,INK,True)

def draw(lesson,cue,path,progress=1):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    d.rounded_rectangle((45,35,1875,1035),radius=35,fill='white',outline='#DBE7DF',width=3)
    text(d,lesson['title'],1830-width(lesson['title'],30),68,30,MUTED,maxw=1400)
    d.line((90,130,1830,130),fill=EMPTY,width=3)
    text(d,cue['chapter'],W/2,175,51,INK,True)
    if cue.get('equation'): equation(d,cue['equation'])
    rows=cue.get('rows',[])
    if rows:
        # A whole has the same length in every row, even with mixed numbers.
        wholes=max(max(1,math.ceil(r['n']/r['d'])) for r in rows)
        unit=1260/wholes
        for j,r in enumerate(rows):
            y=490+j*170; n,den=r['n'],r['d']; cell=unit/den
            text(d,r['label'],260,y-48,30,MUTED)
            count=max(1,math.ceil(n/den))*den
            for i in range(count):
                x=260+i*cell
                fill=TEAL if r['colour']=='teal' else GOLD
                d.rectangle((round(x),y,round(x+cell),y+58),fill=fill if i<n*progress else EMPTY,outline='white',width=2)
            for k in range(count//den+1):
                x=260+k*unit; d.line((x,y,x,y+58),fill=INK,width=4)
            fraction(d,[n,den],1580,y-9,37,TEAL)
    l=cue.get('line')
    if l:
        y=610; x0=210; span=1500; den=l['d']; total=den*l['maximum']
        d.line((x0,y,x0+span,y),fill=MUTED,width=5)
        for i in range(total+1):
            x=x0+span*i/total
            d.line((x,y-16,x,y+16),fill=INK,width=3)
            if i%den==0: text(d,i//den,x,y+34,35,INK,True)
            elif total<=8: fraction(d,[i,den],x-23,y+40,29,MUTED)
        for j,p in enumerate(l['points']):
            x=x0+span*p/total
            if progress>.3:
                d.ellipse((x-11,y-11,x+11,y+11),fill=TEAL)
                fraction(d,[p,den],x-30,y-140,39,TEAL)
        jump=l.get('jump')
        if jump:
            a,b=jump; x1=x0+span*a/total; x2=x0+span*b/total
            xe=x1+(x2-x1)*progress
            d.line((x1,y-30,xe,y-30),fill=GOLD,width=7)
    if cue.get('area'):
        n,den=cue['area']; box=(735,445,1185,895)
        for i in range(den):
            d.pieslice(box,-90+i*360/den,-90+(i+1)*360/den,fill=TEAL if i<n*progress else EMPTY,outline='white',width=5)
    board=cue.get('board',[])
    # Concept diagrams for new topics also appear during openings and recaps.
    if not board and not cue.get('equation') and not rows and not l and not cue.get('area') and not cue.get('model'):
        topic=lesson['topic']; section=lesson['section']
        if topic=='addition-subtraction':
            wrapped(d,'Parts combine to make a total.',320,48)
            d.rounded_rectangle((300,520,1620,650),radius=12,fill=EMPTY,outline=INK,width=3)
            d.rectangle((300,520,970,650),fill=TEAL)
            text(d,'Known part',635,562,40,'white',True)
            text(d,'Other part',1295,562,40,INK,True)
            d.line((300,710,1620,710),fill=INK,width=4)
            text(d,'Total',960,750,44,INK,True)
            wrapped(d,'Add parts • Find a difference • Check the relationship',875,32)
        elif topic=='multiplication-division':
            division=section in ['lesson3','lesson4']
            if division:
                wrapped(d,'Equal groups: the whole is shared fairly.',320,44)
                for j in range(6):
                    x=230+j*250
                    d.rounded_rectangle((x,500,x+210,700),radius=20,fill=EMPTY,outline=TEAL,width=4)
                    text(d,'equal',x+105,565,32,INK,True)
                wrapped(d,'Number of groups × Amount in each group = Total',800,38)
            else:
                wrapped(d,'Four rows of eight: count equal groups.',320,44)
                for row in range(4):
                    for col in range(8):
                        x=580+col*105;y=500+row*82
                        d.ellipse((x,y,x+45,y+45),fill=TEAL if (row*8+col)<32*progress else EMPTY)
                text(d,'4 × 8 = 32',W/2,870,49,TEAL,True)
        elif topic=='factors-multiples':
            wrapped(d,'An array connects factors and their product.',320,44)
            for row in range(4):
                for col in range(6):
                    x=660+col*110;y=500+row*82
                    d.rectangle((x,y,x+62,y+52),fill=TEAL if row*6+col<24*progress else EMPTY)
            text(d,'4 × 6 = 24',W/2,865,49,TEAL,True)
        elif topic=='decimals-percentages':
            if section=='place':
                wrapped(d,'Place value continues to the right of the decimal point.',310,40)
                labels=['Ones','Tenths','Hundredths','Thousandths']
                for j,(label,digit) in enumerate(zip(labels,'4307')):
                    x=280+j*340
                    d.rounded_rectangle((x,500,x+320,740),radius=15,fill=EMPTY)
                    text(d,label,x+160,540,32,INK,True)
                    text(d,digit,x+160,635,62,TEAL,True)
                text(d,'4.307 = 4 ones + 3 tenths + 7 thousandths',W/2,850,39,TEAL,True)
            elif section=='compare':
                wrapped(d,'Compare positions, rather than counting written digits.',310,40)
                y=660; left=220; span=1480
                d.line((left,y,left+span,y),fill=INK,width=4)
                for j in range(11):
                    x=left+span*j/10
                    d.line((x,y-12,x,y+12),fill=INK,width=3)
                text(d,'0.5',left,y+40,35,INK,True)
                text(d,'0.7',left+span,y+40,35,INK,True)
                for j,v in enumerate([.599,.620]):
                    x=left+span*(v-.5)/.2
                    d.ellipse((x-9,y-9,x+9,y+9),fill=TEAL)
                    text(d,f'{v:.3f}',x,y-70-j*65,35,TEAL,True)
                text(d,'0.620 > 0.599',W/2,850,44,TEAL,True)
            else:
                wrapped(d,'One whole divided into one hundred equal parts.',305,42)
                for row in range(10):
                    for col in range(10):
                        x=730+col*46;y=425+row*46
                        d.rectangle((x,y,x+43,y+43),fill=TEAL if row*10+col<75*progress else EMPTY)
                text(d,'75 hundredths = 0.75 = 75%',W/2,920,37,TEAL,True)
    if board:
        size=min(52,200//max(1,len(board))+12)
        y=300 if not cue.get('equation') else 470
        for j,line in enumerate(board):
            line=mathematical_board(line)
            # Handle source fraction notation as structured numerator/bar/denominator.
            if re.search(r'\d+/\d+',line):
                parts=re.split(r'(\d+/\d+)',line)
                tokens=[list(map(int,p.split('/'))) if re.fullmatch(r'\d+/\d+',p) else p for p in parts if p.strip()]
                equation(d,tokens,y)
                y+=155
            else:
                text(d,line,W/2,y,size,TEAL if j==len(board)-1 and progress>.5 else INK,True)
                y+=size*1.55
        # Progressive underline guides attention through the current worked step.
        d.line((300,y+12,300+1320*progress,y+12),fill=TEAL,width=5)
    model=cue.get('model')
    if model and model['type']=='place':
        labels=model['labels']; digits=model['digits']; cw=1500/len(labels); y=700
        for i,(label,digit) in enumerate(zip(labels,digits)):
            x=210+i*cw
            d.rounded_rectangle((x,y,x+cw-8,y+150),radius=9,fill='#FFF0C8' if i==model['highlight'] else EMPTY)
            for k,line in enumerate(label.split('\n')): text(d,line,x+cw/2,y+12+k*26,23,INK,True,maxw=cw-12)
            text(d,digit,x+cw/2,y+86,45,TEAL,True)
    if model and model['type']=='array': draw_array(d,model,progress)
    if model and model['type']=='products': draw_products(d,model,progress)
    if model and model['type']=='groups': draw_groups(d,model,progress)
    if model and model['type']=='share': draw_share(d,model,progress)
    if model and model['type']=='family': draw_family(d,model,progress)
    if model and model['type']=='column': draw_column(d,model)
    if model and model['type']=='bar': draw_part_bar(d,model,progress)
    if model and model['type']=='line':
        y=740; start,end=model['start'],model['end']
        d.line((220,y,1700,y),fill=MUTED,width=4)
        for i in range(11):
            x=220+148*i; v=start+(end-start)*i/10
            d.line((x,y-12,x,y+12),fill=INK,width=3)
            if i in [0,10]: text(d,f'{v:.{model["decimals"]}f}',x,y+32,32,INK,True)
        if model.get('points') is not None:
            for value in model['points']:
                x=220+1480*(value-start)/(end-start);d.ellipse((x-10,y-10,x+10,y+10),fill=TEAL)
                text(d,f'{value:,}',x,y-62,36,TEAL,True)
            for a,b in model.get('jumps',[]):
                x1=220+1480*(a-start)/(end-start);x2=220+1480*(b-start)/(end-start);xe=x1+(x2-x1)*progress;direction=1 if b>a else -1
                d.line((x1,650,xe,650),fill=GOLD,width=6)
                if progress>.05:d.polygon([(xe,650),(xe-direction*14,640),(xe-direction*14,660)],fill=GOLD)
                text(d,('+' if b>a else '−')+f'{abs(b-a):,}',(x1+x2)/2,600,36,GOLD,True)
        elif model.get('mark') is not None:
            x=220+1480*(model['mark']-start)/(end-start)
            d.ellipse((x-10,y-10,x+10,y+10),fill=TEAL)
            text(d,str(model['mark']),x,y-62,36,TEAL,True)
    if cue.get('note'): wrapped(d,cue['note'],925,32)
    if cue.get('role')=='question': text(d,'Think time • 4 seconds',W/2,865,36,GOLD,True)
    d.line((90,1000,90+1740*cue.get('lesson_progress',0),1000),fill=TEAL,width=7)
    im.save(path)
