const {chromium}=require('/opt/node22/lib/node_modules/playwright');(async()=>{const b=await chromium.launch();
for(const [f,o] of [['html/letter-purelens.html','content.pdf'],['html/letter-bg.html','bg.pdf']]){const p=await b.newPage({viewport:{width:794,height:1123}});
await p.goto('file://'+process.cwd()+'/'+f);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
await p.pdf({path:o,printBackground:true,preferCSSPageSize:true});await p.close()}await b.close()})()
