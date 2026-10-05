const { test, expect } = require('@playwright/test');
async function openTopic(page){await page.route('**/js/whole-numbers-auth.js*',r=>r.abort());await page.goto('/whole-numbers.html');await page.evaluate(()=>document.body.classList.remove('auth-loading'))}
test('whole numbers lessons render',async({page})=>{await openTopic(page);for(const id of ['lesson1','lesson2','lesson3','lesson4','lesson5','challenge']){await page.locator('[data-screen="'+id+'"]').click();await expect(page.locator('#'+id)).toHaveClass(/active/)}});
test('whole numbers 30 question challenge',async({page})=>{await openTopic(page);await page.locator('[data-screen="challenge"]').click();for(let q=1;q<=30;q++){await expect(page.locator('#qNumber')).toHaveText(q+' / 30');await expect(page.locator('#qPrompt')).not.toBeEmpty();const choices=page.locator('#qAnswer [data-choice]');if(await choices.count())await choices.first().click();else{await page.locator('#qAnswer input').fill('999999');await page.locator('#checkAnswer').click()}await expect(page.locator('#qFeedback')).not.toBeEmpty();await expect(page.locator('#nextQuestion')).toBeEnabled();await page.locator('#nextQuestion').click()}await expect(page.locator('#resultCard')).toContainText('CHALLENGE COMPLETE')});

test('external learning resources use privacy enhanced embeds and fallbacks',async({page})=>{
  await openTopic(page);
  for(const id of ['lesson1','lesson4','lesson5']){
    await page.locator('[data-screen="'+id+'"]').click();
    const card=page.locator('#'+id+' .video-resource');
    await expect(card).toBeVisible();
    const frame=card.locator('iframe');
    await expect(frame).toHaveAttribute('src',/^https:\/\/www\.youtube-nocookie\.com\/embed\//);
    await expect(frame).toHaveAttribute('title',/.+/);
    await expect(frame).toHaveAttribute('loading','lazy');
    const link=card.locator('a.resource-link');
    await expect(link).toHaveAttribute('href',/^https:\/\/www\.youtube\.com\/watch\?v=/);
    await expect(link).toHaveAttribute('rel',/noopener/);
  }
});
