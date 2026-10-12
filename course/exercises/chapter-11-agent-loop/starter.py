"""Fill in run_loop; use the supplied tests and live adapters with --implementation starter."""
async def run_loop(model, execute, tools, question, *, instructions, max_turns=8):
    # TODO: retain messages, call model, execute allowed tools, pair results by ID,
    # count model calls, distinguish final answer from tool requests, stop at limit.
    raise NotImplementedError('Implement the orchestration loop')
