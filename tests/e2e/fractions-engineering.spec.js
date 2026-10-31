const {test,expect}=require('@playwright/test');
async function open(page){
 // Isolate Firebase in CI. These are UI tests, not real authorisation/storage proof.
 await page.route('**/js/fractions-auth.js*',route=>route.abort());
 await page.goto('/fractions.html');await page.evaluate(()=>document.body.classList.remove('auth-loading'));
}
test('worked mixed-number and subtraction models stay readable and contained',async({page},testInfo)=>{
 await open(page);
 for(const width of [390,768,1280]){
  await page.setViewportSize({width,height:900});await page.locator('[data-screen="mixed"]').click();
  const line=page.locator('.mixed-number-line-svg');await expect(line).toBeVisible();await expect(line).toHaveAttribute('role','img');
  await expect(line.locator('g').first().locator('path')).toHaveCount(13);
  await expect(line.locator('desc')).toContainText('Twelve equal quarter-steps');await line.screenshot({path:testInfo.outputPath(`mixed-line-${width}.png`)});
  const box=await line.boundingBox();expect(box.width).toBeGreaterThan(200);expect(box.x+box.width).toBeLessThanOrEqual(width);
  await expect(page.locator('#mixed')).not.toContainText(/\b\d+\/\d+\b/);
  await page.locator('[data-screen="addsub"]').click();await expect(page.locator('.subtraction-worked-strip .remaining')).toHaveCount(5);await expect(page.locator('.subtraction-worked-strip .removed')).toHaveCount(1);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
 }
});
test('navigation pauses hidden media, announces current page and practice uses correct feedback',async({page})=>{
 await open(page);await page.evaluate(()=>{window.pauseCalls=0;HTMLMediaElement.prototype.pause=function(){window.pauseCalls++}});
 await page.locator('[data-screen="equivalent"]').click();expect(await page.evaluate(()=>window.pauseCalls)).toBeGreaterThan(0);
 await expect(page.locator('[data-screen="equivalent"]')).toHaveAttribute('aria-current','step');
 await expect(page.locator('#equivalent h2')).toBeFocused();await page.locator('#equivalent [data-practice]').click();
 const feedback=page.locator('#equivalent .practice-feedback');await expect(feedback).toHaveClass(/correct/);await expect(feedback).toHaveCSS('color','rgb(24, 121, 78)');
 await page.locator('[data-screen="challenge"]').click();
 await page.evaluate(()=>{quiz=[numberLine()];index=0;render()});
 const coords=await page.locator('#qDisplay .number-line').evaluate(line=>{const axis=line.querySelector('.nl-axis').getBoundingClientRect(),ticks=[...line.querySelectorAll('.nl-tick')].map(x=>x.getBoundingClientRect());return {axisStart:axis.x,axisEnd:axis.right,start:ticks[0].x+ticks[0].width/2,end:ticks.at(-1).x+ticks.at(-1).width/2,ghost:getComputedStyle(line,'::before').content}});
 expect(Math.abs(coords.axisStart-coords.start)).toBeLessThan(1);expect(Math.abs(coords.axisEnd-coords.end)).toBeLessThan(1);expect(coords.ghost).toBe('none');
});
test('full challenge failure can retry the same attempt and start a new challenge',async({page})=>{
 await open(page);await page.evaluate(()=>{window.savedCalls=[];window.MathMagicFractionsProgress={async saveAttempt(score,id){window.savedCalls.push({score,id});if(window.savedCalls.length===1)throw Error('temporary network failure');return{attempts:1,bestScore:score,proficient:score===30}}}});
 await page.locator('[data-screen="challenge"]').click();
 for(let i=0;i<30;i++){
  await expect(page.locator('#qNumber')).toHaveText(`${i+1} / 30`);
  const choices=page.locator('#qAnswer [data-choice-index]');
  if(await choices.count())await choices.first().click();
  else{for(const input of await page.locator('#qAnswer input').all()){const id=await input.getAttribute('id');await input.fill(id==='den'?'997':id==='num'?'1':'999')}await page.locator('#checkAnswer').click()}
  await expect(page.locator('#nextQuestion')).toBeEnabled();await page.locator('#nextQuestion').click();
 }
 await expect(page.locator('#resultCard')).toBeVisible();await expect(page.locator('#saveStatus')).toContainText('could not be recorded');await expect(page.locator('#retrySave')).toBeVisible();await expect(page.locator('#saveStatus')).toHaveCSS('color','rgb(180, 35, 24)');await expect(page.locator('#newChallenge')).toBeVisible();
 await page.locator('#retrySave').click();await expect(page.locator('#saveStatus')).toContainText('Attempt recorded');await expect(page.locator('#retrySave')).toBeHidden();
 const calls=await page.evaluate(()=>window.savedCalls);expect(calls).toHaveLength(2);expect(calls[0].id).toBe(calls[1].id);expect(calls[0].score).toBe(calls[1].score);
 await page.locator('#newChallenge').click();await expect(page.locator('#qNumber')).toHaveText('1 / 30');await expect(page.locator('.quiz-card')).toBeVisible();await expect(page.locator('#resultCard')).toBeHidden();
});
