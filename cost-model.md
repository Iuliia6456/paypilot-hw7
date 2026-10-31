## 1. Cost of one step

### Cache: L07 measurements

Five-run average live-step cost:
- With working cache: $0.0003024.
- With D28 breaking cache: $0.0008834.
- The defective step cost about 2.92 times more.

### D14: manual single-step comparison

| Condition | usage.cost_usd | Sum of model spans | Provider cost |
|---|---:|---:|---:|
| Clean | $0.000295 | $0.000296 | $0.000296 |
| D14 | $0.000675 | $0.002140 | $0.002140 |

With D14, the stand's displayed cost misses retry calls.
The provider and span sum agree. The actual D14 cost was
3.17 times the displayed cost in this run.

The separate B1 kit run showed the same problem at step 2:
$0.000316 displayed versus $0.001710 from spans and provider.

## 2. Cost of a dialogue

### B2: five-run medians

| Profile | Dialogue cost | Dialogue time |
|---|---:|---:|
| clean | $0.004267 | 22.987 s |
| lesson-08 | $0.005311 | 22.747 s |

The defective dialogue cost about 24% more.
Its duration was almost unchanged.

### B3: summarization, one run per condition

| Condition | Model-span cost, excluding summary | Full provider cost |
|---|---:|---:|
| Clean summary | $0.001843 | $0.002389 |
| Defective summary | $0.003183 | $0.003401 |

The defective summary lost transaction details. At step 4,
the agent called get_account and get_transactions again.
The final answer recovered the correct transaction and amount.

Full provider cost was about 42% higher with the defect.
These are single-run observations, not five-run medians.
We did not measure a matching no-summarization control.

## 3. Monthly estimate

### Assumptions - not measured traffic

Source: an illustrative workload chosen for this exercise.
- 800 active users per month.
- 10 dialogues per user per month.
- 80% B1-like dialogues and 20% B2-like dialogues.
- Clean conditions.
- Prices and behaviour remain as measured in B4.
- Only model charges are included; hosting, storage and support
  costs are excluded.

Total: 8,000 dialogues per month.

Using B4 clean median dialogue costs as planning estimates:

Gemini:
8,000 × (0.8 × $0.000518 + 0.2 × $0.005537)
= approximately $12.17 per month.

Haiku:
8,000 × (0.8 × $0.000378 + 0.2 × $0.004109)
= approximately $8.99 per month.

Estimated saving with Haiku: $3.18 per month, about 26%.
Haiku was slower in both scenarios.

These estimates use medians as typical costs. Production
forecasting should use average billed cost and actual traffic,
including expensive outliers.

## 4. Forecast as usage grows

For N users:

Monthly cost =
N × dialogues per user ×
(B1 share × B1 cost + B2 share × B2 cost).

With the assumptions above:
- Gemini: approximately N × $0.015218.
- Haiku: approximately N × $0.011242.

With a fixed scenario mix and dialogue length, cost grows
approximately in proportion to user count.

Longer conversations can grow more expensive faster than their
number of turns: later calls repeatedly read earlier history.
D15 adds duplicated tool results to that growing input.

D14 is a visible defect: repeated calls and longer waits.
D15 is quieter: no extra identical tool calls, but more input
tokens and higher cost.

Neither defect alone proves faster-than-linear growth with
user count; that requires per-user work or retry rates to grow.

## 5. Blind spots

| What misses the cost or problem | What to inspect instead |
|---|---|
| usage.cost_usd omits D14 retries | All model-call spans and provider-reported cost |
| Langfuse has no matching model definition | Configure the exact model match and prices |
| Langfuse prices only input/output | Price cached input, cache creation and reasoning separately |
| usage.cost_usd, kit $ trace and root total-token attributes omit summarization | Inspect agent.summarize usage and full provider cost; include its Langfuse cost |
| Repeated-call checks miss D15 | Inspect context replay and input-token growth |
| A median budget can pass despite expensive runs | Keep per-run results and consider an additional outlier limit |

For the inspected generation, configured prices calculate
$0.00009304, matching provider.cost_usd and the rounded
stand.cost_usd of $0.000093.

Without cached-input pricing, this generation would be
underpriced by approximately 27%.

An exact comparison with Langfuse's calculated numeric total
remains unverified; its tooltip rounded the amount.

## 6. Two cost-saving choices and their trade-offs

| Choice | Expected benefit | What can get worse |
|---|---|---|
| Switch from Gemini to Haiku | B4 clean dialogues were about 26–27% cheaper | Responses were slower; answer quality still needs evaluation |
| Summarize history earlier | Later calls may read fewer tokens | Summarization costs money and may lose details, causing repeated lookups or wrong answers |

Summarization should preserve structured case details and pass
memory checks before being accepted as a cost-saving change.

## 7. Predictions versus results

| Prediction | Observed result |
|---|---|
| D14 actual cost about 5× displayed cost | 3.17× in the manual request; 5.41× at B1 defect step 2 |
| Provider cost approximately matches span sum | Confirmed for the inspected B1 requests |
| B2 lesson-08 costs about 1.25× clean | Measured 1.24× using five-run medians |
| Summarizing after turn 2 makes the dialogue cheaper | Not established: no matching no-summary control; faulty summarization cost more than clean summarization |

## 8. Budget result and remaining limits

The L03 budget counts input plus output tokens across all turns.

Initial clean median: 68,439 tokens.
Calibrated limit: 72,000 tokens, approximately 5% headroom.
Latency limit: 35,000 ms.

On the subsequent comparison:
- Clean median: 64,702 tokens — PASS.
- lesson-08 median: 71,767 tokens — PASS.

The budget did not detect D15 in this batch. We keep this result
rather than lowering the threshold after seeing the defect runs.

The budget case was run separately in l08_budget.jsonl because
the current L03 runner does not support the existing L05
invariant assertions. The combined-set run remains unresolved.


# Model migration decision

Evidence: b4.json. Five runs per model, scenario and condition.

## What is cheaper per dialogue?

On clean B1, Haiku costs $0.000378 versus Gemini's $0.000518
(medians): about 27% cheaper. Median time increases from
3.2 to 4.5 seconds.

On clean B2, Haiku costs $0.004109 versus Gemini's $0.005537:
about 26% cheaper. Median time increases from 11.8 to 21.6 seconds.

Haiku saves money but is slower. We compare dialogue costs
and time, not token counts across models.

## Which checks passed?

B1 baseline passed 5/5 on both models.
With D14, all five runs failed on both models: the repeated-call
check detected the defect.

B2 baseline passed on both models using the five-run median.
With D15, Haiku failed the 6,500-token threshold, while Gemini
passed despite the enabled defect. The threshold therefore
does not detect D15 reliably across models.

## What do these checks miss?

They do not assess tone, completeness, factual correctness of
every answer, or whether the customer receives equally useful
help. These require answer review and judge evaluation in L09.

## Final decision

**What we trade off:** Haiku was about 26–27% cheaper on clean
dialogues, but slower. Earlier summarization may reduce input
tokens, but risks losing details and causing extra tool calls.

**What we choose not to do now:** We do not switch models until
D14 and D15 are fixed and retested. We do not summarize earlier
while the summary loses transaction details.

**When the decision changes:** Consider Haiku after the fixes,
if answer quality passes review and response times are acceptable.
Consider earlier summarization only when it preserves case
details and lowers the full provider cost, including the summary.