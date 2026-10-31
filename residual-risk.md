# Residual Risk Analysis - Golden Dataset L03

**Dataset:** sets/golden.jsonl - 39 cases, including 34 daily cases and 5 human-review cases.

**Dataset set_hash:** f529e24bd425. 

**Mandate:** Ship it.

## 1. Coverage matrix

| Layer | Corpus / RAG | Rule engines | Memory | Tools |
|---|---|---|---|---|
| Retrieval | Not covered | Not covered | Not covered | Not covered |
| Generation | HW-C13; TON-004 and HW-C14 - planned human review | FX-001–FX-009 and their `-S` cases; LIM-001, LIM-001-D, LIM-002, LIM-002-D; DIS-001–DIS-005, DIS-002-N, DIS-004-N; HW-C11, HW-C12 | Not covered | FX-001–FX-009 check the tool’s `final_amount` and its presence in the answer |
| Action | Not covered | LIM-003; DIS-007 | Not covered | LIM-003 checks monthly_remaining_eur; DIS-007 checks eligible |

TON-001–TON-004 and HW-C14 are planned human-review cases and were excluded from the daily runs. TON-001 - TON-003 assess tone and refusal explanations, which this matrix does not represent separately.

## 2. What the dataset misses

| Coverage gap | Possible consequence | Decision | Why accepted for now |
|---|---|---|---|
| Eligibility expressed using unexpected wording: DIS-002-N and DIS-004-N passed despite incorrect permission | Customers are told they can open a dispute when they cannot | Document the gap; strengthen verification before using this test suite as a release readiness criterion; manually review these cases meanwhile | The limitation is documented; passing results are not treated as proof of correct eligibility |
| Conflicting amounts in an answer | Customers may receive misleading transfer-limit information | Keep LIM-003 for the tool field; add a check for contradictory amounts in the answer | The tool field is now checked, but LIM-001 still accepts an answer containing the expected number alongside incorrect amounts |
| Retrieval quality and conversation memory | Missing evidence or forgotten details can produce incorrect answers | Postpone retrieval evaluation to L4 and add multi-turn tests later | This assignment focuses on selected single-turn banking scenarios |
| Tone, clear refusal and unsupported promises | Customers may receive confusing or inappropriate guidance | Retain five human-review cases; automated judge planned for L09 | Daily deterministic checks cannot reliably assess these qualities |

After revision, LIM-003 detects D22 and DIS-007 detects D26.
The wording-based checks DIS-002-N and DIS-004-N remain weak.
HW-C12 also produced a false alarm: “60-day window” was correct,
but the assertion required “60 days”.

Complaints outside the set include:
- C-02 - no dedicated case for the original question.
- C-07 - insufficient context to reproduce the original operation.
- C-15 - mobile-app freezing is outside this agent evaluation.
- C-16 - customer dissatisfaction alone does not establish an error.
- C-20 - insufficient detail to reproduce the complaint.

## 3. Dataset size and cost

The current dataset contains 39 cases: 34 daily cases and
5 human-review cases. Each daily case runs once:
34 × 1 = 34 evaluated answers per daily run.

The cost and model-call figures below refer to the original
37-case dataset, set_hash ee3efa5e629b, with 32 daily cases.
They do not measure the revised 34-case daily run.<br>

The clean baseline made 91 model calls, counted from llm.call
spans for its 32 requests between 2026-10-10 22:16:36 and
22:19:12 UTC. These calls used 262,972 input tokens and
19,387 output tokens: 282,359 tokens in total.

Source: traces-for-hw2.jsonl.

Requested model recorded in all 91 llm.call spans:<br>
claude-haiku-5-5 (gen_ai.request.model).<br> No AI judge was used.

The following calculations are done according to the 3 reports (golden-clean-20261010T221912.json, golden-clean-20261011T132625.json, golden-lesson-03-20261010T231058.json).

| Run | Passed | Total tokens recorded in report |
| --- | --- | ---: |
| Clean baseline | 32/32 | 282,359 |
| lesson-03 | 17/32 | 268,100 |
| Clean with changed prompt | 23/32 | 279,558 |
| Total | | 830,017 |

**Console** usage for October 10-11: 781,059 input + 67,455 output = 848,514 tokens. The three full-run reports contain 830,017 tokens. The remaining 18,497 tokens are usage outside those reports; individual checks were also run during this period.

**Console** cost: October 10 - $0.07; October 11 - $0.04. Total: $0.11.<br>
Cost formula from L02:
cost = model calls × average tokens per call × price per token.<br>
Because the reports do not separate input and output tokens, costs are estimated proportionally using the console’s average cost per token:
- Three full runs: $0.11 ÷ 848,514 × 830,017 ≈ $0.108.
- One clean baseline run: $0.11 ÷ 848,514 × 282,359 ≈ $0.037.<br>

These costs represent an approximate allocation based on token counts.
The calculation assumes a similar ratio of input to output data; final amounts
are rounded to the nearest cent.

Sensitivity: The prompt change caused 9 of 32 cases to change from PASS to FAIL. The result fell from 32/32 to 23/32, matching the prediction recorded in commit 773399e.

Under Zero regulatory risk: Unresolved risks related to eligibility, account restrictions, and prohibited activities will block the release. Direct verification of eligibility results, necessary escalations, and prohibited write operations would be required.