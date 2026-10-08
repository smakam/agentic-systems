import test from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {remarkSafeBreaks} from './markdown.js';

const render=text=>renderToStaticMarkup(React.createElement(Markdown,
  {remarkPlugins:[remarkGfm,remarkSafeBreaks]},text));
test('agent status tables render as table cells, including safe line breaks',()=>{
  const html=render('| Status | Reason | Next step |\n|---|---|---|\n| **paid**<br>payout held | Payment captured | Check delivery |');
  assert.match(html,/<table>/);
  assert.match(html,/<th>Status<\/th>/);
  assert.match(html,/<strong>paid<\/strong><br\/>\s*payout held/);
  assert.doesNotMatch(html,/&lt;br/);
});
test('raw HTML is not enabled by line-break support',()=>{
  const html=render('<iframe src="https://example.test"></iframe>');
  assert.doesNotMatch(html,/<iframe/);
});
