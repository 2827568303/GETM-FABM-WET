const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');

function compatibilityFunction() {
    const match = source.match(/function ensureEcologyNavigationItem\(\) \{[\s\S]*?\n\}/);
    assert.ok(match, 'app.js should define the legacy-template ecology navigation fallback');
    return match[0];
}

function navigationBinding() {
    const match = source.match(/document\.querySelectorAll\('\.nav-item'\)\.forEach\(item => \{\s*item\.addEventListener\('click', \(\) => navigate\(item\.dataset\.page\)\);\s*\}\);/);
    assert.ok(match, 'app.js should bind each navigation item through navigate(page)');
    return match[0];
}

function runFallback({ existing = false, hasModelGroup = true } = {}) {
    const calls = { created: 0, elements: [], appended: [], inserted: [], navigated: [], icons: [] };
    const ecology = existing ? {
        dataset: { page: 'ecology' },
        addEventListener(type, handler) { (this.handlers ||= {})[type] = handler; }
    } : null;
    const modules = { nextSibling: null };
    const parameters = { dataset: { page: 'parameters' } };
    const group = {
        querySelector(selector) {
            if (selector === '[data-page="parameters"]') return parameters;
            if (selector === '[data-page="modules"]') return modules;
            return null;
        },
        appendChild(item) { calls.appended.push(item); },
        insertBefore(item, before) { calls.inserted.push({ item, before }); }
    };
    const document = {
        querySelector(selector) {
            if (selector === '.nav-item[data-page="ecology"]') return ecology;
            if (selector === '[data-group-items="model"]') return hasModelGroup ? group : null;
            return null;
        },
        createElement(tag) {
            calls.created++;
            const element = {
                tagName: tag,
                dataset: {},
                children: [],
                attributes: {},
                setAttribute(name, value) { this.attributes[name] = value; },
                replaceChildren(...children) { this.children = children; },
                appendChild(child) { this.children.push(child); },
                addEventListener(type, handler) { (this.handlers ||= {})[type] = handler; }
            };
            calls.elements.push(element);
            return element;
        },
        createTextNode(text) { return { textContent: text }; },
        querySelectorAll(selector) {
            if (selector !== '.nav-item') return [];
            return existing ? [ecology] : calls.inserted.map(entry => entry.item);
        }
    };
    vm.runInNewContext(`${compatibilityFunction()}\nensureEcologyNavigationItem();\n${navigationBinding()}`, {
        document,
        StudioIcons: { node(name) { const icon = { name }; calls.icons.push(icon); return icon; } },
        navigate(page) { calls.navigated.push(page); }
    });
    return calls;
}

test('legacy template gets one ecology nav item in the model group before normal click binding', () => {
    const calls = runFallback();
    assert.equal(calls.created, 2, 'create one button and its icon');
    assert.equal(calls.inserted.length, 1, 'insert the fallback before model parameter navigation');
    assert.equal(calls.inserted[0].before.dataset.page, 'parameters');
    assert.equal(calls.appended.length, 0);
    const [button, icon] = calls.elements;
    assert.equal(button.type, 'button');
    assert.equal(button.className, 'nav-item getm-case-only');
    assert.equal(button.dataset.page, 'ecology');
    assert.equal(icon.children[0].name, 'foodweb', 'the fallback uses the shared technical food-web icon');
    assert.equal(icon.attributes['aria-hidden'], 'true');
    assert.equal(button.children[1].textContent, '生态网络与食物网');
    assert.equal(typeof button.handlers.click, 'function', 'the injected button receives the app navigation handler');
    button.handlers.click();
    assert.deepEqual(calls.navigated, ['ecology'], 'clicking the fallback invokes navigate("ecology") once');
    assert.ok(source.indexOf('ensureEcologyNavigationItem();') < source.indexOf("document.querySelectorAll('.nav-item').forEach(item =>"),
        'create the fallback before existing app.js click handlers are attached');
    assert.match(source, /item\.dataset\.page\s*=\s*'ecology'/);
    const template = fs.readFileSync('3DWET/app/templates/index.html', 'utf8');
    assert.ok(template.indexOf('studio_icons.js?v=5') < template.indexOf('app.js?v='),
        'the current template loads the shared icon API before the fallback executes');
});

test('template with ecology navigation does not receive a duplicate item', () => {
    const calls = runFallback({ existing: true });
    assert.equal(calls.created, 0);
    assert.equal(calls.inserted.length + calls.appended.length, 0);
});

test('fallback safely does nothing if the template has no model navigation group', () => {
    const calls = runFallback({ hasModelGroup: false });
    assert.equal(calls.created, 0);
    assert.equal(calls.inserted.length + calls.appended.length, 0);
});
