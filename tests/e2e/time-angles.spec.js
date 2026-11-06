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
