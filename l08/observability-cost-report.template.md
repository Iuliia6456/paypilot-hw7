# Observability & Cost Report · [System]

Replace bracketed placeholders with your own measurements. Keep assumptions separate from observations. Link each finding to saved evidence.

| Field | Value |
|---|---|
| System | [System and scope] |
| Stand version | [Version or commit] |
| Main model | [Model and provider] |
| Migration comparison | [Current model → candidate model] |
| Pricing source | [Source, version and date] |
| Model rates per million tokens | [Input, cached input, cache creation, output and reasoning rates] |
| Trace backend | [Backend and instrumentation] |
| Measurement dates | [Dates] |
| Runs per condition | [Scenario, condition and run count] |
| Measurement tools | [Runner, API and trace viewer] |

## Slide 1 · Trace vs. Counter

Session: [Session identifier], [condition], [number of dialogue steps], [total cost].

Session-list screenshot: [Evidence path showing step count and total cost].

Conversation screenshot: [Evidence path showing the dialogue steps].

**Blind spots table:**

| Counter or view | What it misses | How to check the full cost |
|---|---|---|
| [Application cost counter] | [Missing operations and measured difference] | [Independent source and reconciliation method] |
| [Trace viewer without model pricing] | [Observed limitation] | [Required configuration and verification] |
| [Trace viewer with incomplete token pricing] | [Unpriced categories and undercount] | [Complete pricing and comparison] |
| [History summarization] | [Which counters exclude its usage or cost] | [Where full usage and cost are recorded] |

**Incident analysis:**

**Scenario:** [Scenario, condition and history-compression settings].

| Step | Span | What it contains | What went wrong |
|---|---|---|---|
| [Earlier step] | [Span] | [Details present before the failure] | [State before divergence] |
| **[Failure step]** | **[First span where information is lost]** | **Input:** [Required details]. **Output:** [Summary or result without those details]. | [First confirmed divergence] |
| [Later step] | [Model span] | [Actual output, including tool calls and arguments] | [Observed consequence] |
| [Later step] | [Tool span] | [Actual request and result] | [Extra work or incorrect action] |

**Input versus output:** [Compare exact evidence on the first divergent span.]

**For the regulator:** [One sentence identifying where and what was lost, with consequences supported by the trace.]

**Cost from three sources:**

[Identify the scenario and measurement scope. State whether these are individual runs or aggregates.]

| Scenario | Condition | System report (`usage.cost_usd`) | Sum of model spans | Provider cost | Comparison |
|---|---|---:|---:|---:|---|
| [Scenario] | [Baseline] | [Cost] | [Cost] | [Cost] | [Agreement or difference and reason] |
| [Scenario] | [Changed condition] | [Cost] | [Cost] | [Cost] | [Agreement or difference and reason] |

**Scenario cost:**

[Run count per condition and aggregation method.]

| Measurement | Baseline | Changed condition | Changed / baseline |
|---|---:|---:|---:|
| Input tokens, median | [Value] | [Value] | [Ratio] |
| Dialogue time, median | [Value and unit] | [Value and unit] | [Ratio] |
| Dialogue cost, median, from spans | [Value and currency] | [Value and currency] | [Ratio] |

[Interpretation and limitations.]

## Slide 2 · Cost forecast

### Measured costs

Current model: [Model].

| Level | Measured cost | Evidence |
|---|---:|---|
| One step, baseline | [Cost] | [Evidence] |
| One step, changed condition | [Cost] | [Evidence] |
| Short dialogue, baseline | [Cost] | [Evidence and aggregation] |
| Longer dialogue, baseline | [Cost] | [Evidence and aggregation] |

[Describe the scenarios represented by these measurements.]

### Planning assumptions

| Assumption | Value | Source |
|---|---:|---|
| Monthly active users | [Count] | [Source] |
| Dialogues per user per month | [Count] | [Source or explicitly stated assumption] |
| Short conversations | [Share] | [Source] |
| Longer conversations | [Share] | [Source] |
| Cost per scenario | [Measured values] | [Evidence] |

### Monthly estimate

Monthly dialogues = users × dialogues per user.

Weighted dialogue cost = sum of (scenario share × scenario cost).

Monthly model cost = monthly dialogues × weighted dialogue cost = [Estimate].

[Explain exclusions and uncertainty. If using medians, explain that this is a planning approximation rather than an estimate based on mean cost.]

### Forecast for N users

C(N) = N × dialogues per user × sum of (scenario share × scenario cost).

[State assumptions held constant.]

**What can grow faster than N:** [Identify the changing quantity: users, dialogue length, retries or history size. Explain the mechanism and distinguish measured evidence from inference.]

[Loud versus quiet cost defects and how each is detected.]

## Slide 3 · Decision

