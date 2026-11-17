// node docs/report/render_pdf.js  ->  docs/report/report.pdf (needs Playwright)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.resolve(__dirname, 'report.html'));
  await p.pdf({ path: path.resolve(__dirname, 'report.pdf'), format: 'A4', printBackground: true,
                displayHeaderFooter: true, headerTemplate: '<span></span>',
                footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888">ClaimGuard · CSL236 · page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
                margin: { top: '16mm', bottom: '18mm', left: '16mm', right: '16mm' } });
  await b.close();
})();
