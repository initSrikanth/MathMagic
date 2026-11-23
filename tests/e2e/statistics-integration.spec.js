// Exercise production integration after approval; retain the preview before it.
// Firebase modules are mocked at the network boundary; no production bypass exists.
const {test,expect}=require('@playwright/test');
const state=require('../../video-agent/statistics/checkpoint.json');
async function open(page){
 await page.route('**/js/statistics-auth.js*',r=>r.abort());
 await page.addInitScript(()=>{window.MathMagicStatisticsProgress={saveLesson:async()=>({}),getPendingAttempt:()=>null};});
 await page.goto(state.integrated===5?'/statistics.html':'/video-agent/statistics/review/integration-preview.html');
 await page.evaluate(()=>document.body.classList.remove('auth-loading'));
}
for(let i=1;i<=5;i++)test(`integrated lesson ${i}: accessible playback and below-picture captions`,async({page},info)=>{
 await open(page);await page.locator(`[data-screen="lesson${i}"]`).click();
 const card=page.locator(`#lesson${i} .statistics-player`),video=card.locator('video'),toggle=card.locator('[data-caption-toggle]'),panel=card.locator('.statistics-caption-panel');
 await expect(video).toHaveAccessibleName(/\S/);await expect(video).toHaveAttribute('playsinline','');await expect(video).toHaveAttribute('controls','');
 await expect.poll(()=>video.evaluate(v=>v.readyState)).toBeGreaterThanOrEqual(2);
 expect(await video.evaluate(v=>[v.videoWidth,v.videoHeight])).toEqual([1920,1080]);
 await toggle.focus();await page.keyboard.press('Enter');await expect(toggle).toHaveAttribute('aria-pressed','true');await expect(panel).toBeVisible();
 await expect.poll(()=>video.evaluate(v=>v.textTracks[0].cues?.length||0)).toBeGreaterThan(0);
 await video.evaluate(v=>{v.currentTime=30;v.pause()});await expect.poll(()=>video.evaluate(v=>!v.seeking)).toBe(true);
 await expect.poll(()=>panel.locator('p').textContent()).not.toBe('Captions appear here during speech.');
 expect(await video.evaluate(v=>v.textTracks[0].mode)).toBe('hidden');
 if(i===1&&info.project.name==='desktop-chromium'){
  await video.evaluate(v=>v.requestFullscreen());await expect.poll(()=>video.evaluate(v=>document.fullscreenElement===v)).toBe(true);
  await expect(panel).toBeHidden();expect(await video.evaluate(v=>v.textTracks[0].mode)).toBe('showing');
  await page.evaluate(()=>document.exitFullscreen());await expect(panel).toBeVisible();expect(await video.evaluate(v=>v.textTracks[0].mode)).toBe('hidden');
 }
 for(const width of[390,768,1280]){
  await page.setViewportSize({width,height:900});await expect.poll(()=>video.evaluate(v=>Math.abs(v.clientHeight-v.clientWidth*9/16-72))).toBeLessThanOrEqual(2);
  await video.scrollIntoViewIfNeeded();const v=await video.boundingBox(),c=await panel.boundingBox();
  expect(c.y).toBeGreaterThanOrEqual(v.y+v.height);expect(v.x+v.width).toBeLessThanOrEqual(width+1);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  expect(await panel.evaluate(p=>parseFloat(getComputedStyle(p).fontSize))).toBeGreaterThanOrEqual(18);
  await video.focus();await expect(video).toBeFocused();
 }
 await page.setViewportSize({width:390,height:844});await card.screenshot({path:info.outputPath(`lesson${i}-caption-layout-390.png`)});
 const playback=card.getByRole('button',{name:'Play video',exact:true});await playback.focus();await page.keyboard.press('Enter');await expect.poll(()=>video.evaluate(v=>!v.paused)).toBe(true);await expect.poll(()=>video.evaluate(v=>v.currentTime)).toBeGreaterThan(30.2);
 await expect(card.getByRole('button',{name:'Pause video',exact:true})).toBeFocused();await page.keyboard.press('Space');await expect.poll(()=>video.evaluate(v=>v.paused)).toBe(true);
 await page.keyboard.press('Enter');await expect.poll(()=>video.evaluate(v=>!v.paused)).toBe(true);
 await page.locator(`[data-screen="lesson${i===5?1:i+1}"]`).click();await expect.poll(()=>video.evaluate(v=>v.paused)).toBe(true);
 await page.locator(`[data-screen="lesson${i}"]`).click();await toggle.click();await expect(panel).toBeHidden();expect(await video.evaluate(v=>v.textTracks[0].mode)).toBe('disabled');
 await card.locator('summary').click();await expect(card.locator('details')).toContainText('Today we are learning');
 for(const key of['captions','transcript','poster'])expect((await page.request.get('/'+state.lessons[i-1][key])).ok()).toBe(true);
});