### Cost controls and tradeoffs

| Change | Expected benefit | What gets worse or needs protection |
|---|---|---|
| [Change] | [Measured or expected benefit] | [Tradeoff or condition for safe use] |
| [Change] | [Measured or expected benefit] | [Tradeoff or condition for safe use] |
| [Change] | [Measured or expected benefit] | [Tradeoff or condition for safe use] |
| [Optional change] | [Benefit] | [Tradeoff] |

**What we trade:** [Benefit exchanged for a cost, delay or quality risk.]

**What we will not do:** [Changes deferred and reasons.]

**When the decision changes:** [Measurable approval or reconsideration conditions.]

### Model migration

Comparison: [Current model] → [Candidate model].

[Run count per model, scenario and condition; measurement scope.]

| Model | Scenario | Condition | Cost: median (min–max), USD | Time: median (min–max) | Check result |
|---|---|---|---:|---:|---|
| [Current model] | [Short scenario] | [Baseline] | [Values] | [Values] | [Verdict] |
| [Current model] | [Short scenario] | [Defect] | [Values] | [Values] | [Verdict] |
| [Current model] | [Long scenario] | [Baseline] | [Values] | [Values] | [Verdict] |
| [Current model] | [Long scenario] | [Defect] | [Values] | [Values] | [Verdict] |
| [Candidate model] | [Short scenario] | [Baseline] | [Values] | [Values] | [Verdict] |
| [Candidate model] | [Short scenario] | [Defect] | [Values] | [Values] | [Verdict] |
| [Candidate model] | [Long scenario] | [Baseline] | [Values] | [Values] | [Verdict] |
| [Candidate model] | [Long scenario] | [Defect] | [Values] | [Values] | [Verdict] |

Token counts are model-specific and must not be compared one to one across tokenizers.

**Decision:** [Migrate / do not migrate / migrate subject to conditions].

- **What is cheaper:** [Dialogue costs, ratios and latency tradeoffs.]
- **What stayed green:** [Checks and results for both models; missed defects.]
- **What the checks do not see:** [Unassessed answer quality.]

**Thresholds to recalibrate:** [All model-dependent token, latency and monetary limits that require new baseline measurements.]

**Still unmeasured — answers for the judge:**

- [Answer or scenario requiring factual-accuracy evaluation.]
- [Answer or scenario requiring completeness evaluation.]
- [Answer or scenario requiring clarity or tone evaluation.]
- [Answer requiring verification that reported actions match actual results.]

### Budgets recorded in cases

File: [Relative path to case set].

| Case | Token limit | Time limit | Identical-call limit per step | Gate | Runs |
|---|---:|---:|---:|---|---:|
| [Case ID] | [Limit or not configured] | [Limit and unit] | [Limit or not configured] | [Gate] | [Count] |

[Add a row for each case. Explain aggregation rules, baseline model and calibration evidence.]

[Baseline and defect results. Retain failed calibration attempts and explain changes.]

[Outliers or other risks hidden by aggregate checks.]

### Threshold calibration: [Case]

Model: [Model]. Each batch contains [Count] runs.

- Initial baseline calibration median: [Tokens].
- Independent baseline verification median: [Tokens].
- Defect median: [Tokens].

[State whether thresholds were applied offline to saved runs or tested in separate batches.]

| tokens_total threshold | Baseline | Defect condition | Verdict |
|---|---|---|---|
| [Too-loose limit] | [Result] | [Result] | [Why unsuitable] |
| [Too-tight limit] | [Result] | [Result] | [Why unsuitable] |
| [Selected limit] | [Result] | [Result] | [Observed separation and limitations] |

Selected limit = calibration median × (1 + chosen margin), rounded using [Rule].

Actual margin (%) = (selected limit / baseline median − 1) × 100.

[Report margins for calibration and independent verification separately. State when the limit was chosen.]

Evidence:

- Calibration: [Report path].
- Baseline verification: [Report path].
- Defect verification: [Report path].

### Full-set verification

[Commands or settings used to include all required gates.]

- Baseline: [Passed / total].
- Defect condition: [Passed / total and failed checks].
- Behavioural checks: [Results].
- Budget checks: [Results].
- Final system profile: [Profile].

Reports:

- [Defect report path].
- [Baseline report path].

## Predictions before the lab

Recorded on: [Date before measurements].

[State whether predictions were informed by lesson examples or other sources. Do not invent retrospective predictions.]

- Retry cost: [Predicted actual/reported cost ratio and reason].
- Cost-source agreement: [Prediction and reason].
- History-growth cost: [Predicted changed/baseline ratio and reason].
- Earlier summarization: [Predicted effect on total cost and reason].

Comparison with results: [Observed outcomes, supported conclusions and unresolved predictions].
