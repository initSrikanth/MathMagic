"""Build static strand navigation and human-readable audit from the persistent matrix.
Run after editing curriculum-coverage.json or strand-topics.json. No media/auth writes.
"""
from pathlib import Path
import html,json,sys
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'docs/year5'
e=html.escape
def write(path,text):
 if "--check" in sys.argv:
  assert path.exists() and path.read_text()==text, "Generated file is stale: "+str(path.relative_to(ROOT))
 else:path.write_text(text)
resources={
'whole-numbers':('Whole Numbers & Place Value','whole-numbers.html','123','Five learning pages and a 30-question challenge.'),
'fractions':('Fractions','fractions.html','½','Five learning pages and a 30-question challenge.'),
'decimals-percentages':('Decimals & Percentages','decimals-percentages.html','%','Five learning pages and a 30-question challenge.'),
'addition-subtraction':('Addition & Subtraction','addition-subtraction.html','＋−','Five learning pages and a 30-question challenge.'),
'multiplication-division':('Multiplication & Division','multiplication-division.html','×÷','Five learning pages and a 30-question challenge.'),
'factors-multiples':('Factors & Multiples','factors-multiples.html','×','Five learning pages and a 30-question challenge.'),
'measurement':('Measuring Our World','measurement.html','cm²','Five learning pages and a 30-question challenge.'),
 'time-angles':('Time and Angles','time-angles.html','90°','Five learning pages and a 30-question challenge.'),
'space':('Space and Geometry','space-lessons.html','◇','Ten lessons, five interactive tools and a 30-question challenge.'),
'statistics':('Data Detectives — Statistics','statistics.html','▥','Five lessons, five investigations and a 30-question challenge.')}
def progress_card(key):
 title,href,icon,summary=resources[key]
 reset=f'<button type="button" class="tiny-reset" data-reset-topic="{key}" title="Reset {e(title)} progress">Reset</button>' if key in ['whole-numbers','fractions'] else ''
 # Reset is outside the link: keyboard users never encounter nested controls.
 return f'''<article class="topic-practice"><a class="activity-card featured" href="{href}"><div class="activity-icon" aria-hidden="true">{icon}</div><div><span class="pill">YEAR 5</span><h3{' data-statistics-title' if key=='statistics' else ''}>{e(title)}</h3><p>{summary}</p><strong>Start learning →</strong></div></a><div class="progress-panel" data-topic-progress="{key}"><div class="progress-row"><span>Practice <b class="practice-dots">○ ○ ○ ○ ○</b></span><span data-attempts>0/5</span></div><div class="mini-progress"><i data-progress-bar style="width:0%"></i></div><div class="progress-row"><span data-best>Best: —</span>{reset}<span class="proficiency-badge" data-proficiency>START</span></div></div></article>'''
