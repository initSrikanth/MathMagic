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
  await expect(page.getByRole('button',{name:'Retry saving'})).toHaveCount(0);
});
