const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const path='3DWET/app/static/js/confirm_dialog.js';
assert.ok(fs.existsSync(path),'an in-app asynchronous confirmation is required');
const listeners={};let focused={focus(){focused=this;}};const originalFocus=focused;
const elements={};
for(const id of ['studio-confirm','studio-confirm-title','studio-confirm-message','studio-confirm-input','studio-confirm-cancel','studio-confirm-accept']) {
 const classes=new Set();elements[id]={id,value:'',hidden:false,textContent:'',
  classList:{add:x=>classes.add(x),remove:x=>classes.delete(x),contains:x=>classes.has(x)},
  setAttribute(){},focus(){focused=this;},select(){},
  addEventListener:(type,fn)=>listeners[id+':'+type]=fn};
}
const window={StudioI18n:{locale:()=> 'en-US',t:s=>s}};
const context=vm.createContext({window,document:{getElementById:id=>elements[id],get activeElement(){return focused;}},Promise});
vm.runInContext(fs.readFileSync(path,'utf8'),context);
(async()=>{
 let settled=false;
 const first=window.confirmStudio('<unsafe> Keep inputs?').then(v=>{settled=true;return v;});
 await Promise.resolve();assert.equal(settled,false,'dialog must await a user decision');
 assert.equal(elements['studio-confirm-message'].textContent,'<unsafe> Keep inputs?','message must remain plain text');
 assert.equal(elements['studio-confirm-cancel'].textContent,'Cancel');
 assert.equal(focused,elements['studio-confirm-cancel'],'safe action receives initial focus');
 assert.equal(await window.confirmStudio('Second request'),false,'a second request cannot replace a pending decision');
 listeners['studio-confirm-cancel:click']();assert.equal(await first,false);
 assert.equal(focused,originalFocus,'focus returns to the invoking control');
 const accepted=window.confirmStudio('Proceed?');listeners['studio-confirm-accept:click']();assert.equal(await accepted,true);
 const prompt=window.promptStudio('River name','SEED_IN');assert.equal(elements['studio-confirm-input'].value,'SEED_IN');
 elements['studio-confirm-input'].value='SEED_OUT';listeners['studio-confirm-accept:click']();assert.equal(await prompt,'SEED_OUT');
 const cancelled=window.promptStudio('Name','');listeners['studio-confirm:keydown']({key:'Escape',preventDefault(){}});assert.equal(await cancelled,null);
 assert.equal(elements['studio-confirm'].classList.contains('active'),false);
 console.log('In-app confirm/prompt: wait, cancel, accept, text, focus and concurrent protection PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
