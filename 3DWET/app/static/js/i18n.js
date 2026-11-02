/* Offline UI localization. Scientific values, user input and identifiers are never translated. */
(() => {
    'use strict';
    const LOCALE_KEY='3dwet.locale', PACK_KEY='3dwet.languagePacks', MAX_BYTES=262144;
    const CJK=/[\u3400-\u9fff]/;
    const packs=new Map([['zh-CN',{locale:'zh-CN',name:'中文',messages:Object.create(null)}],
        ['en-US',{locale:'en-US',name:'English',messages:Object.create(null)}]]);
    const read=k=>{try{return localStorage.getItem(k);}catch{return null;}};
    const save=(k,v)=>{try{localStorage.setItem(k,v);}catch{/* Private profiles may deny persistence. */}};
    let active=read(LOCALE_KEY)||'zh-CN', observer=null, dialog=null, returnFocus=null;
    const textSources=new WeakMap(), attributeSources=new WeakMap(), fallbacks=new Set(), englishFallbacks=new Set();
    let translatedCount=0;
    const matchers=new Map();
    const excluded='script,style,noscript,pre,code,textarea,[contenteditable],svg,canvas,.js-plotly-plot,.plot-container,.leaflet-pane,#run-log,.run-log,.code-editor,.file-path,[data-file-path],[data-variable-code],[data-i18n-skip]';
    function validatePack(input, builtin=false) {
        const raw=typeof input==='string' ? input : JSON.stringify(input);
        if(typeof raw!=='string'||raw.length>MAX_BYTES) throw new Error('Language pack size is too large (256 KiB maximum).');
        // Check UTF-8 bytes too: a short Chinese string may contain many bytes.
        if(typeof TextEncoder!=='undefined' && new TextEncoder().encode(raw).length>MAX_BYTES) throw new Error('Language pack size is too large (256 KiB maximum).');
        const value=JSON.parse(raw);
        if(!value || Array.isArray(value)||typeof value!=='object') throw new Error('Language pack must be a JSON object.');
        for(const key of Object.keys(value)) if(!['locale','name','messages'].includes(key)) throw new Error('Unsafe or unsupported language pack field.');
        if(typeof value.locale!=='string'||! /^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$/.test(value.locale)||value.locale.length>35) throw new Error('Invalid locale.');
        try { value.locale=Intl.getCanonicalLocales(value.locale)[0]; } catch { throw new Error('Invalid locale.'); }
        if(!builtin && ['zh-CN','en-US'].includes(value.locale)) throw new Error('Built-in locale is reserved.');
        if(typeof value.name!=='string'||!value.name.trim()||value.name.length>60||/[<>\u0000-\u001f]/.test(value.name)) throw new Error('Language name must be plain text.');
        if(!value.messages||typeof value.messages!=='object'||Array.isArray(value.messages)||Object.keys(value.messages).length>4000) throw new Error('messages must be a plain text JSON dictionary (maximum 4000 entries).');
        const messages=Object.create(null);
        for(const [key,text] of Object.entries(value.messages)) {
            if(['__proto__','prototype','constructor'].includes(key)) throw new Error('Unsafe prototype key in language pack.');
            if(typeof text!=='string'||key.length>2000||text.length>5000) throw new Error('Language messages must be plain text strings.');
            if(/<\/?[a-z!][^>]*>/i.test(text)||/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(text)) throw new Error('HTML is not allowed; language messages must be plain text.');
            messages[key]=text;
        }
        return {locale:value.locale,name:value.name.trim(),messages};
    }
    function importPack(input) {
        const pack=validatePack(input);
        if(!packs.has(pack.locale) && packs.size>=18) throw new Error('Maximum 16 imported language packs.');
        packs.set(pack.locale,pack);
        matchers.delete(pack.locale);
        save(PACK_KEY,JSON.stringify([...packs.values()].filter(p=>!['zh-CN','en-US'].includes(p.locale))));
        return {locale:pack.locale,name:pack.name};
    }
    try {for(const pack of JSON.parse(read(PACK_KEY)||'[]')) {const valid=validatePack(pack);packs.set(valid.locale,valid);}} catch {/* Ignore corrupt stored packs. */}
    if(!packs.has(active)) active='zh-CN';
    function compose(source,messages) {
        if(!messages)return undefined;
        const paths=[];
        let protectedSource=source.replace(/(?:[A-Za-z]:[\\/]|\\\\)[^\s<>"'：，。；！？、]+|(?:^|(?<=\s))\/(?:[^\s<>"'：，。；！？、]+)/g,path=>{paths.push(path);return '\u0001'+(paths.length-1)+'\u0002';});
        for(const [regex,key,fields] of [
            [/已选择 (\d+) 个/g,'已选择 {count} 个',{count:0}],
            [/已选择 (\d+) 格/g,'已选择 {count} 格',{count:0}],
            [/核对已解析的 (\d+) 条食性端口关系 · 闭合三节点有向环 (\d+) 个/g,'核对已解析的 {edges} 条食性端口关系 · 闭合三节点有向环 {cycles} 个',{edges:0,cycles:1}],
            [/配置支持的角色实例：生产者\/碎屑 (\d+)，有食性边的消费者 (\d+)，有食性边的鱼类\/顶级捕食者 (\d+)。/g,'配置支持的角色实例：生产者/碎屑 {basal}，有食性边的消费者 {consumers}，有食性边的鱼类/顶级捕食者 {fish}。',{basal:0,consumers:1,fish:2}],
            [/已解析的三节点食性路径 (\d+) 条（3个不同实例、2条有向饮食边；不等同于三角闭环、营养级或已验证摄食）。下方逐条列出真实实例与端口。/g,'已解析的三节点食性路径 {count} 条（3个不同实例、2条有向饮食边；不等同于三角闭环、营养级或已验证摄食）。下方逐条列出真实实例与端口。',{count:0}],
            [/；三实例配置链，(\d+) 条已解析有向饮食边/g,'；三实例配置链，{count} 条已解析有向饮食边',{count:0}],
            [/已解析到实例的猎物→消费者引用 (\d+) 条；配置但未解析 (\d+) 条；声明食性槽未配置端口 (\d+) 个；消费者之间的配置食性边 (\d+) 条；真实已解析边构成的闭合三节点有向环 (\d+) 个。闭环数为 0 时代表当前配置没有闭环；图不推断未配置关系。/g,'已解析到实例的猎物→消费者引用 {references} 条；配置但未解析 {unresolved} 条；声明食性槽未配置端口 {missing} 个；消费者之间的配置食性边 {consumerLinks} 条；真实已解析边构成的闭合三节点有向环 {cycles} 个。闭环数为 0 时代表当前配置没有闭环；图不推断未配置关系。',{references:0,unresolved:1,missing:2,consumerLinks:3,cycles:4}],
            [/(\d+) 个 FABM 实例 · (\d+) 个显式耦合端口 · (\d+) 个已解析食性引用/g,'{instances} 个 FABM 实例 · {ports} 个显式耦合端口 · {dietLinks} 个已解析食性引用',{instances:0,ports:1,dietLinks:2}],
            [/未解析食性引用 (\d+) 条/g,'未解析食性引用 {count} 条',{count:0}]
        ]) {
            if(messages[key])protectedSource=protectedSource.replace(regex,(...args)=>{
                let translated=messages[key];
                for(const [name,index] of Object.entries(fields))translated=translated.replace(`{${name}}`,args[index+1]);
                return translated;
            });
        }
        let matcher=matchers.get(active);
        if(!matcher) {
            const keys=Object.keys(messages).filter(key=>CJK.test(key)&&key.length>1).sort((a,b)=>b.length-a.length);
            if(Object.hasOwn(messages,'层'))keys.push('层');
            matcher=keys.length ? new RegExp(keys.map(key=>key.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|'),'g') : null;
            matchers.set(active,matcher);
        }
        if(!matcher)return undefined;
        const result=protectedSource.replace(matcher,key=>messages[key]);
        // Do not produce invented or half-translated unknown Chinese phrases.
        return result!==source&&!CJK.test(result) ? result.replace(/\u0001(\d+)\u0002/g,(_,n)=>paths[Number(n)]) : undefined;
    }
    function t(value, params) {
        const source=String(value ?? '');
        let result=source;
        if(active!=='zh-CN') {
            const trimmed=source.trim(), ownMessages=packs.get(active)?.messages;
            const messages=active==='en-US' ? ownMessages : Object.assign(Object.create(null),packs.get('en-US')?.messages,ownMessages);
            if(active!=='en-US'&&ownMessages?.[trimmed]===undefined&&packs.get('en-US')?.messages?.[trimmed]!==undefined)englishFallbacks.add(trimmed);
            let translated=messages?.[trimmed];
            if(translated===undefined) {
                // Preserve decorative symbols while matching the actual UI label.
                const start=trimmed.search(/[A-Za-z0-9\u3400-\u9fff]/);
                if(start>0 && messages?.[trimmed.slice(start)]!==undefined) translated=trimmed.slice(0,start)+messages[trimmed.slice(start)];
            }
            if(translated===undefined&&CJK.test(trimmed))translated=compose(trimmed,messages);
            if(translated!==undefined) {result=source.slice(0,source.length-source.trimStart().length)+translated+source.slice(source.trimEnd().length);translatedCount++;}
            else if(CJK.test(trimmed)) fallbacks.add(trimmed);
        }
        if(params) result=result.replace(/\{([A-Za-z0-9_]+)\}/g,(match,key)=>Object.hasOwn(params,key)?String(params[key]):match);
        return result;
    }
    function scientificText(chinese, original) {
        const zh=String(chinese||'').trim(), en=String(original||'').trim();
        if(active==='zh-CN') return zh||en;
        if(active==='en-US') return en||t(zh);
        const translated=t(zh);
        return translated && translated!==zh ? translated : (en||zh);
    }
    function variable(v = {}) {
        v=v||{};
        const english=active==='en-US';
        const originalName=v.zh_name||v.long_name||v.name||'';
        const englishName=v.en_name||v.long_name_en||v.name||'';
        const translatedName=t(originalName);
        const display_name=english ? englishName : active==='zh-CN' ? originalName : translatedName!==originalName?translatedName:englishName;
        const originalMeaning=v.meaning||v.description||'';
        const englishMeaning=v.meaning_en||v.description_en||(!CJK.test(originalMeaning)?originalMeaning:'');
        const translatedMeaning=t(originalMeaning);
        const display_meaning=english ? englishMeaning : active==='zh-CN' ? originalMeaning : translatedMeaning!==originalMeaning?translatedMeaning:englishMeaning;
        const reference=v.reference ? {...v.reference} : null;
        if(reference && english) for(const key of ['label','source','note']) reference[key]=reference[key+'_en']||(!CJK.test(reference[key]||'')?reference[key]:'');
        else if(reference && active!=='zh-CN') for(const key of ['label','source','note']) if(reference[key]) {const translated=t(reference[key]);reference[key]=translated!==reference[key]?translated:reference[key+'_en']||translated;}
        return {...v,long_name:display_name,meaning:display_meaning,display_name,display_meaning,reference,
            comparison_name:scientificText(originalName,englishName),
            comparison_meaning:scientificText(originalMeaning,englishMeaning)};
    }
    const isPath=text=>/^(?:[A-Za-z]:[\\/]|\\\\|\/(?:[\w.-]+\/)+)[^\r\n]*$/.test(text.trim());
    function skip(element) {return !element || element.closest?.(excluded);}
    function translateNode(node) {
        const parent=node.parentElement;
        if(skip(parent)||isPath(node.nodeValue||'')) return;
        let item=textSources.get(node);
        if(!item || node.nodeValue!==item.output) item={source:node.nodeValue,output:node.nodeValue};
        const output=t(item.source);
        item.output=output;textSources.set(node,item);
        if(node.nodeValue!==output) node.nodeValue=output;
    }
    function translateAttributes(element) {
        // Keep graphical/model contents protected while exposing the static
        // accessibility name of our own result canvas in the selected locale.
        const resultCanvas=element?.matches?.('canvas.viz-canvas[role="img"]') && !element.closest?.('[data-i18n-skip]');
        if(skip(element) && !resultCanvas) return;
        let records=attributeSources.get(element);
        if(!records) {records=new Map();attributeSources.set(element,records);}
        for(const attr of ['title','placeholder','aria-label','alt']) {
            const current=element.getAttribute(attr);
            if(current===null||isPath(current)) continue;
            let item=records.get(attr);
            if(!item||current!==item.output) item={source:current,output:current};
            item.output=t(item.source);records.set(attr,item);
            if(current!==item.output) element.setAttribute(attr,item.output);
        }
    }
    function translateTree(root) {
        if(!root) return;
        if(root.nodeType===3) {translateNode(root);return;}
        if(root.nodeType===1) {translateAttributes(root);if(skip(root)) return;}
        if(typeof document==='undefined'||!document.createTreeWalker) return;
        const walker=document.createTreeWalker(root,1|4);
        let node;
        while((node=walker.nextNode())) {if(node.nodeType===3) translateNode(node);else translateAttributes(node);}
    }
    async function setLocale(locale) {
        await ready;
        if(!packs.has(locale)) throw new Error('Unknown locale. Import a language pack first.');
        if(typeof document!=='undefined') {
            const response=await fetch('/api/system/language',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({locale,packs:[...packs.values()].filter(p=>!['zh-CN','en-US'].includes(p.locale))})});
            if(!response.ok) throw new Error('Could not save language preferences.');
        }
        active=locale;fallbacks.clear();englishFallbacks.clear();translatedCount=0;save(LOCALE_KEY,active);
        if(typeof document!=='undefined') {
            document.documentElement.lang=active;
            translateTree(document.documentElement);
            document.dispatchEvent(new CustomEvent('studio-language-changed',{detail:{locale:active}}));
        }
        return active;
    }
    function closeDialog() {
        if(!dialog) return;
        if(dialog.open&&dialog.close) dialog.close();
        dialog.remove();dialog=null;
        returnFocus?.focus?.();returnFocus=null;
    }
    function openDialog() {
        if(typeof document==='undefined') return;
        if(dialog) {dialog.focus();return;}
        returnFocus=document.activeElement;
        dialog=document.createElement('dialog');dialog.className='studio-language-dialog';
        dialog.setAttribute('data-i18n-skip','');dialog.setAttribute('aria-labelledby','studio-language-title');
        const node=(tag,text,cls)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;};
        const heading=node('h2',t('界面语言'));heading.id='studio-language-title';
        const label=node('label',t('选择界面语言'));label.htmlFor='studio-language-select';
        const select=node('select');select.id='studio-language-select';
        const fill=()=>{select.replaceChildren();for(const pack of packs.values()){const option=node('option',pack.name);option.value=pack.locale;select.append(option);}select.value=active;};
        fill();
        const preview=node('div',undefined,'studio-language-preview');preview.setAttribute('aria-live','polite');
        const previewTitle=node('b',t('预览'));
        const sample=node('p');preview.append(previewTitle,sample);
        const renderPreview=()=>{
            const previous=active;active=select.value;
            sample.textContent=[t('仪表盘'),t('输入数据'),t('运行模型'),t('结果与率定')].join(' · ');
            active=previous;
        };
        select.addEventListener('change',renderPreview);renderPreview();
        const importLabel=node('label',t('导入语言包（JSON）'));importLabel.htmlFor='studio-language-import';
        const file=node('input');file.type='file';file.accept='.json,application/json';file.id='studio-language-import';
        file.hidden=true;
        const choose=node('button',t('选择语言包文件'),'btn');choose.type='button';choose.addEventListener('click',()=>file.click());
        const filename=node('span',t('尚未选择文件'),'studio-language-help');
        const help=node('p',t('语言包必须是纯文本 JSON，最大 256 KiB。'), 'studio-language-help');
        const fallbackHelp=node('p',t('导入语言缺少的词条将使用英文；仍未知的文本保留原文。'),'studio-language-help');
        const schema=node('code','{"locale":"fr-FR","name":"Français","messages":{"取消":"Annuler"}}');
        const download=node('button',t('下载语言包模板'),'btn');download.type='button';
        download.addEventListener('click',()=>{
            const template={locale:'fr-FR',name:'Français',messages:{'取消':'Annuler','应用':'Appliquer','仪表盘':'Tableau de bord'}};
            const url=URL.createObjectURL(new Blob([JSON.stringify(template,null,2)],{type:'application/json;charset=utf-8'}));
            const anchor=node('a');anchor.href=url;anchor.download='3dwet-language-template.json';anchor.click();
            setTimeout(()=>URL.revokeObjectURL(url),1000);
        });
        const error=node('p',undefined,'studio-language-error');error.setAttribute('role','alert');
        file.addEventListener('change',async()=>{
            try {
                const selected=file.files?.[0];if(!selected)return;
                filename.textContent=selected.name;
                if(selected.size>MAX_BYTES)throw new Error(t('语言包超过 256 KiB。'));
                const pack=importPack(await selected.text());fill();select.value=pack.locale;renderPreview();
                error.textContent=t('语言包已导入，点击应用启用。');
            } catch(e) {error.textContent=e.message;}
        });
        const actions=node('div',undefined,'studio-language-actions');
        const cancel=node('button',t('取消'),'btn');cancel.type='button';cancel.addEventListener('click',closeDialog);
        const apply=node('button',t('应用'),'btn btn-primary');apply.type='button';
        apply.addEventListener('click',async()=>{apply.disabled=true;try{await setLocale(select.value);closeDialog();}catch(e){error.textContent=e.message;apply.disabled=false;}});
        actions.append(cancel,apply);dialog.append(heading,label,select,preview,importLabel,file,choose,filename,help,fallbackHelp,schema,download,error,actions);
        dialog.addEventListener('cancel',event=>{event.preventDefault();closeDialog();});
        dialog.addEventListener('keydown',event=>{
            if(event.key==='Escape') {event.preventDefault();closeDialog();return;}
            if(event.key==='Tab') {
                const focusables=[...dialog.querySelectorAll('button,select,input')].filter(el=>!el.disabled&&!el.hidden);
                const first=focusables[0],last=focusables.at(-1);
                if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
                else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
            }
        });
        document.body.append(dialog);
        if(dialog.showModal)dialog.showModal();else {dialog.setAttribute('open','');dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');}
        select.focus();
    }
    const ready=(async()=>{
        try {const response=await fetch('/static/i18n/en.json?v=20261027-static-bathymetry-preview');if(!response.ok)throw new Error('English catalog unavailable');const pack=validatePack(await response.json(),true);packs.set('en-US',pack);}
        catch(e){console.warn('Studio language catalog:',e.message);}
        if(typeof document!=='undefined') {
            try {
                const response=await fetch('/api/system/language');
                if(response.ok) {
                    const saved=await response.json();
                    for(const pack of (saved.packs||[]).slice(0,16)) {const valid=validatePack(pack);packs.set(valid.locale,valid);}
                    if(packs.has(saved.locale))active=saved.locale;
                }
            } catch(e) {console.warn('Studio language preferences:',e.message);}
        }
    })();
    window.StudioI18n={t,locale:()=>active,setLocale,openDialog,variable,scientificText,importPack,
        languages:()=>[...packs.values()].map(({locale,name})=>({locale,name})),
        stats:()=>({locale:active,translated:translatedCount,fallbackCount:fallbacks.size,fallbacks:[...fallbacks].sort(),englishFallbackCount:englishFallbacks.size,englishFallbacks:[...englishFallbacks].sort()}),
        translate:()=>typeof document!=='undefined'&&translateTree(document.documentElement),ready};
    async function init() {
        await ready;
        await setLocale(active);
        observer=new MutationObserver(records=>{
            for(const record of records) {
                if(record.type==='characterData')translateNode(record.target);
                else if(record.type==='attributes')translateAttributes(record.target);
                else for(const node of record.addedNodes)translateTree(node);
            }
        });
        observer.observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['title','placeholder','aria-label','alt']});
    }
    if(typeof document!=='undefined') {
        if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
    }
})();
