// Tool invocations and evidence saves measure different operations.
export function executionCounts(metrics={}) {
  const nonnegative=value=>Number.isInteger(value)&&value>=0?value:null;
  return {
    toolInvocations: nonnegative(metrics.actual_tool_invocations)
      ?? (Array.isArray(metrics.tool_attempts)?metrics.tool_attempts.length:null),
    evidenceSaveAttempts: nonnegative(metrics.evidence_save_attempts)
      ?? nonnegative(metrics.business_tool_calls),
  };
}
