/* Keep confirmations inside the workbench; native dialogs pause embedded pages. */
(() => {
    const el=id=>document.getElementById(id);
    const overlay=el('studio-confirm'),input=el('studio-confirm-input');
    const cancel=el('studio-confirm-cancel'),accept=el('studio-confirm-accept');
    let pending=null;
    const text=(zh,en)=>window.StudioI18n?.locale()==='en-US'?en:window.StudioI18n?.t(zh)||zh;
    function finish(approved) {
        if(!pending)return;
        const decision=pending;pending=null;
        overlay.classList.remove('active');overlay.setAttribute('aria-hidden','true');
        decision.previous?.focus?.();
        decision.resolve(decision.prompt?(approved?input.value:null):approved);
    }
    function ask(message,prompt,initial='') {
        if(pending)return Promise.resolve(prompt?null:false);
        el('studio-confirm-title').textContent=text(prompt?'输入内容':'确认操作',prompt?'Enter a value':'Confirm action');
        el('studio-confirm-message').textContent=String(message);
        cancel.textContent=text('取消','Cancel');accept.textContent=text('确认','Confirm');
        input.hidden=!prompt;input.value=String(initial??'');
        input.setAttribute('aria-label',text('输入内容','Enter a value'));
        return new Promise(resolve=>{
            pending={resolve,prompt,previous:document.activeElement};
            overlay.classList.add('active');overlay.setAttribute('aria-hidden','false');
            (prompt?input:cancel).focus();if(prompt)input.select();
        });
    }
    cancel.addEventListener('click',()=>finish(false));
    accept.addEventListener('click',()=>finish(true));
    overlay.addEventListener('click',event=>{if(event.target===overlay)finish(false);});
    overlay.addEventListener('keydown',event=>{
        if(!pending)return;
        if(event.key==='Escape'){event.preventDefault();finish(false);}
        else if(event.key==='Enter'&&event.target===input){event.preventDefault();finish(true);}
        else if(event.key==='Tab'){
            const controls=pending.prompt?[input,cancel,accept]:[cancel,accept];
            const index=controls.indexOf(document.activeElement);
            event.preventDefault();controls[(index+(event.shiftKey?-1:1)+controls.length)%controls.length].focus();
        }
    });
    window.confirmStudio=message=>ask(message,false);
    window.promptStudio=(message,initial='')=>ask(message,true,initial);
})();
