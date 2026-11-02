// Shared scalar mapping for Canvas and Plotly. Settings are scoped to a case and
// variable, while ranges and labels always retain the original numerical values.
(function (root) {
    'use strict';
    const palettes = {
        lake: [[117,227,215],[88,210,226],[57,181,231],[43,145,223],[35,107,210],[23,63,189]],
        cividis: [[0,34,78],[8,52,111],[53,69,108],[79,87,108],[102,105,112],[125,124,120],[148,143,119],[172,164,113],[199,186,99],[227,210,72],[254,232,56]],
        viridis: [[68,1,84],[72,36,117],[65,68,135],[53,95,141],[42,120,142],[33,145,140],[34,168,132],[68,191,112],[122,209,81],[189,223,38],[253,231,37]],
        blueRed: [[33,102,172],[103,169,207],[209,229,240],[247,247,247],[253,219,199],[239,138,98],[178,24,43]]
    };
    const settings = new Map();
    const storageKey = '3dwet.scientific-style.v2';
    const storageVersion = 2;
    const finite = value => typeof value === 'number' && Number.isFinite(value);
    const validRange = (min, max) => finite(min) && finite(max) && min <= max;
    const defaults = () => ({ palette: 'lake', mode: 'auto', min: null, max: null,
        stops:[[0,'#75e3d7'],[1,'#173fbd']],reverse:false,mapping:'continuous',classes:5,nanColor:'#c9cbd0' });
    const clone=value=>({...value,stops:value.stops.map(stop=>[...stop])});
    const hex=value=>typeof value==='string' && /^#[0-9a-f]{6}$/i.test(value);
    const fields=Object.keys(defaults());
    function validate(value) {
        if(value.palette!=='custom' && !Object.prototype.hasOwnProperty.call(palettes,value.palette))throw new RangeError('Unknown palette');
        if(!['auto','locked','custom'].includes(value.mode))throw new RangeError('Unknown range mode');
        const empty=value.min===null && value.max===null;
        if(value.mode==='custom' && (!validRange(value.min,value.max) || value.min===value.max))throw new RangeError('Custom range requires finite min < max');
        if(value.mode==='locked' && !empty && !validRange(value.min,value.max))throw new RangeError('Invalid locked range');
        if(typeof value.reverse!=='boolean')throw new RangeError('Reverse must be boolean');
        if(!['continuous','discrete'].includes(value.mapping))throw new RangeError('Unknown color mapping');
        if(!Number.isInteger(value.classes) || value.classes<2 || value.classes>20)throw new RangeError('Classes must be an integer from 2 to 20');
        if(!hex(value.nanColor))throw new RangeError('Missing color requires #RRGGBB');
        const nodes=value.stops;
        if(!Array.isArray(nodes) || nodes.length<2 || nodes.length>32 || nodes.some((node,i)=>
            !Array.isArray(node) || node.length!==2 || !finite(node[0]) || node[0]<0 || node[0]>1 || !hex(node[1]) ||
            (i>0 && node[0]<=nodes[i-1][0])) || nodes[0][0]!==0 || nodes.at(-1)[0]!==1)
            throw new RangeError('Color nodes require 2..32 ordered positions from 0 to 1 and #RRGGBB colors');
        return clone(value);
    }
    function configuration(value,complete=false) {
        if(!value || typeof value!=='object' || Array.isArray(value))throw new TypeError('Invalid color configuration');
        if(complete && fields.some(key=>!Object.prototype.hasOwnProperty.call(value,key)))throw new TypeError('Incomplete color configuration');
        const next=defaults();
        for(const key of fields)if(Object.prototype.hasOwnProperty.call(value,key))next[key]=value[key];
        const result=validate(next);
        if(result.mode==='auto'){result.min=null;result.max=null;}
        return result;
    }
    function persist() {
        try {
            const storage = root.localStorage;
            if (!storage) return;
            const entries = [];
            settings.forEach((variables, caseKey) => variables.forEach((value, variable) => entries.push({ caseKey, variable, ...value })));
            storage.setItem(storageKey, JSON.stringify({ version: storageVersion, entries }));
        } catch (_) {
            // Disabled/private storage and quota exhaustion must not disable
            // scientific display state in the current app session.
        }
    }
    function restore() {
        try {
            const storage = root.localStorage;
            if (!storage) return;
            const raw=storage.getItem(storageKey);
            const saved = JSON.parse(raw ?? storage.getItem('3dwet.scientific-style.v1'));
            if (!saved || ![1,storageVersion].includes(saved.version) || !Array.isArray(saved.entries)) return;
            saved.entries.forEach(entry => {
                if (!entry || typeof entry.caseKey !== 'string' || typeof entry.variable !== 'string')return;
                try {
                    const value=saved.version===1 ? {palette:entry.palette,mode:entry.mode,min:entry.min,max:entry.max} : entry;
                    bucket(entry.caseKey).set(entry.variable,configuration(value,saved.version!==1));
                } catch (_) { /* A malformed record must not discard other valid variables. */ }
            });
        } catch (_) {
            // Corrupt JSON or unavailable storage leaves the default settings.
        }
    }
    function bucket(caseKey) {
        const key = String(caseKey ?? '');
        if (!settings.has(key)) settings.set(key, new Map());
        return settings.get(key);
    }
    function get(caseKey, variable) {
        return clone(bucket(caseKey).get(String(variable ?? '')) || defaults());
    }
    function set(caseKey, variable, patch) {
        if (!patch || typeof patch !== 'object') throw new TypeError('Invalid range settings');
        const previous = get(caseKey, variable);
        const next = { ...previous };
        for (const key of fields) {
            if (Object.prototype.hasOwnProperty.call(patch, key)) next[key] = patch[key];
        }
        validate(next);
        if (next.mode !== 'custom' && previous.mode !== next.mode) {
            next.min = null;
            next.max = null;
        }
        // The locked range is established by resolve's first valid frame, not
        // by arbitrary patch limits left over from another mode.
        if (next.mode === 'auto') { next.min = null; next.max = null; }
        bucket(caseKey).set(String(variable ?? ''), clone(next));
        persist();
        return clone(next);
    }
    function nodes(config) {
        let result;
        if(config.palette==='custom' && Array.isArray(config.stops))result=config.stops.map(([position,value])=>[position,[1,3,5].map(i=>parseInt(value.slice(i,i+2),16))]);
        else {
            const colors=Object.prototype.hasOwnProperty.call(palettes,config.palette) ? palettes[config.palette] : palettes.lake;
            result=colors.map((value,i)=>[i/(colors.length-1),value]);
        }
        return config.reverse ? result.map(([position,value])=>[1-position,value]).reverse() : result;
    }
    const rgb=channels=>`rgb(${channels.join(',')})`;
    function interpolate(value,points) {
        let high=points.findIndex(point=>point[0]>=value);
        if(high<=0)return rgb(points[high<0?points.length-1:0][1]);
        const [lowPosition,low]=points[high-1],[highPosition,upper]=points[high];
        const fraction=(value-lowPosition)/(highPosition-lowPosition);
        return rgb(low.map((v,channel)=>Math.round(v+(upper[channel]-v)*fraction)));
    }
    function mapper(config = 'lake') {
        config=typeof config==='string'?{palette:config}:config || defaults();
        const points=nodes(config),missing=config.nanColor || '#c9cbd0';
        const classes=config.classes,discrete=config.mapping==='discrete';
        return t=>{
            if(!finite(t))return missing;
            let value=Math.max(0,Math.min(1,t));
            if(discrete)value=(Math.min(classes-1,Math.floor(value*classes))+.5)/classes;
            return interpolate(value,points);
        };
    }
    function color(t,config='lake'){return mapper(config)(t);}
    function colorscale(config) {
        const points=nodes(config);
        if(config.mapping!=='discrete')return points.map(([position,channels])=>[position,rgb(channels)]);
        return Array.from({length:config.classes},(_,i)=>{
            const value=interpolate((i+.5)/config.classes,points);
            return [[i/config.classes,value],[(i+1)/config.classes,value]];
        }).flat();
    }
    function exportConfig(caseKey,variable){return {version:storageVersion,style:get(caseKey,variable)};}
    function importConfig(caseKey,variable,payload){
        if(!payload || payload.version!==storageVersion)throw new RangeError('Unsupported color configuration version');
        const value=configuration(payload.style,true);
        bucket(caseKey).set(String(variable ?? ''),value);persist();return clone(value);
    }
    function ticks(min, max, count = 5) {
        if (!validRange(min, max)) return { values: [], labels: [] };
        if (min === max) return { values: [min], labels: [String(Object.is(min, -0) ? 0 : min)] };
        const size = Math.max(2, Math.min(20, Math.round(finite(count) ? count : 5)));
        const values = [];
        for (let index = 0; index < size; index++) {
            // Weighted interpolation also handles ranges whose span overflows.
            const fraction = index / (size - 1);
            const value = index === 0 ? min : index === size - 1 ? max : min * (1 - fraction) + max * fraction;
            if (values.length === 0 || value !== values[values.length - 1]) values.push(value);
        }
        const magnitude = Math.max(Math.abs(min), Math.abs(max));
        const step = Math.abs(max / (size - 1) - min / (size - 1));
        const scientific = magnitude >= 1e7 || magnitude < 1e-4;
        let labels;
        for (let precision = 0; precision <= 17; precision++) {
            labels = values.map(value => {
                if (scientific) return value.toExponential(precision).replace(/\.0+(?=e)/, '');
                const digits = Math.max(0, Math.min(100, -Math.floor(Math.log10(step || 1)) + precision));
                return value.toFixed(digits).replace(/(\.\d*?)0+$/, '$1').replace(/\.$/, '').replace(/^-0$/, '0');
            });
            // Distinct labels alone can still round a small nonzero endpoint
            // to zero when another endpoint determines the overall precision.
            if (new Set(labels).size === values.length && values.every((value, index) => value === 0 || Number(labels[index]) !== 0)) return { values, labels };
        }
        return { values, labels: values.map(String) };
    }
    function legendTicks(min,max,width=200,fontSize=10) {
        width=Number.isFinite(width)&&width>0?width:200;
        for(let count=5;count>=2;count--){
            const marks=ticks(min,max,count);
            const labelWidth=Math.max(0,...marks.labels.map(label=>label.length))*fontSize*.62+12;
            if(marks.labels.length*labelWidth<=width || count===2)return marks;
        }
    }
    function resolve({ caseKey, variable, min, max }) {
        let current = get(caseKey, variable);
        const noData = !validRange(min, max);
        if (!noData && current.mode === 'locked' && !validRange(current.min, current.max)) {
            current.min = min;
            current.max = max;
            bucket(caseKey).set(String(variable ?? ''), current);
            persist();
        }
        if (!noData && current.mode !== 'auto') { min = current.min; max = current.max; }
        if (noData) { min = null; max = null; }
        const marks = ticks(min, max);
        return { ...clone(current), min, max,
            colorscale: colorscale(current),
            tickvals: marks.values, ticktext: marks.labels, noData };
    }
    restore();
    root.ScientificStyle = { get, set, resolve, color, mapper, colorscale, validateConfig:configuration,
        exportConfig, importConfig, ticks, legendTicks };
})(typeof window !== 'undefined' ? window : globalThis);
