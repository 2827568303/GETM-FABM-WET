(function(root) {
    'use strict';
    const isChinese = () => !root.StudioI18n || root.StudioI18n.locale().startsWith('zh');
    const tr = (zh,en) => { const result=root.StudioI18n?.t(zh); return isChinese()?zh:(result && result!==zh?result:en); };
    const localVariable = v => root.StudioI18n?.variable(v || {}) || Object.assign({},v,{display_name:v?.zh_name || v?.long_name,display_meaning:v?.meaning});
    const finite = v => typeof v === 'number' && Number.isFinite(v);
    const number = v => finite(v) ? Number(v.toPrecision(5)).toLocaleString(root.StudioI18n?.locale() || 'zh-CN',{maximumFractionDigits:6}) : '—';
    const escape = v => String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    function formatReference(r) {
        if (!r || r.kind === 'unset') return tr('未设置通用数值参考','No universal numeric reference set');
        let value = finite(r.lower) && finite(r.upper) ? `${number(r.lower)} – ${number(r.upper)}` :
            finite(r.lower) ? `≥ ${number(r.lower)}` : finite(r.upper) ? `≤ ${number(r.upper)}` : number(r.value);
        const label=(!isChinese() && r.label_en) || r.label || ({standard:'水质标准参考',initial:'模型初始值',custom:'用户设定参考'}[r.kind] || '参考值');
        return `${(!isChinese() && r.label_en) || tr(label, r.kind==='standard'?'Water quality reference':r.kind==='initial'?'Initial model baseline':'User reference')}: ${value} ${r.unit || r.units || ''}`;
    }
    function valuesOf(value, out=[]) {
        if (Array.isArray(value)) value.forEach(v=>valuesOf(v,out));
        else if (finite(value)) out.push(value);
        return out;
    }
    function assess(data, reference) {
        const values=valuesOf(data), r=reference || {kind:'unset'};
        if (!values.length) return {status:'empty',count:0};
        const mean=values.reduce((a,b)=>a+b,0)/values.length;
        if (r.kind==='unset') return {status:'unset',count:values.length,mean};
        if (r.kind==='initial' || (!finite(r.lower) && !finite(r.upper)))
            return {status:'reference',count:values.length,mean,delta:finite(r.value)?mean-r.value:null};
        const outside=values.filter(v=>(finite(r.lower)&&v<r.lower)||(finite(r.upper)&&v>r.upper)).length;
        return {status:outside?'warning':'ok',count:values.length,mean,outside,percent:100*outside/values.length};
    }
    const registry=new Map(), latest=new Map();
    const ids=['viz2d-var','viz3d-iso-var','viz3d-var','viz3d-avg-var','vheat-var','ts-var','map-field-var','cal-var-select'];
    function referenceText(name) { return formatReference(registry.get(name)?.reference); }
    function valueText(name, value) {
        const v=localVariable(registry.get(name)), r=v?.reference;
        const report=assess([value],r);
        return `${v?.display_name || name}: ${number(value)} ${v?.units || ''} · ${formatReference(r)}`+
            (report.status==='warning'?' · '+tr('超出参考范围','Outside reference range'):report.status==='reference'&&finite(report.delta)?` · ${escape(tr('与参考相差','Difference from reference'))} ${number(report.delta)}`:'');
    }
    function show(id) {
        const select=document.getElementById(id); if(!select) return;
        let card=document.getElementById(id+'-guide');
        if(!card) {
            card=document.createElement('section');card.id=id+'-guide';card.className='results-variable-card';
            const controls=select.closest('.viz-controls') || select.closest('.form-row') || select.closest('.form-group');
            (controls || select).insertAdjacentElement('afterend',card);
        }
        const native=registry.get(select.value);
        const v=native && localVariable(native);
        if(!v) {card.hidden=true;return;} card.hidden=false;card.dataset.i18nSkip='true';
        const r=v.reference || {kind:'unset'}, sample=latest.get(id);
        const a=sample?.name===select.value?assess(sample.data,r):null;
        let status=tr('选择位置可查看该值与参考的关系。','Select a position to compare its value with the reference.');
        if(a?.status==='empty') status=tr('当前切片没有有效数值，无法比较。','This slice has no valid values to compare.');
        else if(a?.status==='unset') status=isChinese()?`当前有效值 ${a.count} 个，均值 ${number(a.mean)}；该变量没有通用“正常值”，请设置本湖参考。`:`${a.count} valid values · mean ${number(a.mean)}. No universal normal value; set a reference for this lake.`;
        else if(a?.status==='reference') status=isChinese()?`当前均值 ${number(a.mean)}；与参考相差 ${number(a.delta)} ${v.units || ''}。变化不等同于异常。`:`Mean ${number(a.mean)} · difference from reference ${number(a.delta)} ${v.units || ''}. Change does not imply an abnormal condition.`;
        else if(a) status=isChinese()?`当前有效值 ${a.count} 个 · 均值 ${number(a.mean)} · 超参考范围 ${a.outside} 个（${number(a.percent)}%）；属于当前显示范围的筛查。`:`${a.count} valid values · mean ${number(a.mean)} · ${a.outside} outside range (${number(a.percent)}%). Screening covers the displayed sample only.`;
        card.innerHTML=`<div class="variable-guide-heading"><strong>${escape(v.comparison_name || v.display_name)}</strong><code>${escape(v.name)}</code><span>${escape(v.units || tr('无量纲','Dimensionless'))}</span></div>
            <p>${escape(v.comparison_meaning || v.display_meaning || v.long_name_en || '')}</p>
            <div class="reference-strip"><b>${escape(formatReference(r))}</b><span>${escape(r.source || '')}</span></div>
            <p class="reference-note">${escape(r.note || tr('参考值用于辅助理解，需结合本湖实测资料及模拟条件。','Interpret references together with observations and model conditions.'))}</p>
            ${/^https?:\/\//i.test(r.source_url || "")?`<a href="${escape(r.source_url)}" target="_blank" rel="noopener">${escape(tr('查看参考依据','View reference source'))} ${StudioIcons.svg('external')}</a>`:''}
            <div class="reference-status" data-status="${escape(a?.status || '')}">${escape(status)}</div>
            <details><summary>${escape(tr('设置本案例参考值 / 范围','Set case reference value / range'))}</summary>
            <form class="reference-form"><label>${escape(tr('参考下限','Lower bound'))}<input name="lower" type="number" step="any" value="${finite(r.lower)?r.lower:''}" placeholder="${escape(tr('可留空','Optional'))}"></label>
            <label>${escape(tr('参考上限','Upper bound'))}<input name="upper" type="number" step="any" value="${finite(r.upper)?r.upper:''}" placeholder="${escape(tr('可留空','Optional'))}"></label>
            <label>${escape(tr('单值参考','Reference value'))}<input name="value" type="number" step="any" value="${finite(r.value)?r.value:''}" placeholder="${escape(tr('如本湖实测均值','e.g. observed lake mean'))}"></label>
            <button class="btn btn-sm" type="submit">${escape(tr('保存到当前案例','Save to this case'))}</button><button class="btn btn-sm" type="button" data-reset>${escape(tr('恢复默认参考','Restore default reference'))}</button></form></details>`;
        const form=card.querySelector('form');
        async function save(reset=false) {
            const data={name:v.name,units:v.units,reset,label:'用户设定参考（非水质标准）'};
            ['lower','upper','value'].forEach(k=>{const raw=form.elements[k].value.trim();data[k]=raw===''?null:Number(raw);});
            const response=await fetch('/api/results/reference',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
            const body=await response.json();
            if(!response.ok || body.error) {root.toast?.(body.error || tr('参考保存失败','Could not save the reference'),'error');return;}
            registry.set(v.name,body.variable);ids.forEach(show); root.toast?.(tr('本案例参考已更新','Case reference updated'),'success');
        }
        form.addEventListener('submit',e=>{e.preventDefault();save().catch(e=>root.toast?.(String(e),'error'));});
        form.querySelector('[data-reset]').addEventListener('click',()=>save(true).catch(e=>root.toast?.(String(e),'error')));
    }
    function setVariables(items) {
        registry.clear(); latest.clear();items.forEach(v=>registry.set(v.name,v));
        if(typeof document==='undefined') return;
        ids.forEach(id=>{const el=document.getElementById(id);if(!el)return;
            if(!el.dataset.variableGuide){el.dataset.variableGuide='true';el.addEventListener('change',()=>show(id));} show(id);});
    }
    function updateValues(id, data) {
        const select=typeof document!=='undefined'&&document.getElementById(id); if(!select) return;
        latest.set(id,{name:data.var_name || select.value,data:data.data || []}); show(id);
    }
    if(typeof document!=='undefined') document.addEventListener('studio-language-changed',()=>ids.forEach(show));
    const api={formatReference,assess,setVariables,updateValues,refresh:show,referenceText,valueText};
    root.VariableGuide=api;
    if(typeof module!=='undefined') module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
