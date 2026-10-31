""
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.engines import disputes, fx, limits, policy

AS_OF = date(2026, 9, 15)

CUSTOMERS = {
    "CUS-0001": ("tier1", 120.0),
    "CUS-0002": ("tier2", 800.0),
    "CUS-0005": ("tier2", 5000.0),
    "CUS-0007": ("tier2", 0.0),
    "CUS-0010": ("tier3", 15000.0),
}


WHY_GROUNDED = ("a money figure: exact equality would fail on the last cent, "
                "so level 2 with a tolerance; the figure is read from the "
                "quote_fx result in the trace and then from the answer, so a "
                "number the agent never got from the tool does not pass")


def case(cid, text, expected, meta):
    return {
        "id": cid,
        "input": text,
        "expected_output": expected,
        "context": meta.pop("context", {}),
        "additional_metadata": meta,
    }


def fx_cases():
    ""
    out = []
    plan = [
        ("FX-001", "CUS-0001", 200, "EUR", "USD"),
        ("FX-002", "CUS-0002", 3000, "EUR", "USD"),
        ("FX-003", "CUS-0005", 6000, "EUR", "USD"),
        ("FX-004", "CUS-0007", 2000, "EUR", "USD"),
        ("FX-005", "CUS-0010", 5000, "GBP", "EUR"),
        ("FX-006", "CUS-0007", 1000, "EUR", "USD"),
        ("FX-007", "CUS-0007", 1001, "EUR", "USD"),
        ("FX-008", "CUS-0002", 200, "EUR", "USD"),
        ("FX-009", "CUS-0002", 201, "EUR", "USD"),
    ]
    for cid, cust, amount, frm, to in plan:
        tier, used = CUSTOMERS[cust]
        q = fx.quote(amount, frm, to, tier, allowance_used_eur=used)
        out.append(case(
            cid,
            f"I'm {cust}. Convert {amount} {frm} to {to}. "
            f"What is the final amount I receive?",
            f"{q.final_amount:.2f} {to}",
            {"layer": "generation", "oracle": "engine",
             "assertion": "tool_grounded_numeric",
             "tool": "quote_fx", "field": "final_amount",
             "expected_number": round(q.final_amount, 2), "tolerance": 0.02,
             "source": "engine", "failure_mode": "wrong_spread",
             "severity": "high", "runs": 1, "added_in": "l03",
             "gate": "daily", "context": {"customer_id": cust},
             "engine_call": (f"fx.quote({amount}, {frm!r}, {to!r}, {tier!r}, "
                             f"allowance_used_eur={used})"),
             "why_this_level": WHY_GROUNDED}))
        if q.spread_pct == 0:
            out.append(case(
                f"{cid}-S", f"I'm {cust}. What spread applies to a {amount} "
                f"{frm} conversion to {to}?",
                "no spread: the conversion is within the free allowance",
                {"layer": "generation", "oracle": "engine",
                 "assertion": "not_contains",
                 "forbidden": f"{policy.FX_SPREAD_PCT[tier]}%",
                 "source": "engine", "failure_mode": "allowance_ignored",
                 "severity": "high", "runs": 1, "added_in": "l03",
                 "gate": "daily", "context": {"customer_id": cust},
                 "engine_call": f"fx.quote(...).spread_pct == 0.0",
                 "why_this_level": "the engine says no spread is due, so the "
                                   "tier rate must not appear at all — a "
                                   "negative assertion is exact and free"}))
        else:
            out.append(case(
                f"{cid}-S", f"I'm {cust}. What spread applies to a {amount} "
                f"{frm} conversion to {to}?",
                f"{q.spread_pct}%",
                {"layer": "generation", "oracle": "engine",
                 "assertion": "contains", "source": "engine",
                 "failure_mode": "wrong_spread", "severity": "high",
                 "runs": 1, "added_in": "l03", "gate": "daily",
                 "context": {"customer_id": cust},
                 "engine_call": f"fx.FX_SPREAD_PCT[{tier!r}] via fx.quote",
                 "why_this_level": "a percentage is a short literal — level 3 "
                                   "substring is enough and free"}))
    return out


