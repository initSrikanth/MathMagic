const { test, expect } = require('@playwright/test');
const { createHash } = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

test('non-production MP4 fixture supports byte ranges, playback, seeking and mobile containment', async ({ page, request, baseURL }) => {
  // This standalone harness does not navigate to or change a live lesson/auth flow.
  const localBytes = fs.readFileSync(path.join(__dirname, '../fixtures/video-production-smoke.mp4'));
  const mediaPath = '/tests/fixtures/video-production-smoke.mp4';
  const complete = await request.get(mediaPath);
  expect(complete.status()).toBe(200);
  expect(complete.headers()['content-type']).toBe('video/mp4');
  expect(createHash('sha256').update(await complete.body()).digest('hex'))
    .toBe(createHash('sha256').update(localBytes).digest('hex'));
  const range = await request.get(mediaPath, { headers: { Range: 'bytes=0-1023' } });
  expect(range.status()).toBe(206);
  expect(range.headers()['content-range']).toBe(`bytes 0-1023/${localBytes.length}`);
  expect((await range.body()).length).toBe(1024);
  const invalid = await request.get(mediaPath, { headers: { Range: `bytes=${localBytes.length}-` } });
  expect(invalid.status()).toBe(416);
  await page.setContent(`<meta name="viewport" content="width=device-width, initial-scale=1"><main style="max-width:960px;margin:auto"><h1>Non-production video transport check</h1>
    <video aria-label="MathMagic readiness fixture" controls playsinline preload="metadata" style="width:100%;height:auto">
    <source src="${baseURL}${mediaPath}" type="video/mp4"></video></main>`);
  const video = page.getByLabel('MathMagic readiness fixture');
  await expect.poll(() => video.evaluate(v => v.readyState)).toBeGreaterThanOrEqual(2);
  const metadata = await video.evaluate(v => ({ width: v.videoWidth, height: v.videoHeight, duration: v.duration, error: v.error?.code }));
  expect(metadata.width).toBe(1920);
  expect(metadata.height).toBe(1080);
  expect(metadata.duration).toBeGreaterThan(3.9);
  expect(metadata.duration).toBeLessThan(4.1);
  expect(metadata.error).toBeUndefined();
  await video.evaluate(v => v.play());
  await expect.poll(() => video.evaluate(v => v.currentTime)).toBeGreaterThan(0.2);
  for (const seconds of [0.5, 2, 3.2]) {
    await video.evaluate((v, t) => { v.pause(); v.currentTime = t; }, seconds);
    await expect.poll(() => video.evaluate(v => !v.seeking && v.readyState >= 2)).toBeTruthy();
    expect(await video.evaluate(v => v.currentTime)).toBeCloseTo(seconds, 1);
  }
  await video.evaluate(v => { v.currentTime = 3.4; return v.play(); });
  await expect.poll(() => video.evaluate(v => v.ended)).toBeTruthy();
  const box = await video.boundingBox();
  expect(box.x).toBeGreaterThanOrEqual(0);
  expect(box.x + box.width).toBeLessThanOrEqual(page.viewportSize().width);
  expect(box.width / box.height).toBeCloseTo(16 / 9, 2);
});
