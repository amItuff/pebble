// node assets/src/render_banner.js  -> assets/banner.png (2560x1280) and assets/social-preview.png (1280x640)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  for (const [scale, out] of [[2, 'banner.png'], [1, 'social-preview.png']]) {
    const p = await b.newPage({ viewport: { width: 1280, height: 640 }, deviceScaleFactor: scale });
    await p.goto('file://' + path.resolve(__dirname, 'banner.html'));
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.resolve(__dirname, '..', out) });
    await p.close();
  }
  await b.close();
})();