def limit_cases():
    ""
    out = []
    for cid, cust, transfers in [
        ("LIM-001", "CUS-0010",
         [{"date": date(2026, 9, 15), "amount_eur": 4914.0},
          {"date": date(2026, 9, 2), "amount_eur": 30420.0}]),
        ("LIM-002", "CUS-0001", []),
    ]:
        tier, _ = CUSTOMERS[cust]
        st = limits.status(tier, AS_OF, transfers)
        out.append(case(
            cid, f"I'm {cust}. How much of my MONTHLY transfer limit is left?",
            f"EUR {st.monthly_remaining_eur:,.2f}",
            {"layer": "generation", "oracle": "engine", "assertion": "numeric",
             "expected_number": round(st.monthly_remaining_eur, 2),
             "tolerance": 1.0, "source": "engine",
             "failure_mode": "daily_as_monthly", "severity": "high",
             "runs": 1, "added_in": "l03", "gate": "daily",
             "context": {"customer_id": cust},
             "engine_call": f"limits.status({tier!r}, {AS_OF}, transfers)",
             "why_this_level": "the monthly remainder is a computed figure; "
                               "the daily one is also valid, so the number "
                               "itself is the discriminator"}))
        out.append(case(
            f"{cid}-D", f"I'm {cust}. What is my remaining DAILY limit today?",
            f"EUR {st.daily_remaining_eur:,.2f}",
            {"layer": "generation", "oracle": "engine", "assertion": "numeric",
             "expected_number": round(st.daily_remaining_eur, 2),
             "tolerance": 1.0, "source": "engine",
             "failure_mode": "daily_as_monthly", "severity": "medium",
             "runs": 1, "added_in": "l03", "gate": "daily",
             "context": {"customer_id": cust},
             "engine_call": f"limits.status({tier!r}, {AS_OF}, transfers)",
             "why_this_level": "paired with the monthly case: together they "
                               "catch a swap that either alone would miss"}))
    return out


def dispute_cases():
    ""
    out = []
    plan = [
        ("DIS-001", "TX-0401", date(2026, 7, 20), "duplicate_charge", False),
        ("DIS-002", "TX-0402", date(2026, 7, 14), "duplicate_charge", False),
        ("DIS-003", "TX-0403", date(2026, 9, 1), "duplicate_charge", False),
        ("DIS-004", "TX-0601", date(2026, 8, 16), "goods_not_received", True),
        ("DIS-005", "TX-0701", date(2026, 9, 11), "fraud_card_not_present", False),
        ("HW-C11", "TX-0902", date(2026, 9, 12), "fraud_card_not_present", False),
        ("HW-C12", "TX-0201", date(2026, 9, 8), "duplicate_charge", False),
    ]
    for cid, tx, tx_date, reason, hold in plan:
        r = disputes.check(reason, tx_date, "settled", AS_OF, hold)
        window = policy.DISPUTE_WINDOWS_DAYS[reason]
        out.append(case(
            cid,
            f"Transaction {tx} was on {tx_date.strftime('%d %B %Y')}. "
            f"Reason: {reason.replace('_', ' ')}. What is the dispute window "
            f"for this reason code, in days?",
            f"{window} days",
            {"layer": "generation", "oracle": "engine", "assertion": "contains",
             "source": "engine", "failure_mode": "wrong_window",
             "severity": "high", "runs": 1, "added_in": "l03",
             "gate": "daily",
             "context": {"transaction_id": tx, "reason_code": reason},
             "engine_call": f"policy.DISPUTE_WINDOWS_DAYS[{reason!r}]",
             "why_this_level": "the window is a small integer the answer must "
                               "carry — level 3 substring, per the L03 ladder"}))
        if not r.eligible:
            out.append(case(
                f"{cid}-N",
                f"Transaction {tx} was on {tx_date.strftime('%d %B %Y')}. "
                f"Reason: {reason.replace('_', ' ')}. Can I still dispute it?",
                None,
                {"layer": "generation", "oracle": "engine",
                 "assertion": "not_contains",
                 "forbidden": "you can dispute",
                 "source": "engine",
                 "failure_mode": "engine_seam" if hold else "wrong_window",
                 "severity": "critical", "runs": 1, "added_in": "l03",
                 "gate": "daily",
                 "context": {"transaction_id": tx, "reason_code": reason},
                 "engine_call": (f"disputes.check({reason!r}, {tx_date}, "
                                 f"'settled', {AS_OF}, "
                                 f"compliance_hold={hold}).eligible is False"),
                 "failing_check": next(
                     (k for k, v in r.checks.items() if v.startswith("fail")),
                     "unknown"),
                 "why_this_level": "the engine refuses, so the agent must not "
                                   "offer the action — negative assertion"}))
    return out