async function mockFirebase(page,{user='release_student',approved=true,fail=false}={}){
 await page.addInitScript(({user,approved,fail})=>{
  const saved=JSON.parse(localStorage.getItem('TEST_ONLY_firestore')||'{}');saved['access/'+user]={approved};
  window.__firebaseMock={user,fail,saved,queue:Promise.resolve(),commit(){localStorage.setItem('TEST_ONLY_firestore',JSON.stringify(this.saved))}};
 },{user,approved,fail});
 await page.route('https://www.gstatic.com/firebasejs/**/firebase-app.js',r=>r.fulfill({contentType:'text/javascript',body:'export const initializeApp=()=>({});'}));
 await page.route('https://www.gstatic.com/firebasejs/**/firebase-auth.js',r=>r.fulfill({contentType:'text/javascript',body:`const m=window.__firebaseMock;const auth={currentUser:m.user?{uid:m.user}:null};export const getAuth=()=>auth;export const onAuthStateChanged=(_,fn)=>{m.listener=fn;queueMicrotask(()=>fn(auth.currentUser))};export const signOut=async()=>{auth.currentUser=null;await m.listener(null)};`}));
 await page.route('https://www.gstatic.com/firebasejs/**/firebase-firestore.js',r=>r.fulfill({contentType:'text/javascript',body:`const m=window.__firebaseMock;export const getFirestore=()=>({});export const doc=(_, ...p)=>p.join('/');export const getDoc=async p=>{if(m.fail)throw Error('TEST read failure');return{exists:()=>p in m.saved,data:()=>structuredClone(m.saved[p])}};export const runTransaction=(_,fn)=>{const job=m.queue.then(async()=>{const edits=[];const result=await fn({get:getDoc,set:(p,d)=>edits.push([p,structuredClone(d)])});for(const[p,d]of edits)m.saved[p]=d;m.commit();return result});m.queue=job.catch(()=>{});return job};`}));
}
test('actual auth adapter: approved save, idempotence and fresh-page restore (mock SDK)',async({page})=>{
 await mockFirebase(page);await page.goto('/statistics.html');await expect(page.locator('body')).not.toHaveClass(/auth-loading/);
 await page.locator('#reflection1').fill('I checked each response and used the evidence.');await page.locator('#lesson1 [data-complete]').click();await expect(page.locator('#completeStatus1')).toContainText('recorded');
 await page.evaluate(async()=>{const a=window.MathMagicStatisticsProgress;await a.saveAttempt(30,'browser_attempt_001');await a.saveAttempt(30,'browser_attempt_001')});
 await expect(page.locator('#bestText')).toHaveText('Best: 30/30');await page.reload();await expect(page.locator('body')).not.toHaveClass(/auth-loading/);
 await expect(page.locator('#attemptText')).toHaveText('1 of 5 completed');await expect(page.locator('#bestText')).toHaveText('Best: 30/30');
 expect(await page.evaluate(()=>window.__firebaseMock.saved['progress/release_student/topics/statistics'].completedLessons)).toEqual([1]);
 await page.locator('#logoutBtn').click();await expect(page).toHaveURL(/index\.html$/);
});
for(const [name,options,url]of[['signed out',{user:null},/index\.html$/],['unapproved',{approved:false},/access-required\.html$/],['read failure',{fail:true},/access-required\.html\?error=1$/]])test(`actual auth adapter fails closed: ${name} (mock SDK)`,async({page})=>{
 await mockFirebase(page,options);await page.goto('/statistics.html');await expect(page).toHaveURL(url);
 expect(await page.evaluate(()=>window.MathMagicStatisticsProgress)).toBeUndefined();
});
