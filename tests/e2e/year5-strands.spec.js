const {test,expect}=require('@playwright/test');
const {mockFirebase}=require('./helpers/curriculum-firebase');
const matrix=require('../../docs/year5/curriculum-coverage.json'),navigation=require('../../docs/year5/strand-topics.json');
const strands=navigation.strands.map(s=>s.id);
const seed={};for(const topic of ['whole-numbers','fractions','decimals-percentages','addition-subtraction','multiplication-division','factors-multiples','measurement','time-angles','space','statistics'])seed['progress/curriculum_student/topics/'+topic]={attempts:2,bestScore:23,lastScore:21,proficient:false,completedLessons:[1]};

for(const strand of navigation.strands)test(`Year 5 ${strand.name}: hierarchy, coverage and responsive keyboard navigation`,async({page},info)=>{
 if(strand.id==='statistics')await page.addInitScript(()=>{window.StatisticsConfig={title:'Evidence Explorers'};});
 await mockFirebase(page,{seed});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/dashboard.html');await expect(page.locator('body')).toHaveClass(/authenticated/);
 const card=page.locator(`[data-strand="${strand.id}"]`);await card.focus();await page.keyboard.press('Enter');
 await expect(page).toHaveURL(new RegExp('/year5-'+strand.id+'\\.html$'));await expect(page.locator('h1')).toHaveText(strand.name);
 await expect(page.getByRole('navigation',{name:'Breadcrumb'})).toContainText('Year 5');
 const rows=matrix.descriptors.filter(r=>r.strand===strand.name);await expect(page.locator('.curriculum-note')).toContainText(`${rows.filter(r=>r.status==='COMPLETE').length} of ${rows.length} skills fully covered`);
 await expect(page.locator('.curriculum-topic')).toHaveCount(Math.max(1,strand.topics.length));
 if(strand.id==='statistics')for(const title of await page.locator('[data-statistics-title]').all())await expect(title).toHaveText('Evidence Explorers');
 for(const width of [390,768,1280]){
  await page.setViewportSize({width,height:900});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  for(const link of await page.locator('.curriculum-topic a').all()){const b=await link.boundingBox();expect(b.width).toBeGreaterThan(1);expect(b.x+b.width).toBeLessThanOrEqual(width+1);}
 }
 for(const topic of strand.progress_topics){const p=page.locator(`[data-topic-progress="${topic}"]`);await expect(p.locator('[data-attempts]')).toHaveText('2/5');await expect(p.locator('[data-best]')).toHaveText('Best: 23/30');}
 if(!strand.topics.length){await expect(page.locator('.curriculum-topic')).toContainText('still to be built');await expect(page.locator('.curriculum-topic a')).toHaveCount(0);}
 await page.getByRole('link',{name:'Year 5',exact:true}).focus();expect(await page.getByRole('link',{name:'Year 5',exact:true}).evaluate(a=>getComputedStyle(a).outlineStyle)).toBe('solid');
 await page.keyboard.press('Enter');await expect(page).toHaveURL(/dashboard\.html$/);
 await expect(page.locator('.strand-card')).toHaveCount(6);await expect(page.locator('.year-strip button')).toHaveCount(10);
 await expect(page.getByRole('button',{name:'Year 6, coming later'})).toBeDisabled();
 expect(errors).toEqual([]);
 if(strand.id==='number'&&info.project.name==='desktop-chromium'){
  await page.setViewportSize({width:1280,height:1000});await page.screenshot({path:info.outputPath('dashboard-desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:info.outputPath('dashboard-390.png'),fullPage:true});
 }
});

test('All seven dashboard/strand routes fail closed for signed-out, unapproved and failed approval reads (mock SDK)',async({browser})=>{
 for(const options of [{uid:null},{approved:false},{fail:true}]){
  const context=await browser.newContext();const page=await context.newPage();await mockFirebase(page,options);
  for(const path of ['dashboard',...strands.map(s=>'year5-'+s)]){
   await page.goto('/'+path+'.html');await expect(page).toHaveURL(options.uid===null?/index\.html$/:options.fail?/access-required\.html\?error=1$/:/access-required\.html$/);
   expect(await page.evaluate(()=>window.__curriculumMock.writes)).toEqual([]);
  }
  await context.close();
 }
});

test('Progress restores through dashboard and strand pages; reset stays UID/topic scoped (mock SDK)',async({page})=>{
 await mockFirebase(page,{seed});await page.goto('/year5-number.html');await expect(page.locator('body')).toHaveClass(/authenticated/);
 const whole=page.locator('[data-topic-progress="whole-numbers"]');await expect(whole.locator('[data-best]')).toHaveText('Best: 23/30');
 await page.reload();await expect(whole.locator('[data-attempts]')).toHaveText('2/5');
 page.once('dialog',d=>d.accept());await whole.getByRole('button',{name:'Reset',exact:true}).click();await expect(whole.locator('[data-attempts]')).toHaveText('0/5');
 await expect(page.locator('[data-topic-progress="fractions"] [data-attempts]')).toHaveText('2/5');
 await page.getByRole('link',{name:'Year 5',exact:true}).click();await expect(page.locator('[data-topic-progress="whole-numbers"] [data-attempts]')).toHaveText('0/5');
 await expect(page.locator('[data-topic-progress="statistics"] [data-attempts]')).toHaveText('2/5');
 expect(await page.evaluate(()=>window.__curriculumMock.writes)).toEqual([]); // Fresh page restores the persisted mock document; no migration writes.
 const stored=await page.evaluate(()=>window.__curriculumMock.saved);expect(stored['progress/curriculum_student/topics/whole-numbers'].attempts).toBe(0);expect(stored['progress/curriculum_student/topics/fractions']).toEqual(seed['progress/curriculum_student/topics/fractions']);
 await page.getByRole('button',{name:'Log out',exact:true}).click();await expect(page).toHaveURL(/index\.html$/);
});

test('Strand links open the actual lesson/activity/assessment panels across existing topics',async({page})=>{
 // Navigation is isolated from MP4 downloads; existing media suites retain real playback checks.
 await page.route('**/*.mp4',route=>route.abort());
 await mockFirebase(page,{seed});
 for(const strand of navigation.strands)for(const topic of strand.topics){
  const lesson=topic.lessons[topic.lessons.length-1];await page.goto('/'+lesson.href);
  // Algebra's contextual breadcrumb is carried by the actual landing-page link.
  await expect(page.locator('#'+lesson.href.split('#')[1])).toHaveClass(/active/);
  await expect(page.getByRole('navigation',{name:'Curriculum breadcrumb'})).toBeVisible();
  if(!lesson.activity.startsWith('space-')){
   await page.goto('/'+lesson.activity);await expect(page.locator('#'+lesson.href.split('#')[1])).toHaveClass(/active/);
   expect(await page.locator('#'+lesson.href.split('#')[1]).evaluate(s=>s.contains(document.activeElement))).toBe(true);
  }
  await page.goto('/'+topic.assessment);
  if(topic.assessment==='space-challenge.html')await expect(page.locator('#startBtn')).toBeVisible();
  else await expect(page.locator('#challenge')).toHaveClass(/active/);
 }
 await page.goto('/year5-algebra.html');await page.locator('.curriculum-topic ol a').first().click();await expect(page).toHaveURL(/multiplication-division\.html\?strand=algebra#lesson3$/);await expect(page.getByRole('navigation',{name:'Curriculum breadcrumb'})).toContainText('Algebra');
 // The real protected adapter must continue to fail closed on an unavailable callable.
 await page.goto('/multiplication-division.html#challenge');await expect(page.locator('#challenge')).toHaveClass(/active/);await expect(page.locator('#qPrompt')).not.toContainText('Calculate exactly.');
});
