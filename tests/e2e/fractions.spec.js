const { test, expect } = require('@playwright/test');

async function openFractions(page) {
  // CI isolates Firebase auth/progress so browser QA can deterministically test the
  // complete learning/challenge UI without storing real student credentials.
  await page.route('**/js/fractions-auth.js*', route => route.abort());
  await page.goto('/fractions.html');
  await page.evaluate(() => document.body.classList.remove('auth-loading'));
  await expect(page.locator('h1')).toHaveText('Fractions');
}

test('five learning pages and challenge navigation render', async ({ page }) => {
  await openFractions(page);
  const tabs = ['meaning','equivalent','mixed','addsub','problems','challenge'];
  for (const id of tabs) {
    await page.locator('[data-screen="'+id+'"]').click();
    await expect(page.locator('#'+id)).toHaveClass(/active/);
  }
});


test('five graphics-only lessons retain their verified MP4 players', async ({page})=>{
 await openFractions(page);
 const batch=require('../../video-agent/fractions-graphics-2026/manifest.json');
 for(const l of batch.lessons){
  await page.locator('[data-screen="'+l.section+'"]').click();
  const card=page.locator('[data-fractions-graphics="'+l.id+'"]'),video=card.locator('video');
  await expect(video).toBeVisible();await expect(video.locator('source')).toHaveAttribute('src',l.src);
  await expect(video.locator('source')).toHaveAttribute('type','video/mp4');
  for(const attr of ['controls','playsinline'])await expect(video).toHaveAttribute(attr,'');
  await expect(video).toHaveAttribute('preload','metadata');await expect(video).not.toHaveAttribute('autoplay',/.*/);
  await expect(video).toHaveAttribute('aria-label','MathMagic - '+l.title);
  await expect(card.locator('.video-frame + a')).toHaveAttribute('href',l.src);
  await expect(page.locator('#'+l.section+' iframe')).toHaveCount(0);
 }
});

test('original explainer frames stay responsive on desktop and mobile', async ({ page }) => {
  for (const vp of [{width:1280,height:800},{width:390,height:844}]) {
    await page.setViewportSize(vp);
    await openFractions(page);
    const frame = page.locator('#meaning .video-frame');
    const box = await frame.boundingBox();
    expect(box).not.toBeNull();
    expect(box.width).toBeLessThanOrEqual(vp.width);
    expect(Math.abs((box.width / box.height) - (16/9))).toBeLessThan(0.08);
  }
});

// UI-flow fixtures use each generated question's expected answer; mathematical
// correctness is independently covered by the existing generator regression.
async function submitValidAnswer(page) {
  const question = await page.evaluate(() => {
    const q = quiz[index];
    return { type: q.type, answer: q.answer, options: q.options };
  });
  await expect(page.locator('#nextQuestion')).toBeDisabled();
  if (question.type === 'choice') {
    const option = question.options.indexOf(question.answer);
    expect(option).toBeGreaterThanOrEqual(0);
    await page.locator(`[data-choice-index="${option}"]`).click();
  } else {
    if (question.type === 'mixed') {
      await page.locator('#whole').fill(String(question.answer[0]));
      await page.locator('#num').fill('1');
      await page.locator('#den').fill('1');
      await page.locator('#checkAnswer').click();
      await expect(page.locator('#nextQuestion')).toBeDisabled();
      await expect(page.locator('#qFeedback')).toContainText('less than one whole');
    }
    const fields = question.type === 'mixed' ? ['whole', 'num', 'den']
      : question.type === 'single' ? ['single'] : ['num', 'den'];
    const values = Array.isArray(question.answer) ? question.answer : [question.answer];
    for (let i = 0; i < fields.length; i++) {
      await page.locator('#' + fields[i]).fill(String(values[i]));
    }
    await expect(page.locator('#nextQuestion')).toBeDisabled();
    await page.locator('#checkAnswer').click();
  }
  await expect(page.locator('#qFeedback')).toHaveClass(/\bcorrect\b/);
  await expect(page.locator('#nextQuestion')).toBeEnabled();
}

test('all 30 challenge positions are interactive and visually usable', async ({ page }) => {
  await openFractions(page);
  await page.locator('[data-screen="challenge"]').click();

  for (let q = 1; q <= 30; q++) {
    await expect(page.locator('#qNumber')).toHaveText(q+' / 30');
    await expect(page.locator('#qPrompt')).not.toBeEmpty();
    await expect(page.locator('#qLevel')).not.toBeEmpty();

    const model = page.locator('#qDisplay .area-quiz, #qDisplay .strip-quiz, #qDisplay .fraction-visual, #qDisplay .number-line');
    if (await model.count()) {
      const box = await model.first().boundingBox();
      expect(box).not.toBeNull();
      expect(box.width).toBeGreaterThan(100);
      expect(box.height).toBeGreaterThan(20);
    }

    await submitValidAnswer(page);

    await expect(page.locator('#qFeedback')).not.toBeEmpty();
    await expect(page.locator('#nextQuestion')).toBeEnabled();
    await page.locator('#nextQuestion').click();
  }

  await expect(page.locator('#resultCard')).toBeVisible();
  await expect(page.locator('#resultCard')).toContainText('CHALLENGE COMPLETE');
});

test('student-facing challenge does not expose slash fraction notation', async ({ page }) => {
  await openFractions(page);
  await page.locator('[data-screen="challenge"]').click();
  for (let q = 1; q <= 30; q++) {
    const visible = await page.locator('#qPrompt, #qDisplay, #qAnswer').allTextContents();
    expect(visible.join(' ')).not.toMatch(/\b\d+\/\d+\b/);

    await submitValidAnswer(page);
    await page.locator('#nextQuestion').click();
  }
});
