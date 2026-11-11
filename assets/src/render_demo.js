// node assets/src/render_demo.js  -> frames in assets/_work/frames (deterministic seek), then ffmpeg builds demo.mp4 / demo.gif
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const FPS = +process.env.FPS || 30;
(async () => {
  const out = path.resolve(__dirname, '..', '_work', 'frames');
  fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  await p.goto('file://' + path.resolve(__dirname, 'demo.html'));
  await p.evaluate(() => document.fonts.ready);
  const dur = await p.evaluate(() => window.DURATION);
  const words = await p.evaluate(() => window.WORDS);
  console.log('words', JSON.stringify(words), 'duration', dur);
  const n = Math.round(dur / 1000 * FPS);
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => window.render(t), i * 1000 / FPS);
    await p.screenshot({ path: path.join(out, `f${String(i).padStart(5, '0')}.png`) });
  }
  await b.close();
  console.log('frames', n);
})();
