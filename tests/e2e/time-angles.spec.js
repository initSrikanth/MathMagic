const {test,expect}=require('@playwright/test');

// UI checks only: the production Firebase approval and persistence path is not mocked as verified.
async function openTopic(page){
  await page.route('**/js/time-angles-auth.js*',route=>route.abort());
  await page.goto('/time-angles.html');
  await page.evaluate(()=>{
    document.body.classList.remove('auth-loading');
    window.__saved=[];
    window.MathMagicTimeAnglesProgress={
      saveAttempt:async(score,id)=>{
        window.__saved.push({score,id});
        return {attempts:window.__saved.length,bestScore:score};
      }
    };
  });
}

test('Time and Angles: five lessons, navigation and mobile dashboard link',async({page})=>{
  await openTopic(page);
  for(const size of [{width:390,height:844},{width:1280,height:800}]){
    await page.setViewportSize(size);
    for(let n=1;n<=5;n++){
      await page.locator('[data-screen="lesson'+n+'"]').click();
      await expect(page.locator('#lesson'+n)).toHaveClass(/active/);
      await expect(page.locator('#lesson'+n+' .learn').first().locator('ol li')).toHaveCount(3);
      expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
    }
    await expect(page.locator('.topic-return a[href="dashboard.html"]').first()).toBeVisible();
  }
});

test('Time and Angles: complete 30-question challenge and save once',async({page})=>{
  await openTopic(page);
  await page.locator('[data-screen="challenge"]').click();
  for(let n=0;n<30;n++){
    await expect(page.locator('#qNumber')).toHaveText((n+1)+' / 30');
    await expect(page.locator('#nextQuestion')).toBeDisabled();
    const answer=await page.evaluate(()=>quiz[index].answer);
    await page.locator('#answerInput').fill(answer);
    await page.locator('#checkAnswer').click();
    await expect(page.locator('#qFeedback')).toHaveText('Correct!');
    await expect(page.locator('#qSolution')).toBeVisible();
    await page.locator('#nextQuestion').click();
  }
  await expect(page.locator('#resultCard')).toContainText('Challenge complete: 30 / 30');
  await expect(page.locator('#resultCard')).toContainText('Attempt saved');
  const saves=await page.evaluate(()=>window.__saved);
  expect(saves).toHaveLength(1);
  expect(saves[0].score).toBe(30);
  expect(saves[0].id).toMatch(/^[A-Za-z0-9_-]{8,100}$/);
});

test('Time and Angles: invalid time input does not advance',async({page})=>{
  await openTopic(page);
  await page.locator('[data-screen="challenge"]').click();
  // The first sequence item is angle classification; reach the first time-format question.
  await page.locator('#answerInput').fill('acute');
  await page.locator('#checkAnswer').click();
  await page.locator('#nextQuestion').click();
  await expect(page.locator('#qTopic')).toHaveText('12-hour and 24-hour time');
  for(const bad of ['25:90','2:05','abc']){
    await page.locator('#answerInput').fill(bad);
    await page.locator('#checkAnswer').click();
    await expect(page.locator('#nextQuestion')).toBeDisabled();
  }
});

test('Time and Angles: Back to Dashboard navigates from lessons and challenge on mobile',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.route('**/js/auth-guard.js*',route=>route.abort());
  await openTopic(page);
  await page.locator('[data-screen="lesson5"]').click();
  await page.locator('.topic-return a[href="dashboard.html"]').first().click();
  await expect(page).toHaveURL(/\/dashboard\.html$/);
  await page.goto('/time-angles.html');
  await page.evaluate(()=>{
    document.body.classList.remove('auth-loading');
    window.MathMagicTimeAnglesProgress={saveAttempt:async()=>({attempts:1,bestScore:30})};
  });
  await page.locator('[data-screen="challenge"]').click();
  await expect(page.locator('.topic-return a[href="dashboard.html"]').first()).toBeVisible();
  await page.locator('.topic-return a[href="dashboard.html"]').first().click();
  await expect(page).toHaveURL(/\/dashboard\.html$/);
});

test('Time and Angles: malformed numeric responses do not consume a question',async({page})=>{
  await openTopic(page);
  await page.locator('[data-screen="challenge"]').click();
  // The first question is angle classification; answer it to reach a time-format question.
  await page.locator('#answerInput').fill('acute');
  await page.locator('#checkAnswer').click();
  await page.locator('#nextQuestion').click();
  await expect(page.locator('#qNumber')).toHaveText('2 / 30');
  for(const invalid of ['24:00','00:60','12:5','-01:00']){
    await page.locator('#answerInput').fill(invalid);
    await page.locator('#checkAnswer').click();
    await expect(page.locator('#qNumber')).toHaveText('2 / 30');
    await expect(page.locator('#nextQuestion')).toBeDisabled();
  }
});


test('Time and Angles: failed progress write can retry without counting twice',async({page})=>{
  await openTopic(page);
  await page.evaluate(()=>{
    window.__saveCalls=[];
    window.MathMagicTimeAnglesProgress={saveAttempt:async(score,id)=>{
      window.__saveCalls.push({score,id});
      if(window.__saveCalls.length===1)throw new Error('Temporary connection failure');
      return {attempts:1,bestScore:score};
    }};
  });
  await page.locator('[data-screen="challenge"]').click();
  for(let n=0;n<30;n++){
    const answer=await page.evaluate(()=>quiz[index].answer);
    await page.locator('#answerInput').fill(answer);
    await page.locator('#checkAnswer').click();
    await page.locator('#nextQuestion').click();
  }
  await expect(page.locator('#resultCard')).toContainText('Save failed');
  await page.getByRole('button',{name:'Retry saving'}).click();
  await expect(page.locator('#resultCard')).toContainText('Attempt saved');
  const calls=await page.evaluate(()=>window.__saveCalls);
  expect(calls).toHaveLength(2);
  expect(calls[0]).toEqual(calls[1]);
  await expect(page.locator('#resultCard button').filter({hasText:'Retry saving'})).toBeHidden();
});


