const test = require('node:test');
const assert = require('node:assert/strict');

const { loadVideos } = require('../app/static/storage.js');

test('loadVideos calls /api/v1/videos with credentials and renders empty state', async () => {
    const grid = { innerHTML: '' };
    const calls = [];
    const fetchFn = async (url, opts) => {
        calls.push({ url, opts });
        return {
            ok: true,
            status: 200,
            json: async () => []
        };
    };

    await loadVideos({ fetchFn, gridEl: grid, onUnauthorized: () => assert.fail('should not redirect') });

    assert.equal(calls.length, 1);
    assert.equal(calls[0].url, '/api/v1/videos');
    assert.equal(calls[0].opts.credentials, 'include');
    assert.ok(grid.innerHTML.includes('暂无生成记录'));
});

test('loadVideos triggers onUnauthorized on 401', async () => {
    const grid = { innerHTML: '' };
    let unauthorized = false;
    const fetchFn = async () => ({
        ok: false,
        status: 401,
        text: async () => ''
    });

    await loadVideos({ fetchFn, gridEl: grid, onUnauthorized: () => { unauthorized = true; } });
    assert.equal(unauthorized, true);
});

test('loadVideos renders server error detail', async () => {
    const grid = { innerHTML: '' };
    const fetchFn = async () => ({
        ok: false,
        status: 500,
        text: async () => JSON.stringify({ detail: 'boom' })
    });

    await loadVideos({ fetchFn, gridEl: grid });
    assert.ok(grid.innerHTML.includes('加载失败'));
    assert.ok(grid.innerHTML.includes('boom'));
});

