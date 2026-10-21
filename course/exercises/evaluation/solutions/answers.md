# Evaluation — solutions

Complete the exercise before reading the historical grades. Human judgments and automated judge outputs are evidence to inspect, not interchangeable truth labels.

## Human review

The supplied nano answers are cases 02, 09, 16, 23 and 24. `historical-human-five.json` preserves the recorded human grades: **2, 1, 1, 0, 1**. Some historical judgments have no written rationale; that absence is explicit. Students should provide their own fact-based reasons.

- **02:** The answer names both order-1 products, quantities of two, and the correct sellers. This satisfies the factual request.
- **09:** It explains buyer payment as captured but does not clarify whether the question concerns buyer payment or seller settlement. The clarified rubric asks for that distinction.
- **16:** It correctly says the payout cannot yet release, but misses the explanation that 23 hours have passed and one hour of the 24-hour hold remains. A status field alone is insufficient for the requested eligibility explanation.
- **23:** It asks about an unrelated Cedar ambiguity rather than answering which sellers the incident affected. The reference identifies only payout-1/Cedar as confirmed affected and requires caution about broader impact.
- **24:** It gives the correct remaining unpaid amount of INR 2,249.10. The recorded human and Claude v3 grades are partial. Inspect the request, evidence and required causal explanation: an unrequested arithmetic breakdown is optional under the clarified reference. A reviewer arguing for full credit must explain whether all essential explanation/evidence requirements are met rather than blindly copy the old grade. The later October run and adjudication involved different saved candidate answers and is not this record.

A disagreement with the historical labels should be documented and reviewed, not silently overwritten. The full 18-case paired report retains the original and clarified references, both candidate outputs, separate human/Claude scores and reasoning.

## Native structured comparison

| Case | Shipment status | Quantity | Expected grade |
| --- | --- | ---: | --- |
| item-1 in order-1 | delivered | 2 | correct |
| item-2 in order-1 | delivered | 2 | correct |
| item-3 in order-2 | pending | 2 | correct |

All three supplied answers are actual recorded agent outputs. The older five-case fixture remains as optional preparation history. Reference fields come from independent database queries taken before each run and rechecked afterward. Candidate traces and output provenance are in the fixture.

The native evaluator requires valid JSON fields. Matching status and quantity gives `correct`; correct status with incorrect quantity gives `partial`; incorrect status gives `incorrect`; invalid schema gives `invalid_output`; missing reference gives `not_assessable`. This teaching contract treats shipment status as critical. It allows additional evidence fields but does not assess their entailment.

## Instructor Claude replay

The instructor uses cases 02, 09, 16, 21 and 23. `saved-claude-five.json` contains the historical Claude v3 grades **2, 1, 1, 2, 0**. A fresh teaching run uses the smaller `chapter14-demo-v1` rubric, so it is a separate evaluation; never replace the full historical 18-case table with its scores.

The validated fresh run returned **2, 1, 1, 1, 0**. Case 21 demonstrates why judgment can differ: refund facts are correct, while the timeline citations point to order-state evidence rather than the chronological event evidence. Compare the grader's rationale, business facts and rubric. The new run is a workflow demonstration, not an independent validation of Claude accuracy or a new model ranking.
