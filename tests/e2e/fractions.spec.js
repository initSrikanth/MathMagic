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


test('five original MathMagic explainers retain approved MP4 or Scrimba players across the learning pages', async ({ page }) => {
  await openFractions(page);
  const mp4s = [
    ['meaning','videos/MathMagic_Comparing_Fractions_FINAL.mp4'],
    ['equivalent','https://raw.githubusercontent.com/initSrikanth/MathMagic/feature/video-production-agent/videos/MathMagic_Equivalent_Fractions_FINAL.mp4'],
    ['mixed','videos/MathMagic_Mixed_Numbers_FINAL.mp4']
  ];
  for (const [screen, src] of mp4s) {
    await page.locator('[data-screen="'+screen+'"]').click();
    const video = page.locator('#'+screen+' video');
    await expect(video).toHaveCount(1);
    await expect(page.locator('#'+screen+' iframe')).toHaveCount(0);
    await expect(video).toHaveAttribute('controls','');
    await expect(video).toHaveAttribute('playsinline','');
    await expect(video).toHaveAttribute('preload','metadata');
    await expect(video).toHaveAttribute('aria-label',/MathMagic/);
    await expect(video).not.toHaveAttribute('autoplay',/.*/);
    await expect(video.locator('source')).toHaveAttribute('src',src);
    await expect(video.locator('source')).toHaveAttribute('type','video/mp4');
    const fallbackSrc = screen === 'equivalent'
      ? 'https://github.com/initSrikanth/MathMagic/raw/refs/heads/feature/video-production-agent/videos/MathMagic_Equivalent_Fractions_FINAL.mp4'
      : src;
    await expect(page.locator('#'+screen+' .video-frame + a')).toHaveAttribute('href',fallbackSrc);
  }
  const expected = [
    ['addsub','guide0pl10dlm6','12ondtimn8vnq0il'],
    ['problems','guide0qcibakhr','klaes8bm913i2o8c']
  ];
  for (const [screen, guide, claim] of expected) {
    await page.locator('[data-screen="'+screen+'"]').click();
    const share='https://scrimba.com/explain/'+guide+'?claim='+claim+'&fullscreen=1';
    const frame = page.locator('#'+screen+' iframe[src="'+share+'"]');
    await expect(frame).toHaveCount(1);
    await expect(frame).toHaveAttribute('loading','lazy');
    await expect(frame).toHaveAttribute('title',/MathMagic/);
    await expect(frame).toHaveAttribute('allowfullscreen','');
    const fallback = page.locator('#'+screen+' a[href="'+share+'"]');
    await expect(fallback).toHaveCount(1);
  }
});

test('approved Mixed Numbers video loads and plays within desktop and mobile layouts', async ({ page }) => {
  const response=await page.request.get('/videos/MathMagic_Mixed_Numbers_FINAL.mp4',{headers:{Range:'bytes=0-1023'}});
  expect(response.status()).toBe(206);
  expect(response.headers()['content-type']).toBe('video/mp4');
  expect(response.headers()['content-range']).toBe('bytes 0-1023/4870811');
  expect((await response.body()).length).toBe(1024);
  await openFractions(page);
  await page.locator('[data-screen="mixed"]').click();
  const video = page.locator('#mathmagic-mixed-video');
  await expect.poll(() => video.evaluate(v => v.readyState)).toBeGreaterThanOrEqual(2);
  const metadata = await video.evaluate(v => ({duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error?.code}));
  expect(metadata.error).toBeUndefined();
  expect(metadata.duration).toBeCloseTo(75.889,1);
  expect(metadata.width).toBe(1280);
  expect(metadata.height).toBe(720);
  await video.evaluate(v => v.play());
  await expect.poll(() => video.evaluate(v => v.currentTime)).toBeGreaterThan(0.2);
  for (const time of [15,30,45,60,74]) {
    await video.evaluate((v,t) => {v.pause();v.currentTime=t;},time);
    await expect.poll(() => video.evaluate(v => !v.seeking && v.readyState >= 2)).toBeTruthy();
    expect(await video.evaluate(v => v.currentTime)).toBeCloseTo(time,0);
  }
  await video.evaluate(v => {v.currentTime=74;return v.play();});
  await expect.poll(() => video.evaluate(v => v.ended),{timeout:10000}).toBeTruthy();
  for (const viewport of [{width:1280,height:800},{width:390,height:844}]) {
    await page.setViewportSize(viewport);
    const box=await video.boundingBox();
    expect(box).not.toBeNull();
    expect(box.width).toBeLessThanOrEqual(viewport.width);
    expect(Math.abs(box.width/box.height-16/9)).toBeLessThan(0.08);
    expect(await page.evaluate(() => document.documentElement.scrollWidth<=document.documentElement.clientWidth+1)).toBeTruthy();
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

    const choices = page.locator('#qAnswer [data-choice-index]');
    if (await choices.count()) {
      await choices.first().click();
    } else {
      const inputs = page.locator('#qAnswer input');
      expect(await inputs.count()).toBeGreaterThan(0);
      for (let i = 0; i < await inputs.count(); i++) await inputs.nth(i).fill('1');
      await page.locator('#checkAnswer').click();
    }

    // Some simplified-fraction entries can request further simplification after
    // an equivalent answer. Replace with a clearly wrong value to complete the item.
    if (!(await page.locator('#nextQuestion').isEnabled())) {
      const inputs = page.locator('#qAnswer input');
      for (let i = 0; i < await inputs.count(); i++) {
        await inputs.nth(i).fill(i === 0 ? '999' : '997');
      }
      await page.locator('#checkAnswer').click();
    }

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

    const choices = page.locator('#qAnswer [data-choice-index]');
    if (await choices.count()) await choices.first().click();
    else {
      const inputs = page.locator('#qAnswer input');
      for (let i = 0; i < await inputs.count(); i++) await inputs.nth(i).fill(i === 0 ? '999' : '997');
      await page.locator('#checkAnswer').click();
    }
    if (!(await page.locator('#nextQuestion').isEnabled())) {
      const inputs = page.locator('#qAnswer input');
      for (let i = 0; i < await inputs.count(); i++) await inputs.nth(i).fill(i === 0 ? '991' : '983');
      await page.locator('#checkAnswer').click();
    }
    await page.locator('#nextQuestion').click();
  }
});
