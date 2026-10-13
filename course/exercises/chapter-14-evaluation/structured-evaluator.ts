function evaluate(ctx: EvaluationContext): EvaluationResult {
  let expected = ctx.experiment?.itemExpectedOutput;
  if (typeof expected === "string") { try { expected = JSON.parse(expected); } catch { expected = null; } }
  if (!expected || typeof expected !== "object") expected = ctx.observation.metadata?.expected_output;
  let actual = ctx.observation.output;
  if (typeof actual === "string") { try { actual = JSON.parse(actual); } catch { actual = null; } }
  const valid = actual !== null && typeof actual === "object" && !Array.isArray(actual) && typeof actual.shipment_status === "string" && Number.isInteger(actual.quantity);
  const hasReference = expected !== null && typeof expected === "object" && typeof expected.shipment_status === "string" && Number.isInteger(expected.quantity);
  if (!hasReference) return {scores:[{name:"structured_grade",value:"not_assessable",dataType:"CATEGORICAL",comment:"Missing or invalid reference."}]};
  const statusMatches = valid && actual.shipment_status === expected.shipment_status;
  const quantityMatches = valid && actual.quantity === expected.quantity;
  const grade = !valid ? "invalid_output" : !statusMatches ? "incorrect" : quantityMatches ? "correct" : "partial";
  return {scores:[
    {name:"structured_grade",value:grade,dataType:"CATEGORICAL",comment:"Status is critical. A quantity mismatch with correct status earns partial credit."},
    {name:"schema_valid",value:valid,dataType:"BOOLEAN"},
    {name:"status_matches",value:statusMatches,dataType:"BOOLEAN"},
    {name:"quantity_matches",value:quantityMatches,dataType:"BOOLEAN"}
  ]};
}