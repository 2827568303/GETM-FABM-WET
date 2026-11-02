// Model calendar presentation: year + day of year (DOY), never astronomical JD.
// Naive model times are UTC calendar coordinates; explicit offsets normalize to UTC.
const ModelDates = (() => {
    const DAY = 86400000;
    const pad = (n, length = 2) => String(n).padStart(length, '0');
    const leap = year => year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
    function utc(year, month = 1, day = 1) {
        const date = new Date(0);
        date.setUTCFullYear(year, month - 1, day);
        date.setUTCHours(0, 0, 0, 0);
        return date;
    }
    function parse(value) {
        if (typeof value !== 'string') return null;
        let text = value.trim();
        // Existing imported data may use compact or US-style calendar dates.
        text = text.replace(/^(\d{4})(\d{2})(\d{2})$/, '$1-$2-$3')
            .replace(/^(\d{1,2})\/(\d{1,2})\/(\d{4})(.*)$/, '$3-$1-$2$4');
        const ordinal = /^(\d{4})-(?:DOY)?(\d{3})(.*)$/i.exec(text);
        const calendar = /^(\d{4})[-/](\d{1,2})[-/](\d{1,2})(.*)$/.exec(text);
        if (!ordinal && !calendar) return null;
        const year = Number((ordinal || calendar)[1]);
        if (year < 1 || year > 9999) return null;
        let date, tail;
        if (ordinal) {
            const day = Number(ordinal[2]);
            if (day < 1 || day > (leap(year) ? 366 : 365)) return null;
            date = utc(year);
            date.setUTCDate(day);
            tail = ordinal[3];
        } else {
            const month = Number(calendar[2]), day = Number(calendar[3]);
            date = utc(year, month, day);
            if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return null;
            tail = calendar[4];
        }
        let hasTime = false, fraction = '';
        if (tail) {
            const time = /^(?:T|\s+)(\d{2}):(\d{2})(?::(\d{2})(\.\d{1,6})?)?(Z|[+-]\d{2}:?\d{2})?$/.exec(tail);
            if (!time) return null;
            const hour = +time[1], minute = +time[2], second = +(time[3] || 0);
            if (hour > 23 || minute > 59 || second > 59) return null;
            hasTime = true;
            fraction = time[4] || '';
            // Date stores milliseconds. Keep the original subsecond text and
            // truncate its millisecond projection so .999999 never rolls the
            // calendar to the next second while retaining the old fraction.
            date.setUTCHours(hour, minute, second, Number(fraction.slice(1, 4).padEnd(3, '0')));
            const zone = time[5];
            if (zone && zone !== 'Z') {
                const parts = /^([+-])(\d{2}):?(\d{2})$/.exec(zone);
                if (+parts[2] > 23 || +parts[3] > 59) return null;
                date = new Date(date.getTime() - (parts[1] === '+' ? 1 : -1) * (+parts[2] * 60 + +parts[3]) * 60000);
            }
        }
        if (date.getUTCFullYear() < 1 || date.getUTCFullYear() > 9999) return null;
        return {date, hasTime, fraction};
    }
    function clock(parsed) {
        const d = parsed.date;
        return `${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())}${parsed.fraction}`;
    }
    function format(value, options = {}) {
        const parsed = parse(value);
        if (!parsed) return value;
        const year = parsed.date.getUTCFullYear();
        const day = Math.floor((parsed.date.getTime() - utc(year).getTime()) / DAY) + 1;
        return `${pad(year, 4)}-DOY${pad(day, 3)}${options.time || parsed.hasTime ? ' ' + clock(parsed) : ''}`;
    }
    function toIso(value, options = {}) {
        const parsed = parse(value);
        if (!parsed) throw new Error('请输入有效的年份与年内儒略日：YYYY-DOYDDD HH:mm:ss（平年001–365，闰年001–366）');
        const d = parsed.date;
        return `${pad(d.getUTCFullYear(), 4)}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}${options.time || parsed.hasTime ? ' ' + clock(parsed) : ''}`;
    }
    function formatText(value) {
        if (typeof value !== 'string') return value;
        return value.replace(/\b\d{4}[-/]\d{2}[-/]\d{2}(?:(?:T| +)\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?(?:Z|[+-]\d{2}:?\d{2})?)?\b/g, match => format(match));
    }
    function chartLabels(values) { return (values || []).map(value => format(value)); }
    function plotlyAxis(values) {
        const labels = chartLabels(values);
        const parsed = values.map(parse);
        if (!parsed.length || parsed.some(value => !value)) return {x: labels, labels, axis: {type: 'category'}};
        const x = parsed.map(value => value.date.getTime());
        const step = Math.max(1, Math.ceil((x.length - 1) / 10));
        const indices = x.map((_, i) => i).filter(i => i % step === 0 || i === x.length - 1);
        return {x, labels, axis: {type: 'linear', tickmode: 'array', tickvals: indices.map(i => x[i]), ticktext: indices.map(i => labels[i])}};
    }
    return {parse, format, toIso, formatText, chartLabels, plotlyAxis};
})();
