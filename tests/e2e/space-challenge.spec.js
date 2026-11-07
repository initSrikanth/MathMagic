const {test,expect}=require('@playwright/test');

// Browser integration for the actual Space challenge UI and question generator.
// Firebase is replaced only in this test's network route; production auth remains unchanged.
test.beforeEach(async ({page})=>{
  await page.route('**/js/space-auth.js',async route=>route.fulfill({
    status:200,contentType:'application/javascript',
    body:`window.__spaceSaves=[];window.__spaceFailSave=false;
      window.MathMagicSpaceProgress={
        async saveAttempt(score,id){
          window.__spaceSaves.push({score,id});
          if(window.__spaceFailSave)throw new Error('Simulated offline save');
          return {attempts:1,bestScore:score};
        }
      };
      document.body.classList.remove('auth-loading');`
  }));
  await page.goto('/space-challenge.html');
  await expect(page.getByRole('button',{name:'Start challenge'})).toBeEnabled();
});

test('30 questions, six bands, worked feedback and a single saved attempt',async ({page})=>{
  await page.getByRole('button',{name:'Start challenge'}).click();
  for(let i=0;i<30;i++){
    await expect(page.locator('#questionNumber')).toContainText('Question '+(i+1)+' of 30');
    await expect(page.locator('#questionNumber')).toContainText('Level '+(Math.floor(i/5)+1)+' of 6');
    await expect(page.locator('#choices button')).toHaveCount(4);
    await page.locator('#choices button').first().click();
    await page.getByRole('button',{name:'Check answer'}).click();
    await expect(page.locator('#feedback')).toBeVisible();
    await expect(page.locator('#feedback')).not.toBeEmpty();
    await page.locator('#nextBtn').click();
  }
  await expect(page.getByText('Attempt saved.')).toBeVisible();
  expect(await page.evaluate(()=>window.__spaceSaves)).toHaveLength(1);
  await expect(page.getByRole('button',{name:'Try a new challenge'})).toBeEnabled();
});

test('failed progress save retains attempt ID, retries without duplicate and blocks restart',async ({page})=>{
  await page.evaluate(()=>window.__spaceFailSave=true);
  await page.getByRole('button',{name:'Start challenge'}).click();
  for(let i=0;i<30;i++){
    await page.locator('#choices button').first().click();
    await page.getByRole('button',{name:'Check answer'}).click();
    await page.locator('#nextBtn').click();
  }
  await expect(page.getByRole('button',{name:'Retry saving this attempt'})).toBeVisible();
  await expect(page.getByRole('button',{name:'Try a new challenge'})).toBeHidden();
  await page.evaluate(()=>window.__spaceFailSave=false);
  await page.getByRole('button',{name:'Retry saving this attempt'}).click();
  await expect(page.getByText('Attempt saved.')).toBeVisible();
  const saves=await page.evaluate(()=>window.__spaceSaves);
  expect(saves).toHaveLength(2);
  expect(saves[0].id).toBe(saves[1].id);
  expect(saves[0].score).toBe(saves[1].score);
});
