const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const assert = require('node:assert/strict');
const source = fs.readFileSync(path.join(__dirname, '../scripts/x-ad-filter.js'), 'utf8');
let tests = 0;
const url = 'https://api.twitter.com/graphql/abc123/HomeTimeline';
function run(body, overrides = {}) {
  let calls = 0, result;
  vm.runInNewContext(source, {
    $request: {url: overrides.url || url},
    $response: {status: overrides.status || 200, body},
    console: {log() {}},
    $done(value) { calls++; result = value; }
  }, {timeout: 1000});
  assert.equal(calls, 1);
  return JSON.parse(JSON.stringify(result));
}
function check(name, fn) {fn(); tests++; console.log('PASS ' + name);}
const organic = {entryId: 'tweet-1', content: {itemContent: {tweet_results: {result: {text: 'hello'}}}}};
const cursor = {entryId: 'cursor-bottom-1', content: {value: 'pagination-token'}};
const ad = {entryId: 'tweet-2', content: {itemContent: {promotedMetadata: {advertiser_results: {id: '1'}}}}};
check('remove explicit promoted metadata; preserve tweet and cursor', () => {
  const body = {data: {home: {instructions: [{entries: [organic, ad, cursor]}]}}};
  const out = JSON.parse(run(JSON.stringify(body)).body);
  assert.deepEqual(out.data.home.instructions[0].entries, [organic, cursor]);
});
check('module items retain organic neighbors', () => {
  const moduleAd = {item: {itemContent: {promotedMetadata: {id: '2'}}}};
  const body = {data: {timeline: {entries: [{content: {items: [{item: {itemContent: {text: 'normal'}}}, moduleAd]}}]}}};
  const out = JSON.parse(run(JSON.stringify(body)).body);
  assert.equal(out.data.timeline.entries[0].content.items.length, 1);
  assert.equal(out.data.timeline.entries[0].content.items[0].item.itemContent.text, 'normal');
});
check('promoted entry ID recognized', () => {
  const out = JSON.parse(run(JSON.stringify({data: {entries: [{entryId: 'promoted-tweet-10'}, cursor]}})).body);
  assert.deepEqual(out.data.entries, [cursor]);
});
check('unmodified JSON passed through without reserialization', () => {
  assert.deepEqual(run(JSON.stringify({data: {entries: [organic, cursor]}})), {});
});
check('quoted metadata does not remove parent organic tweet', () => {
  const quote = {entryId: 'tweet-3', content: {itemContent: {quote: {promotedMetadata: {id: 'nested'}}}}};
  assert.deepEqual(run(JSON.stringify({data: {entries: [quote]}})), {});
});
check('empty metadata and ordinary text mentioning ads retained', () => {
  assert.deepEqual(run(JSON.stringify({data: {entries: [{content: {itemContent: {promotedMetadata: {}, text: 'advertising'}}}]}})), {});
});
check('invalid JSON and errors are unchanged', () => {
  for (const body of ['<html>Error</html>', '{', JSON.stringify({errors: [{message: 'error'}], data: {entries: [ad]}})]) {
    assert.deepEqual(run(body), {});
  }
});
check('non-target hosts/endpoints/statuses not modified', () => {
  const body = JSON.stringify({data: {entries: [ad]}});
  for (const endpoint of ['https://abs.twitter.com/graphql/abc/HomeTimeline', 'https://api.twitter.com/graphql/abc/Login', 'https://evil.example/graphql/abc/HomeTimeline']) {
    assert.deepEqual(run(body, {url: endpoint}), {});
  }
  assert.deepEqual(run(body, {status: 403}), {});
});
check('oversize and deep JSON passed through', () => {
  assert.deepEqual(run(' '.repeat(3 * 1024 * 1024 + 1)), {});
  let nested = {entries: [ad]};
  for (let i = 0; i < 95; i++) nested = {next: nested};
  assert.deepEqual(run(JSON.stringify({data: nested})), {});
});
console.log('All ' + tests + ' checks passed. Synthetic responses only; no live X app test.');