test('Time and Angles: incorrect response reveals worked feedback without awarding a mark',async({page})=>{
  await openTopic(page);
  await page.locator('[data-screen="challenge"]').click();
  const expected=await page.evaluate(()=>quiz[index].answer);
  const wrong=expected==='acute'?'reflex':'acute';
  await page.locator('#answerInput').fill(wrong);
  await page.locator('#checkAnswer').click();
  await expect(page.locator('#qFeedback')).toContainText('Not quite');
  await expect(page.locator('#qSolution')).toContainText('Worked solution:');
  await expect(page.locator('#qSolution')).toContainText('Correct answer: '+expected);
  await expect(page.locator('#qScore')).toHaveText('0 / 30');
  await expect(page.locator('#nextQuestion')).toBeEnabled();
  await page.locator('#nextQuestion').click();
  await expect(page.locator('#qNumber')).toHaveText('2 / 30');
});


test('Time and Angles: 12-hour pm answer passes both format and numeric validation',async({page})=>{
  await openTopic(page);
  await page.locator('[data-screen="challenge"]').click();
  const target=await page.evaluate(()=>quiz.findIndex(q=>q.kind===11));
  expect(target).toBeGreaterThanOrEqual(0);
  for(let n=0;n<target;n++){
    const answer=await page.evaluate(()=>quiz[index].answer);
    await page.locator('#answerInput').fill(answer);
    await page.locator('#checkAnswer').click();
    await expect(page.locator('#nextQuestion')).toBeEnabled();
    await page.locator('#nextQuestion').click();
  }
  const answer=await page.evaluate(()=>quiz[index].answer);
  expect(answer).toMatch(/^(?:[1-9]|1[0-2]):[0-5]\d pm$/);
  await page.locator('#answerInput').fill(answer);
  await page.locator('#checkAnswer').click();
  await expect(page.locator('#qFeedback')).toHaveText('Correct!');
  await expect(page.locator('#nextQuestion')).toBeEnabled();
});

const AxeBuilder=require('@axe-core/playwright').default;
test('Time and Angles: WCAG AA, transcript keyboard access and responsive lessons',async({page})=>{
  await openTopic(page);
  for(const screen of ['lesson1','lesson2','lesson3','lesson4','lesson5','challenge']){
    await page.locator('[data-screen="'+screen+'"]').click();
    const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
    expect(result.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),screen).toEqual([]);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
    if(screen!=='lesson1'&&screen!=='challenge'){
      const summary=page.locator('#'+screen+' .video-transcript summary');await summary.focus();await page.keyboard.press('Enter');
      await expect(page.locator('#'+screen+' .video-transcript')).toHaveAttribute('open','');
      const link=page.locator('#'+screen+' .video-transcript a');expect((await page.request.get(await link.getAttribute('href'))).ok()).toBe(true);
    }
  }
});

test('Time and Angles: four native caption tracks load and follow early, middle and late playback',async({page})=>{
  test.setTimeout(120000);await openTopic(page);
  for(let n=2;n<=5;n++){
    await page.locator('[data-screen="lesson'+n+'"]').click();
    const video=page.locator('#lesson'+n+' video');await expect(video).toHaveAttribute('playsinline','');
    const track=video.locator('track[kind="captions"][srclang="en"]');await expect(track).toHaveCount(1);
    await video.evaluate(v=>{v.muted=true;v.preload='auto';v.load();v.textTracks[0].mode='showing';});
    await expect.poll(()=>video.evaluate(v=>v.readyState>=2&&v.textTracks[0].cues?.length>40)).toBe(true);
    expect(await video.evaluate(v=>Array.from(v.textTracks[0].cues).every(c=>c.line===1&&c.position===50&&c.size===90))).toBe(true);
    const times=await video.evaluate(v=>{const cues=v.textTracks[0].cues;return [0,Math.floor(cues.length/2),cues.length-1].map(i=>cues[i].startTime+.1)});
    for(const time of times){
      await video.evaluate(async(v,t)=>{v.currentTime=t;await v.play()},time);
      await expect.poll(()=>video.evaluate(v=>v.currentTime)).toBeGreaterThan(time+.05);
      await expect.poll(()=>video.evaluate(v=>v.textTracks[0].activeCues?.length||0)).toBeGreaterThan(0);
      await video.evaluate(v=>v.pause());
    }
    await expect(video).toHaveAttribute('poster',/.+\.jpg$/);
  }
  await page.locator('[data-screen="lesson1"]').click();
  await expect(page.locator('#lesson1 video track')).toHaveCount(0); // Explicitly blocked, not fabricated captions.
});

test('Time and Angles: replacement question controls reject malformed formats and retain feedback colours',async({page})=>{
  await openTopic(page);await page.locator('[data-screen="challenge"]').click();
  for(let n=0;n<30;n++){
    const q=await page.evaluate(()=>quiz[index]);
    if([13,14,16].includes(q.kind)){
      const bad=q.kind===14?'C':'25:00';await page.locator('#answerInput').fill(bad);await page.locator('#checkAnswer').click();await expect(page.locator('#nextQuestion')).toBeDisabled();
    }
    await page.locator('#answerInput').fill(q.answer);await page.locator('#checkAnswer').click();
    await expect(page.locator('#qFeedback')).toHaveClass(/correct/);
    expect(await page.locator('#qFeedback').evaluate(e=>getComputedStyle(e).color)).toBe('rgb(24, 121, 78)');
    await page.locator('#nextQuestion').click();
  }
});
