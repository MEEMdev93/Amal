const {chromium}=require('/opt/node22/lib/node_modules/playwright');const fs=require('fs'),path=require('path');
(async()=>{const b=await chromium.launch();
for(const line of fs.readFileSync(process.argv[2],'utf8').trim().split('\n')){const [f,o,W,H,sc,pdf]=line.split('|');
const p=await b.newPage({viewport:{width:+W,height:+H},deviceScaleFactor:+sc});
await p.goto('file://'+path.resolve(f));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(200);
await p.screenshot({path:o});if(pdf)await p.pdf({path:pdf,printBackground:true,preferCSSPageSize:true});await p.close();console.log('done',o)}
await b.close();})();
