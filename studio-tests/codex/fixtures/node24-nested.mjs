import {describe,it,test} from 'node:test';
describe('outer',()=>{it('one',()=>{});describe('inner',()=>{it('deep',()=>{});it.skip('skip',()=>{});});});
test('flat',()=>{});test('parent',async t=>{await t.test('child',()=>{});});
