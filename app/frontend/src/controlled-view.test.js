import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {readFileSync} from 'node:fs';
import {build} from 'esbuild';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';

const compiled=await build({entryPoints:[new URL('./ControlledAnswer.jsx',import.meta.url).pathname],bundle:true,write:false,platform:'node',format:'cjs',packages:'external',metafile:true});
const module={exports:{}};
new Function('require','module','exports',compiled.outputFiles[0].text)(createRequire(import.meta.url),module,module.exports);
const ControlledAnswer=module.exports.default;
const source=JSON.parse(readFileSync(new URL('../../backend/tests/fixtures/a2ui-answer.json',import.meta.url)))[0].createSurface.dataModel;
const render=ui=>renderToStaticMarkup(React.createElement(ControlledAnswer,{ui},React.createElement('p',null,'Retained support explanation')));
test('controlled summary renders evidence directly without an A2UI runtime',()=>{
 assert.ok(Object.keys(compiled.metafile.inputs).every(p=>!p.includes('A2UI')));
 assert.ok(Object.values(compiled.metafile.outputs).flatMap(o=>o.imports).every(x=>!x.path.startsWith('@a2ui/')));
 const html=render({status:'completed',renderer:'application-prebuilt',selection:{view:'summary',reference:'r0'},data:source.records.r0,actions:source.actions});
 assert.match(html,/Order summary/);
 assert.match(html,/dispatched/i);
 assert.match(html,/Show order history/);
 assert.match(html,/Retained support explanation/);
 assert.doesNotMatch(html,/A2UI messages received/);
});
test('controlled table and timeline display source rows and preserve notices',()=>{
 const dataset={title:'Evidence',headers:['kind','occurred at','details'],rows:[['delivered','2026-10-01T10:00:00Z','<script>not executable</script>']],scope:'Investigation evidence',source:'e1',notice:'Partial records shown',timeline:true};
 for(const view of ['table','timeline']){
  const html=render({status:'completed',renderer:'application-prebuilt',selection:{view,reference:'d0'},data:dataset,actions:{}});
  assert.match(html,/delivered/i);
  assert.match(html,/Partial records shown/);
  assert.match(html,/&lt;script&gt;not executable&lt;\/script&gt;/);
  assert.doesNotMatch(html,/<script>/);
 }
});
test('saved legacy controlled output asks for regeneration instead of invoking A2UI',()=>{
 const html=render({status:'completed',generation_mode:'controlled',messages:[]});
 assert.match(html,/Regenerate the view/);
 assert.match(html,/Retained support explanation/);
 assert.doesNotMatch(html,/A2UI messages received/);
});
