// Permit the line-break tag used inside agent tables without enabling raw HTML.
export function remarkSafeBreaks() {
  return function visit(node) {
    if (node.type === 'html' && /^<br\s*\/?\s*>$/i.test(node.value)) {
      node.type = 'break';
      delete node.value;
    }
    node.children?.forEach(visit);
  };
}