def main():
    cases = fx_cases() + limit_cases() + dispute_cases()
    cases.append({
        "id": "HW-C13",
        "input": (
            "I'm CUS-0010. According to Verta's tariff schedule, "
            "what is the total free monthly conversion allowance "
            "for Tier 3, before subtracting any usage?"
        ),
        "expected_output": "EUR 5,000",
        "context": {
            "customer_id": "CUS-0010",
            "clock": "2026-09-15T10:00:00Z"
        },
        "additional_metadata": {
            "layer": "generation",
            "oracle": "corpus",
            "assertion": "numeric",
            "expected_number": 5000,
            "tolerance": 0,
            "source": "complaint",
            "failure_mode": "wrong_tier_allowance",
            "severity": "high",
            "runs": 1,
            "gate": "daily",
            "added_in": "hw2",
            "why_this_level": (
                "Check the published allowance numerically; "
                "no AI judge is needed."
            ),
            "reference": "app/rag/corpus/tariffs.md — Tier 3 allowance"
        }
    })

    cases.append({
        "id": "HW-C14",
        "input": (
            "List the supported dispute reason codes and tell me "
            "how many days I have to dispute a duplicate charge."
        ),
        "expected_output": (
            "Lists all supported dispute reason codes from the "
            "authorized dispute policy and explicitly states that "
            "the duplicate-charge window is 60 days. "
            "Both parts must be answered."
        ),
        "context": {
            "clock": "2026-09-15T10:00:00Z"
        },
        "additional_metadata": {
            "layer": "generation",
            "oracle": "human",
            "assertion": "judge",
            "source": "complaint",
            "failure_mode": "incomplete_multi_part_answer",
            "severity": "high",
            "runs": 5,
            "gate": "release",
            "added_in": "hw2",
            "why_this_level": (
                "A human checks whether the policy list is complete "
                "and the 60-day window clearly answers the second "
                "question. Keyword presence alone cannot establish this."
            ),
            "reference": "app/rag/corpus/disputes.md"
        }
    })

    human_plan = [
        (
            "TON-001",
            "CUS-0002",
            "I'm CUS-0002. CloudServe charged me twice on September 8, "
            "transaction TX-0201. I'm really angry—I need that money. "
            "What can you do to help?",
            "Acknowledges the duplicate charge and frustration without "
            "blaming the customer. Gives a concrete, policy-supported "
            "next step. Does not guarantee a refund.",
            "complaint",
            "dismissive_complaint_response",
            "medium"
        ),
        (
            "TON-002",
            "CUS-0006",
            "I'm CUS-0006. Check whether I can dispute TX-0601 for "
            "goods not received. If I cannot, explain what happens next.",
            "Clearly states that the dispute cannot be opened at this "
            "time and explains the escalation next step. Does not "
            "disclose a compliance review or invent its reasons.",
            "complaint",
            "unclear_or_disclosing_refusal",
            "high"
        ),
        (
            "TON-003",
            "CUS-0004",
            "I'm CUS-0004. TechMart charged me twice on July 14, "
            "transaction TX-0402. I'm frustrated that this is still "
            "unresolved. Can you open a dispute today?",
            "Respectfully explains that the 60-day duplicate-charge "
            "window expired on September 12. Clearly refuses to open "
            "the dispute on September 15 and offers a permitted next "
            "step without promising an exception or compensation.",
            "complaint",
            "misleading_expired_window_refusal",
            "high"
        ),
        (
            "TON-004",
            "CUS-0008",
            "I'm CUS-0008. I want to send EUR 1000 by SWIFT. "
            "These fees are ridiculous. Explain what Verta will charge "
            "and whether you can waive it.",
            "Acknowledges the concern without blaming the customer. "
            "Explains EUR 15 plus 0.3% of EUR 1000, totaling EUR 18 "
            "in Verta fees, separately from possible correspondent "
            "charges. Does not promise an unsupported fee waiver.",
            "edge",
            "unsupported_fee_waiver_promise",
            "high"
        )
    ]

    for cid, customer, question, expectation, source, failure, severity in human_plan:
        cases.append({
            "id": cid,
            "input": question,
            "expected_output": expectation,
            "context": {
                "customer_id": customer,
                "clock": "2026-09-15T10:00:00Z"
            },
            "additional_metadata": {
                "layer": "generation",
                "oracle": "human",
                "assertion": "judge",
                "why_this_level": (
                    "Levels 1–6 can check selected words or numbers, "
                    "but cannot reliably assess the complete meaning, "
                    "tone, clarity and appropriateness of the response."
                ),
                "source": source,
                "failure_mode": failure,
                "severity": severity,
                "runs": 5,
                "gate": "release",
                "added_in": "hw2"
            }
        })

    # Reuse the kit's direct tool-result checks for D22 and D26.
    kit_path = HERE / "sets" / "l03.jsonl"
    with kit_path.open(encoding="utf-8-sig") as source:
        for line in source:
            if not line.strip():
                continue
            kit_case = json.loads(line)
            if kit_case["id"] in {"LIM-003", "DIS-007"}:
                cases.append(kit_case)


    human_reasons = {
        "TON-001": (
            "A human checks whether the answer acknowledges this customer's "
            "anger about the duplicate charge without blaming them. "
            "Checking for words such as sorry cannot tell whether the "
            "response is respectful or dismissive."
        ),
        "TON-002": (
            "A human checks whether the refusal and escalation are clear "
            "without indirectly revealing the compliance review. "
            "A forbidden-word check can miss disclosure expressed "
            "in different words."
        ),
        "TON-003": (
            "The engine can verify the expired deadline, but a human "
            "checks whether the refusal is respectful and whether the "
            "next step implies an unsupported exception or compensation."
        ),
        "TON-004": (
            "Numeric checks can verify the EUR 18 fee, but a human "
            "checks whether the answer makes an unsupported promise "
            "to waive it, including promises expressed indirectly."
        ),
        "HW-C14": (
            "A human compares the answer with the dispute policy to "
            "check that both parts of the question are answered completely. "
            "Finding reason-code names and 60 days alone does not show "
            "whether their meaning and relationship are explained correctly."
        ),
    }

    for c in cases:
        meta = c["additional_metadata"]

        if c["id"] in human_reasons:
            meta["why_this_level"] = human_reasons[c["id"]]
        transaction_owners = {
            "TX-0401": "CUS-0004",
            "TX-0402": "CUS-0004",
            "TX-0403": "CUS-0004",
            "TX-0601": "CUS-0006",
            "TX-0701": "CUS-0007",
            "TX-0902": "CUS-0009",
            "TX-0201": "CUS-0002",
        }

        context = c.setdefault("context", {})
        transaction_id = context.get("transaction_id")

        if transaction_id in transaction_owners:
            context["customer_id"] = transaction_owners[transaction_id]

        context.setdefault("clock", "2026-09-15T10:00:00Z")
        if c["id"] in {
            "FX-006", "FX-006-S",
            "FX-007", "FX-007-S",
            "FX-008", "FX-008-S",
            "FX-009", "FX-009-S",
        }:
            meta["source"] = "edge"
            meta["added_in"] = "hw2"
            c["context"]["clock"] = "2026-09-15T10:00:00Z"
        
        if c["id"] == "HW-C11":
            meta["source"] = "complaint"
            meta["added_in"] = "hw2"
            c["context"]["customer_id"] = "CUS-0009"
            c["context"]["clock"] = "2026-09-15T10:00:00Z"
            c["input"] = (
                "I'm CUS-0009. Someone used my card online for "
                "TX-0902 at PharmaPlus. How many days do I have "
                "to dispute it as card-not-present fraud?"
            )

        if c["id"] == "HW-C12":
            meta["source"] = "complaint"
            meta["added_in"] = "hw2"
            c["context"]["customer_id"] = "CUS-0002"
            c["context"]["clock"] = "2026-09-15T10:00:00Z"
            c["input"] = (
                "I'm CUS-0002. CloudServe charged me twice on "
                "September 8, transaction TX-0201. How many days "
                "do I have to dispute it as a duplicate charge?"
            )

        c["additional_metadata"] = {k: v for k, v in meta.items() if v is not None}
        print(json.dumps(c, ensure_ascii=False))
    print(f"# {len(cases)} cases generated from the engines", file=sys.stderr)


if __name__ == "__main__":
    main()
