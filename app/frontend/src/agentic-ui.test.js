import {test} from 'node:test';
import assert from 'node:assert/strict';
import {isolatedHtml,generatedCsp,modeDescriptions} from './agentic-ui.js';
test('generated document applies a no-script/no-network policy before model markup',()=>{
 const html=isolatedHtml('<html><script>fetch("https://invalid.example")</script></html>');
 assert.ok(html.indexOf('Content-Security-Policy')<html.indexOf('<html>'));
 assert.match(generatedCsp,/script-src 'none'/);
 assert.match(generatedCsp,/connect-src 'none'/);
 assert.match(generatedCsp,/form-action 'none'/);
 assert.throws(()=>isolatedHtml('x'.repeat(100001)));
 assert.equal(Object.keys(modeDescriptions).length,3);
});
