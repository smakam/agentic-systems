// Generated code gets no same-origin capability, credentials or network access.
export const mcpCsp="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'; frame-src 'none'; object-src 'none'";
export const generatedCsp=mcpCsp.replace("script-src 'unsafe-inline'", "script-src 'none'");
export function isolatedHtml(html){
 if(typeof html!=='string'||html.length>100000)throw new Error('Invalid generated document');
 // The first policy applies before any model-authored tags or scripts execute.
 return `<!doctype html><meta http-equiv="Content-Security-Policy" content="${generatedCsp}"><meta name="referrer" content="no-referrer">${html}`;
}
export const modeDescriptions={
 controlled:'The model selects one prebuilt view and its data. The application fixes the arrangement.',
 declarative:'The model composes registered components and data references. The client draws the widgets.',
 'open-ended':'The model writes HTML and CSS without a widget catalog. This demo disables scripts and network access.'
};
