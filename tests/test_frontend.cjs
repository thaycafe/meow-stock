const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const base = fs.readFileSync('app/templates/base.html', 'utf8');
const script = base.match(/<script>\s*((?:\/\/.*\s*)*const foldCase[\s\S]*?)<\/script>/)[1];

function setup(storage = {}) {
  const stores = {}, components = {}, requests = [], sources = new Set();
  const document = {
    body: { appendChild(source) { sources.add(source); } },
    createElement() {
      return {
        listeners: new Map(),
        addEventListener(name, fn) { this.listeners.set(name, fn); },
        removeEventListener(name) { this.listeners.delete(name); },
        remove() { sources.delete(this); },
        complete(detail) { this.listeners.get('htmx:afterRequest')?.({ target: this, detail }); },
      };
    },
    addEventListener(name, fn) { fn(); },
  };
  const context = vm.createContext({
    document, localStorage: {
      getItem() { return null; }, setItem() {}, ...storage,
    },
    Alpine: {
      store(name, value) { stores[name] = value; },
      data(name, factory) { components[name] = factory; },
    },
    htmx: { ajax(verb, path, options) {
      return new Promise((resolve, reject) => requests.push({ options, resolve, reject }));
    } },
  });
  vm.runInContext(script, context);
  return { stores, components, requests, sources, context };
}

test('concurrent requests to the same endpoint complete independently and clean up', async () => {
  const env = setup();
  const first = vm.runInContext("htmxRequest('POST', '/stock/items', {})", env.context);
  const second = vm.runInContext("htmxRequest('POST', '/stock/items', {})", env.context);
  let firstDone = false;
  first.then(() => { firstDone = true; });
  const result = { successful: true };
  env.requests[1].options.source.complete(result);
  assert.equal(await second, result);
  assert.equal(firstDone, false);
  assert.equal(env.sources.size, 1);
  env.requests[0].reject(new Error('network'));
  assert.equal((await first).successful, false);
  assert.equal(env.sources.size, 0);
});

test('search keys use the same case folding as the server', () => {
  const { context } = setup();
  const normalize = s => vm.runInContext('normalize', context)(s);
  assert.equal(normalize('  STRAẞE  Açúcar '), 'strasse acucar');
  assert.equal(normalize('ΟΔΟΣ ſ ı'), 'οδοσ s ı');
});

test('cart tolerates unavailable, malformed, and non-array storage', () => {
  for (const getItem of [
    () => { throw new Error('denied'); },
    ...['{', 'null', '{}', '"text"', '7'].map(value => () => value),
  ]) {
    const cart = setup({ getItem, setItem() { throw new Error('quota'); } }).stores.cart;
    assert.equal(cart.ids.length, 0);
    cart.toggle(3);
    assert.equal(cart.has(3), true);
    cart.prune([]);
    assert.equal(cart.has(3), false);
  }
  let saved;
  const cart = setup({ getItem: () => '[1,2]', setItem(key, value) { saved = [key, value]; } }).stores.cart;
  cart.toggle(1);
  assert.deepEqual(saved, ['meow-cart', '[2]']);
});

test('duplicate responses only affect the submitted draft', () => {
  const { components } = setup();
  const form = components.addItemForm({ genericError: 'Error' });
  form.$refs = { form: {}, name: { value: 'New draft' } };
  form.pending = true;
  const event = { detail: {
    elt: form.$refs.form, successful: false,
    requestConfig: { formData: new Map([['name', 'Old draft']]) },
    xhr: { responseText: 'Duplicate', getResponseHeader: () => '12' },
  } };
  form.afterRequest(event);
  assert.equal(form.pending, false);
  assert.equal(form.error, '');
  assert.equal(form.existingId, null);
  form.$refs.name.value = 'Old draft';
  form.afterRequest(event);
  assert.equal(form.error, 'Duplicate');
  assert.equal(form.existingId, '12');
});

test('stock editor stays locked during save and becomes editable after failure', () => {
  const row = fs.readFileSync('app/templates/partials/stock_row.html', 'utf8');
  const handler = name => row.match(new RegExp('@' + name + '="([^"]+)"'))[1];
  const form = { dataset: { genericError: 'Error' }, reset() { throw new Error('draft reset'); } };
  const context = vm.createContext({
    editing: true, editError: '', editPending: false, $el: form,
    $event: { detail: { elt: form } },
  });
  const run = name => vm.runInContext('(function() {' + handler(name) + '})()', context);
  run('htmx:before-request');
  assert.equal(context.editPending, true);
  run('keydown.escape');
  assert.equal(context.editing, true);
  for (const control of row.matchAll(/<(input|select|button)\b[^>]*>/g)) {
    if (/name=|type="submit"|btn_cancel/.test(control[0]) || control[0].includes('@click="if (editPending)')) {
      assert.match(control[0], /:disabled="editPending"/);
    }
  }
  context.$event.detail.successful = false;
  context.$event.detail.xhr = { responseText: 'Duplicate' };
  run('htmx:after-request');
  assert.equal(context.editPending, false);
  assert.equal(context.editing, true);
  assert.equal(context.editError, 'Duplicate');
  context.editing = true;
  context.$event.detail.successful = true;
  run('htmx:after-request');
  assert.equal(context.editing, false);
  assert.equal(context.editError, '');
});

test('failed delete shows an error without closing the stock editor', () => {
  const row = fs.readFileSync('app/templates/partials/stock_row.html', 'utf8');
  const handler = row.match(/hx-delete=[^>]*@htmx:after-request\.stop="([^"]+)"/)[1];
  const button = { form: { dataset: { genericError: 'Error' } } };
  const context = vm.createContext({ editing: true, editError: '', $el: button, $event: { detail: { successful: false, xhr: { responseText: '' } } } });
  vm.runInContext(handler, context);
  assert.equal(context.editError, 'Error');
  assert.equal(context.editing, true);
  context.$event.detail.xhr.responseText = 'Not found';
  vm.runInContext(handler, context);
  assert.equal(context.editError, 'Not found');
});
