# Agentic UI: Choosing How Agents Present And Interact

Status: full article review draft and isolated implementation are prepared. See AGENTIC-UI-DEMO.md and AGENTIC-UI-VALIDATION.md. Speaker notes follow article review.

## Objective
Explain the design choices behind an agent's visual response using one marketplace order: what the agent produces, how it reaches the application, how it is rendered, and how the application exchanges requests and updates with the agent.

## Article Structure
1. **The user problem.** Introduce the marketplace support application. Compare a text answer about an order with an order summary, items table, and recorded-event timeline.
2. **Four questions as a reading map.** How is the UI generated? How is it delivered? How is it rendered? How do the application and agent communicate during interaction? Local sorting and expanding sections do not necessarily involve the agent.
3. **Three generation patterns.** Controlled selects and fills a prebuilt view; declarative composes approved components (A2UI is one specification); open-ended produces UI code. These are useful design categories, not three formal standards. Model-generated UI code is the open-ended branch, not a fourth category.
4. **The same marketplace question in three modes.** Reuse the existing support investigation and factual evidence. Show the selected widget/inputs, A2UI description, or generated HTML/CSS/JavaScript alongside the result. Clearly distinguish model decisions from application code. Order status first, history second.
5. **Delivery and rendering are separate.** Explain a custom HTTP API versus MCP integration, and registered widgets versus executable web UI. A2UI does not require or prohibit an iframe. MCP can itself run over HTTP.
6. **MCP Apps embedding.** Embed the declarative A2UI example in an MCP Apps host. Explain tool metadata, UI resource fetch, sandbox, input/result delivery, and iframe-to-host-to-MCP-server tool calls. Compare direct marketplace rendering with embedding. MCP Apps does not prescribe generation.
7. **Where AG-UI and CopilotKit fit.** Architecture discussion only. AG-UI standardizes app-agent events, progress, state, and interactions. CopilotKit supplies integration libraries/runtime. Neither is required to generate UI code. Do not imply an arbitrary third-party host supports a separate AG-UI connection without integration and permissions.
8. **Choosing an approach and its trade-offs.** Use the decisions below. Generation, embedding, and agent communication are separate choices; combinations are possible.
9. **Lessons, summary, code, references, acknowledgements.** Preserve existing A2UI technical depth in its declarative subsection or an appendix. Derive speaker notes after the article is settled.

## Coverage Map
| Technology | What it defines | What the application still supplies |
|---|---|---|
| A2UI | Component descriptions, bindings, composition, and action messages interpreted by compatible renderers | Widget implementations, catalog, business logic, transport integration |
| MCP Apps | UI resource discovery/loading, sandboxed embedding, host/view data and tool-call bridge | UI generation method, internal view design, provider business logic |
| AG-UI | App-agent event and state exchange, including run lifecycle and user interaction | UI generation, widgets/rendering, domain behavior and integration |

## How To Choose
- **Controlled:** Known useful views, strongest predictability. A complex prebuilt dashboard can be controlled. Trade-off: developers implement every supported view.
- **Declarative:** Known component vocabulary, variable combinations and arrangements. Trade-off: build compatible widgets/catalog and validate descriptions; unsupported components require development.
- **Open-ended:** Views cannot be anticipated and arbitrary visual expression matters. Trade-off: generated-code validation, isolation, accessibility, correctness, styling, and device behavior need more attention. Complexity alone is not a reason to choose it.
- **MCP Apps:** Useful when the interface should run inside a compatible assistant whose frontend you do not control. Supply a web interface and tools using the host contract. For an owned website, direct rendering may be simpler. A sandbox iframe alone is not an MCP Apps integration.
- **AG-UI:** Useful when a shared live app-agent contract for progress, state, or user decisions reduces custom plumbing and aids compatible runtime integration. A simple custom request/response API may suffice. Can support any generation pattern; is not automatically layered over MCP Apps.

## Demo Scope
- Separate branch from current main; preserve existing A2A/A2UI work.
- Test-only controls: controlled, declarative, open-ended. Keep plain text/source evidence available.
- Controlled: model chooses from a bounded set of prebuilt views and supplied record/dataset references.
- Declarative: reuse existing A2UI catalog, SDK validation, and client widgets.
- Open-ended: model produces static HTML/CSS from the same evidence; sanitize it and run in a script-disabled, network-disabled iframe. History controls remain outside the generated document.
- MCP Apps: additional declarative embedding path with real tools/list, resources/read, tools/call, initialization, input/result delivery, and history interaction. A local teaching host is not proof of compatibility with ChatGPT or Claude.
- AG-UI: diagram and explanation only; no new runtime integration.
- No business database reset, main merge, production restart, or publication is part of this request.

## Evidence And Visuals
Use a side-by-side user view, three generation paths, the four-question coverage map, direct-versus-embedded architecture, and an AG-UI connection diagram. Label proposed integrations until run and verified. Verify generated-code facts against source evidence; record latency/token usage only when measured. Avoid claiming broad industry adoption or ranking without evidence.

## Primary References
- https://docs.copilotkit.ai/generative-ui/open-generative-ui
- https://a2ui.org/concepts/overview/
- https://modelcontextprotocol.io/extensions/apps/overview
- https://apps.extensions.modelcontextprotocol.io/api/
- https://docs.ag-ui.com/introduction
