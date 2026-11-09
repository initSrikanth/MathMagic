const {test,expect}=require('@playwright/test');

// Presentation/interaction tests isolate the existing Firebase module. They do not verify live access.
test.beforeEach(async({page})=>{
 await page.route('**/js/space-auth.js',r=>r.fulfill({contentType:'application/javascript',body:"document.body.classList.remove('auth-loading');"}));
});

test('Space course: ten numbered tabs, a separate assessment and keyboard selection',async({page})=>{
 await page.goto('/space-lessons.html');
 const tabs=page.getByRole('tab');
 await expect(tabs).toHaveCount(10);
 await expect(page.locator('section.lesson:visible')).toHaveCount(1);
 await expect(page.locator('.challenge-tab')).toHaveAttribute('href','space-challenge.html');
 for(let i=0;i<10;i++){
  await expect(tabs.nth(i)).toHaveAttribute('aria-controls','lesson-'+(i+1));
  await expect(tabs.nth(i).locator('span')).not.toBeEmpty();
 }
 await tabs.first().focus();
 await page.keyboard.press('ArrowRight');
 await expect(tabs.nth(1)).toBeFocused();
 await expect(tabs.nth(1)).toHaveAttribute('aria-selected','true');
 await expect(page.locator('#lesson-2')).toBeVisible();
 await expect(page.locator('#lesson-1')).toBeHidden();
 await page.keyboard.press('End');
 await expect(tabs.last()).toBeFocused();
 await expect(page.locator('#lesson-10')).toBeVisible();
 await page.keyboard.press('ArrowRight');
 await expect(tabs.first()).toBeFocused();
 await page.keyboard.press('ArrowLeft');
 await expect(tabs.last()).toBeFocused();
 await page.keyboard.press('Home');
 await expect(tabs.first()).toBeFocused();
 expect(await tabs.first().evaluate(el=>getComputedStyle(el).outlineStyle)).toBe('solid');
 await page.keyboard.press('Tab');
 await expect(page.locator('.challenge-tab')).toBeFocused();
});

test('Space course: deep links, history, next/previous and hidden-media pause preserve position',async({page})=>{
 await page.goto('/space-lessons.html#lesson-8');
 await expect(page.locator('#lesson-8')).toBeVisible();
 await expect(page.locator('[data-screen="lesson-8"]')).toHaveAttribute('aria-selected','true');
 const selected=await page.locator('[data-screen="lesson-8"]').boundingBox();
 expect(selected.x).toBeGreaterThanOrEqual(0);
 expect(selected.x+selected.width).toBeLessThanOrEqual(page.viewportSize().width);
 const video=page.locator('#lesson-8 video');
 await video.evaluate(v=>{v.__coursePaused=0;v.pause=()=>v.__coursePaused++;});
 await page.locator('#lesson-8 [data-lesson-next="lesson-9"]').click();
 await expect(page.locator('#lesson-9 h2')).toBeFocused();
 await expect(page).toHaveURL(/#lesson-9$/);
 expect(await video.evaluate(v=>v.__coursePaused)).toBeGreaterThan(0);
 await page.goBack();
 await expect(page.locator('#lesson-8')).toBeVisible();
 await page.locator('[data-screen="lesson-10"]').click();
 await expect(page.locator('section.lesson:visible')).toHaveCount(1);
 await expect(page.locator('#lesson-10 .lesson-nav .primary')).toHaveAttribute('href','space-challenge.html');
 await page.locator('#lesson-10 [data-lesson-next="lesson-9"]').click();
 await expect(page.locator('#lesson-9')).toBeVisible();
 await page.evaluate(()=>location.hash='lesson-4');
 await expect(page.locator('#lesson-4')).toBeVisible();
});

for(const width of [390,768,1440])test('Space shared layout: no overflow or overlapping navigation at '+width+'px',async({page})=>{
 await page.setViewportSize({width,height:1000});
 for(const file of ['space-lessons.html','space-challenge.html','space-coordinates.html','space-lab.html','space-symmetry.html','space-net-explorer.html','space-classification.html']){
  await page.goto('/'+file);
  await expect(page.locator('.mathmagic-nav')).toBeVisible();
  await expect(page.locator('.course-shell .course-header h1')).toBeVisible();
  await expect(page.locator('link[href^="css/addition-subtraction.css"]')).toHaveCount(1);
  expect(await page.locator('.course-header').evaluate(el=>getComputedStyle(el).backgroundImage)).toContain('linear-gradient');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),file).toBe(true);
  for(const control of await page.locator('.space-lesson-navigation .tab,.space-tool-nav a').all()){
   const box=await control.boundingBox();
   expect(box.height,file).toBeGreaterThanOrEqual(44);
   expect(box.width,file).toBeGreaterThanOrEqual(44);
  }
  const tabs=page.locator('.lesson-tabs .tab');
  if(await tabs.count()){
   const boxes=await tabs.evaluateAll(elements=>elements.map(e=>{const b=e.getBoundingClientRect();return{x:b.x,y:b.y,right:b.right,bottom:b.bottom}}));
   for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){
    const a=boxes[i],b=boxes[j];expect(a.right<=b.x||b.right<=a.x||a.bottom<=b.y||b.bottom<=a.y,'tabs overlap in '+file).toBe(true);
   }
  }
  if(file==='space-lessons.html'){
   // All ten panels inherit the same cards and media containment, including the last tab on touch screens.
   for(let n=1;n<=10;n++){
    const tab=page.locator('[data-screen="lesson-'+n+'"]');
    await tab.click();
    const lesson=page.locator('#lesson-'+n);
    await expect(lesson).toBeVisible();
    await expect(lesson.locator('.rule-card').first().locator('ol li')).toHaveCount(3);
    await expect(lesson.locator('.worked.example-card')).toHaveCount(2);
    await expect(lesson.locator('video')).toBeVisible();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
   }
  }
 }
});