def shell(title,body):
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MathMagic | {e(title)}</title><link rel="stylesheet" href="css/style.css"><link rel="stylesheet" href="css/curriculum.css?v=1"></head>
<body class="protected-page curriculum-page"><a class="curriculum-skip" href="#learning">Skip to learning</a><header class="topbar"><a class="logo" href="dashboard.html">Math<span>Magic</span></a><div class="user-area"><img data-user-photo class="avatar" alt="Profile" hidden><div><strong data-user-name>Learner</strong><small data-user-email></small></div><button class="outline-button" data-logout>Log out</button></div></header>
{body}
<script type="module" src="js/auth-guard.js?v=6"></script><script type="module" src="js/measurement-dashboard.js?v=2"></script><script type="module" src="js/space-dashboard.js"></script><script src="js/statistics-config.js?v=1"></script><script type="module" src="js/statistics-dashboard.js?v=1"></script></body></html>'''
def count(rows):
 return f'{sum(r["status"]=="COMPLETE" for r in rows)} of {len(rows)} skills fully covered'
def strand_card(s,rows):
 return f'''<a class="strand-card strand-{s['id']}" href="year5-{s['id']}.html" data-strand="{s['id']}"><span class="strand-symbol" aria-hidden="true">{s['symbol']}</span><h3>{s['name']}</h3><p>{e(s['intro'])}</p><p class="curriculum-coverage">Lesson coverage: {count(rows)}</p><strong>{'See what is planned' if not s['topics'] else 'Explore '+s['name']} →</strong></a>'''
def context(href,strand):
 if strand!='algebra':return href
 file,sep,anchor=href.partition('#');return file+'?strand=algebra'+(sep+anchor if sep else '')
def build():
 matrix=json.loads((DATA/'curriculum-coverage.json').read_text());nav=json.loads((DATA/'strand-topics.json').read_text());rows=matrix['descriptors']
 buttons=''.join('<button type="button" '+('class="selected" aria-pressed="true" aria-label="Year 5, selected"' if y==5 else f'disabled aria-label="Year {y}, coming later"')+f'>{y}</button>' for y in range(1,11))
 cards=''.join(strand_card(s,[r for r in rows if r['strand']==s['name']]) for s in nav['strands'])
 grouped_practice=''.join('<h3 class="section-label">Year 5 • '+name+'</h3><div class="activity-grid compact-grid">'+''.join(progress_card(k) for k in keys)+'</div>' for name,keys in [('Number',list(resources)[:6]),('Measurement',['time-angles','measurement']),('Space',['space']),('Statistics',['statistics'])])
 body=f'''<main class="dashboard" id="learning" tabindex="-1"><section class="hero"><p class="eyebrow">YOUR LEARNING SPACE</p><h1>Hello, <span data-user-name>Learner</span>!</h1><p>Choose a strand, explore a topic and keep building your maths skills.</p></section><div class="year-strip"><strong>Choose year</strong><div aria-label="Year levels">{buttons}</div><small>Year 5 is open. Other year levels are coming later.</small></div><section aria-labelledby="strands-heading"><h2 id="strands-heading">Year 5 • Explore a strand</h2><p>Choose a strand to find its topics, lessons, activities and assessments.</p><div class="strand-grid">{cards}</div><p class="curriculum-note">Lesson coverage describes the learning we have built. Some skills need more learning resources. Your own practice and scores are shown separately below.</p></section><section class="practice-section" aria-labelledby="practice-heading"><h2 id="practice-heading">Your topic practice</h2><p>Continue an existing topic. Practice attempts and best scores belong to you; they do not change lesson coverage.</p>{grouped_practice}</section></main>'''
 write(ROOT/'dashboard.html',shell('Dashboard',body)+'\n')
 for s in nav['strands']:
  sr=[r for r in rows if r['strand']==s['name']];topics=[]
  for i,t in enumerate(s['topics']):
   lessons=''.join(f'<li><a href="{e(context(l["href"],s["id"]))}">{e(l["title"])}</a><a class="activity-link" href="{e(context(l["activity"],s["id"]))}">Try the activity<span class="sr-only"> for {e(l["title"])}</span></a></li>' for l in t['lessons'])
   assessment_name=e(resources[next(k for k,v in resources.items() if v[1]==t['page'])][0])
   if t['page']=='statistics.html':assessment_name='<span data-statistics-title>'+assessment_name+'</span>'
   topics.append(f'''<article class="curriculum-topic" id="topic-{i+1}"><h3{' data-statistics-title' if t['page']=='statistics.html' else ''}>{e(t['title'])}</h3><p>{e(t['description'])}</p><small>{'Existing lessons to explore • more learning planned' if t['planned'] else 'Existing learning resources'}</small><h4>Lessons and interactive activities</h4><ol>{lessons}</ol><h4>Assessment</h4><p>This topic uses the existing {assessment_name} challenge and practice record.</p><a class="assessment-link" href="{e(context(t['assessment'],s['id']))}">Open the 30-question challenge<span class="sr-only"> for {e(t['title'])}</span></a></article>''')
  if not topics:topics=['<article class="curriculum-topic"><h3>Chance Investigators — planned</h3><p>Explore possible outcomes, compare fair and uneven chances, repeat experiments and use frequencies to estimate likelihood.</p><p>Lessons, activities, assessment and videos are still to be built. There is no challenge or practice record yet.</p></article>']
  extra='<p>Extra exploration: <a href="space-lessons.html#lesson-9">Test shape-classification algorithms</a>. This supports reasoning and is separate from the three Space skills above.</p>' if s['id']=='space' else ''
  practice=f'<section class="practice-section" aria-labelledby="practice-heading"><h2 id="practice-heading">Your practice</h2><p>These are your existing topic records. Shared lessons and challenges use the same record wherever you open them.</p><div class="activity-grid compact-grid">{"".join(progress_card(k) for k in s["progress_topics"])}</div></section>' if s['progress_topics'] else '<section class="practice-section"><h2>Your practice</h2><p>Practice tracking will be available when this learning is ready.</p></section>'
  body=f'''<nav class="curriculum-nav" aria-label="Breadcrumb"><ol><li><a href="dashboard.html">Year 5</a></li><li aria-current="page">{s['name']}</li></ol></nav><main class="dashboard" id="learning" tabindex="-1"><header class="hero"><p class="eyebrow">YEAR 5</p><h1>{s['name']}</h1><p>{s['intro']}</p></header><p class="curriculum-note">Lesson coverage: <strong>{count(sr)}</strong>. This describes our learning resources, not your scores. {'More learning is planned for this strand.' if any(r['status']!='COMPLETE' for r in sr) else 'Your practice is shown separately below.'}</p><section aria-labelledby="topics-heading"><h2 id="topics-heading">Explore topics</h2><div class="topic-grid">{''.join(topics)}</div>{extra}</section>{practice}</main>'''
  write(ROOT/f'year5-{s["id"]}.html',shell('Year 5 '+s['name'],body)+'\n')
 # Human-readable matrix retains every required evidence column, not just totals.
 lines=['# Year 5 curriculum coverage — verified resource audit','', 'Audited 24 November 2026 against main `'+matrix['baseline_commit']+'`. [Machine-readable matrix](curriculum-coverage.json) is the source of truth. [Actual resource/served-byte inventory](resource-audit.json) and [development plan](strand-completion-plan.md) are separate records.','',matrix['attribution'],'','## Method and limits','']
 for k,v in matrix['status_definitions'].items():lines.append(f'- **{k}**: {v}')
 lines+=['','Coverage is independent of student progress, media approval and deployment. A COMPLETE descriptor does not certify a released strand. Practical building, measurement and open investigation performance require pupil/teacher observation. Source/transcript inspection and public byte verification do not constitute new full listening/viewing.','']
 for source in matrix['authoritative_sources']:lines.append(f'- [{source["purpose"]}]({source["url"]})')
 for note in matrix['source_notes']:lines.append('- '+note)
 lines+=['','## All 24 descriptors','', '| Strand | Code and exact description | Required knowledge and skills | Existing topic / lesson paths | Interactive activity | Assessment evidence | Video coverage / approval | Gaps and action | Development | Deployment |','|---|---|---|---|---|---|---|---|---|---|']
 def link(p):return f'[{p}](../../{p})'
 for r in rows:
  a=r['assessment'];v=r['video_coverage'];videos='<br>'.join(link(x['path'])+' — '+x['approval_status'] for x in v) or 'Missing'
  cells=[r['strand'],f"**{r['code']} — {r['status']}**<br>{r['description']}",'<br>'.join(r['required_knowledge_and_skills']),'<br>'.join(link(p) for p in r['lessons']) or 'None',link(r['interactive_activity']['path'])+'<br>'+r['interactive_activity']['detail'] if r['interactive_activity'] else 'Missing',link(a['path'])+' '+', '.join('`'+x+'`' for x in a['symbols'])+'<br>'+a['finding'] if a else 'Missing',videos,'<br>'.join(r['corrective_action']),r['development_status'],r['deployment_status']]
  lines.append('| '+' | '.join(x.replace('|','&#124;') for x in cells)+' |')
 lines+=['','## Achievement standard cross-check','', '| Achievement aspect | Descriptor evidence | Finding |','|---|---|---|']
 for r in rows:lines.append(f"| {r['achievement_standard_aspect']} | {r['code']} | {r['status']}: "+('Required source learning and assessment identified; release evidence remains separate.' if not r['gaps'] else ' '.join(r['gaps']))+' |')
 lines+=['','All achievement-standard aspects are mapped. Modelling/algorithm creation, inverse fact families, broad unknown-equation reasoning, angle assessment validity and all chance-experiment aspects remain open. No achievement-standard completion or individual mastery is inferred from the number of topic cards.','']
 write(DATA/'curriculum-coverage.md','\n'.join(lines))
if __name__=='__main__':build()
