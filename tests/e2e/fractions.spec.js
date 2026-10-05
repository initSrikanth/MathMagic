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
