"""Reusable vector animations; no LaTeX dependency and no raster slide deck."""
import json
import os
from pathlib import Path
import numpy as np
from manim import *

BG='#0D172B'; INK='#F5F7FC'; MUTED='#ACBAD1'; TEAL='#35DCC2'; GOLD='#FFD166'
BLUE='#71AFFF'; PANEL='#152641'; EMPTY='#243B57'
FONT='Open Sans'
config.background_color=BG

def txt(s, size=32, colour=INK):
    return Text(str(s),font=FONT,font_size=size,color=colour,disable_ligatures=True)

def fit(m,w):
    if m.width>w: m.scale_to_fit_width(w)
    return m

def frac(n,d, colour=INK):
    top=txt(n,38,colour); bottom=txt(d,38,colour)
    width=max(top.width,bottom.width,.38)+.15
    bar=Line(LEFT*width/2,RIGHT*width/2,color=colour,stroke_width=3)
    top.next_to(bar,UP,buff=.10); bottom.next_to(bar,DOWN,buff=.10)
    return VGroup(top,bar,bottom)

def token(t):
    if isinstance(t,list):
        if len(t)==2: return frac(*t)
        return VGroup(txt(t[0],46),frac(*t[1:])).arrange(RIGHT,buff=.18)
    return txt(t,42, GOLD if t in ['>','<','=','≠'] else INK)

def equation(tokens):
    g=VGroup(*(token(t) for t in tokens)).arrange(RIGHT,buff=.27)
    return fit(g,12.1).move_to([0,1.85,0])

def strip(r, y):
    n,d=r['n'],r['d']; c=TEAL if r['colour']=='teal' else GOLD
    cells=VGroup()
    width=8.7; h=.46
    wholes=max(1,int(np.ceil(n/d))); count=wholes*d
    for i in range(count):
        cell=Rectangle(width=width/count,height=h,stroke_color=BG,stroke_width=2,
                       fill_color=c if i<n else EMPTY,fill_opacity=1)
        cell.move_to([-width/2+(i+.5)*width/count,y,0]); cells.add(cell)
    outline=Rectangle(width=width,height=h,stroke_color=MUTED,stroke_width=1).move_to([0,y,0])
    for unit in range(1,wholes):
        x=-width/2+width*unit/wholes
        outline.add(Line([x,y-h/2,0],[x,y+h/2,0],color=INK,stroke_width=4))
    label=fit(txt(r['label'],25,MUTED),8.7).next_to(outline,UP,buff=.13)
    value=frac(n,d,c).scale(.64).next_to(outline,RIGHT,buff=.35)
    return VGroup(cells,outline,label,value)

def number_line(l):
    d=l['d']; maximum=l['maximum']; total=d*maximum
    left=-5.55; width=11.1; y=-.55
    axis=Line([left,y,0],[left+width,y,0],color=MUTED,stroke_width=3)
    ticks=VGroup(); labels=VGroup()
    for i in range(total+1):
        x=left+width*i/total
        ticks.add(Line([x,y-.12,0],[x,y+.12,0],color=MUTED,stroke_width=2))
        if i%d==0: labels.add(txt(i//d,27).move_to([x,y-.42,0]))
        elif total<=8: labels.add(frac(i,d,MUTED).scale(.47).move_to([x,y-.61,0]))
    points=VGroup()
    for k,p in enumerate(l['points']):
        x=left+width*p/total; c=TEAL if k%2==0 else GOLD
        dot=Dot([x,y,0],radius=.085,color=c)
        label=frac(p,d,c).scale(.72).move_to([x,y+.84+(k%2)*.0,0])
        points.add(VGroup(dot,label))
    return VGroup(axis,ticks,labels,points)

def area_model(n,d):
    # Equal area, equal angles, same whole for every partition.
    sectors=VGroup()
    for i in range(d):
        sector=Sector(radius=1.17,start_angle=PI/2+i*TAU/d,angle=TAU/d,
                      fill_color=TEAL if i<n else EMPTY,fill_opacity=1,
                      stroke_color=BG,stroke_width=5)
        sector.shift(DOWN*.5); sectors.add(sector)
    return sectors

class FractionFilm(Scene):
    def construct(self):
        timeline=json.loads(Path(os.environ['MM_TIMELINE']).read_text())
        lesson=timeline['lesson']; cues=timeline['cues']
        # Consistent permanent frame, with ample margins for native player controls.
        brand=txt('MathMagic',22,TEAL).to_corner(UL,buff=.34)
        lesson_title=fit(txt(lesson['title'],22,MUTED),9).to_corner(UR,buff=.34)
        rule=Line([-6.65,3.29,0],[6.65,3.29,0],color=EMPTY,stroke_width=2)
        self.add(brand,lesson_title,rule)
        progress_bg=Line([-6.65,-3.68,0],[6.65,-3.68,0],color=EMPTY,stroke_width=4)
        self.add(progress_bg)
        current={}; progress=None
        for i,cue in enumerate(cues):
            target={}
            target['chapter']=fit(txt(cue['chapter'],35),12.5).move_to([0,2.83,0])
            if cue['equation']: target['equation']=equation(cue['equation'])
            rows=cue['rows']
            if rows:
                ys={1:[-.15],2:[.1,-1.25],3:[.55,-.55,-1.65]}[len(rows)]
                target['model']=VGroup(*(strip(r,y) for r,y in zip(rows,ys)))
            if cue['line']: target['model']=number_line(cue['line'])
            if cue['area']: target['model']=area_model(*cue['area'])
            if cue['context']:
                # Small context tag rather than decorative clutter over the maths.
                label=txt(cue['context'],18,GOLD)
                box=RoundedRectangle(width=label.width+.36,height=.4,corner_radius=.1,
                                     stroke_color=GOLD,stroke_width=1).move_to(label)
                target['context']=VGroup(box,label).move_to([-4.7,-2.46,0])
            target['note']=fit(txt(cue['note'],25,MUTED),12.0).move_to([0,-3.08,0])
            step=txt(f'{cue["index"]+1:02}  •  {len(lesson["beats"]):02}',17,MUTED).move_to([5.94,-3.42,0])
            target['step']=step
            animations=[]
            for key,old in list(current.items()):
                if key not in target:
                    animations.append(FadeOut(old,shift=UP*.1)); del current[key]
            for key,new in target.items():
                if key in current:
                    if key=='model' and rows and isinstance(current[key],VGroup):
                        animations.append(ReplacementTransform(current[key],new))
                    else: animations.append(ReplacementTransform(current[key],new))
                else:
                    if key=='model' and rows:
                        animations.append(LaggedStart(*(FadeIn(r,shift=RIGHT*.14) for r in new),lag_ratio=.15))
                    else: animations.append(FadeIn(new,shift=UP*.09))
            # Frame-quantised *absolute* audio boundaries avoid accumulated drift.
            end=round(cue['end']*30)/30-timeline.get('offset',0)
            budget=end-self.time
            intro=min(.7,budget*.18)
            self.play(*animations,run_time=intro)
            current=target
            # Reveal/shade cells in a travelling highlight, or trace the distance.
            movement=[]
            if rows:
                for model,r in zip(current['model'],rows):
                    if r['n']:
                        movement.append(Indicate(VGroup(*list(model[0])[:r['n']]),color=GOLD,scale_factor=1.025))
            elif cue['area']:
                movement.append(LaggedStart(*(Indicate(s,color=GOLD,scale_factor=1.02) for s in current['model']),lag_ratio=.15))
            elif cue['line']:
                l=cue['line']; a,b=l.get('jump') or [0,l['points'][-1] if l['points'] else l['d']]
                x=lambda p: -5.55+11.1*p/(l['maximum']*l['d'])
                path=ArcBetweenPoints([x(a),-.55,0],[x(b),-.55,0],angle=-PI/3 if b>a else PI/3,color=GOLD)
                self.play(Create(path),run_time=min(1.8,budget*.22))
                current['path']=path
            if movement:
                self.play(*movement,run_time=min(1.4,budget*.2))
            if cue['equation']:
                eq=current['equation']
                # A restrained moving underline guides attention through the equation.
                underline=Line(eq.get_left()+DOWN*.66,eq.get_right()+DOWN*.66,color=TEAL,stroke_width=2)
                self.play(Create(underline),run_time=min(1.0,budget*.14))
                current['underline']=underline
            new_progress=Line([-6.65,-3.68,0],[-6.65+13.3*(cue['index']+1)/len(lesson['beats']),-3.68,0],color=TEAL,stroke_width=4)
            if progress is None: self.add(new_progress)
            else: self.remove(progress); self.add(new_progress)
            progress=new_progress
            remaining=end-self.time
            if remaining>1/30: self.wait(remaining,frozen_frame=True)
