import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import AgenticSystem

# ─────────────────────────────────────────────────────────────────────────────
# Eval rubric:
#   route_correct  — did the router pick the right tool?
#   has_response   — did both EN and AR responses come back non-empty?
#   escalation_ok  — for refund/complaint, is needs_human=True?
#   uncertainty_ok — for adversarial/out-of-scope, is confidence < 0.8?
# ─────────────────────────────────────────────────────────────────────────────

TEST_CASES = [
    # (query, expected_route, description, check_escalation, check_uncertainty)
    # ── Gift Finder — Easy ────────────────────────────────────────────────────
    ("I want a gift for a newborn baby girl",               "gift_finder", "EN gift · newborn",          False, False),
    ("Lego toys for a 2 year old boy",                      "gift_finder", "EN gift · toddler toys",     False, False),
    ("Budget friendly diapers for 6 month old",             "gift_finder", "EN gift · budget diapers",   False, False),
    ("Recommendations for a first time mom under 300 AED",  "gift_finder", "EN gift · new mom budget",   False, False),
    ("أريد شراء هدية لطفل عمره سنتين",                     "gift_finder", "AR gift · toddler",          False, False),
    ("هدية للأم الجديدة بميزانية 200 درهم",                 "gift_finder", "AR gift · new mom",          False, False),

    # ── Support — Easy ────────────────────────────────────────────────────────
    ("Where is my order #12345?",                           "support",     "EN support · order status",  False, False),
    ("I want a refund for my damaged stroller",             "support",     "EN support · refund",        True,  False),
    ("My delivery is late and I am very angry",             "support",     "EN support · complaint",     True,  False),
    ("هل يمكنني استرجاع المنتج؟",                           "support",     "AR support · return/refund", True,  False),

    # ── Adversarial / Out-of-scope ────────────────────────────────────────────
    ("What is the weather in Dubai today?",                 "support",     "Out-of-scope · weather",     False, True),
    ("Hello",                                               "support",     "Ambiguous · greeting",       False, True),
]


def score_result(result: dict, check_escalation: bool, check_uncertainty: bool) -> dict:
    """Return individual rubric scores for one test case."""
    scores = {}
    scores["route_correct"] = result.get("route_correct", False)
    scores["has_response"]  = bool(result.get("response_en")) and bool(result.get("response_ar"))

    if check_escalation:
        scores["escalation_ok"] = result.get("needs_human", False) is True
    else:
        scores["escalation_ok"] = None   # N/A

    if check_uncertainty:
        conf = result.get("confidence", 1.0)
        scores["uncertainty_ok"] = (conf < 0.8) if conf != "N/A" else False
    else:
        scores["uncertainty_ok"] = None  # N/A

    return scores


def run_evaluation():
    print("\n" + "=" * 78)
    print("  Mumzworld AI Copilot — Evaluation Report")
    print(f"  Model:   Groq / llama-3.3-70b-versatile")
    print(f"  Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 78)

    system = AgenticSystem()
    results = []

    passed_route   = 0
    passed_total   = 0   # all rubric checks that apply
    checked_total  = 0
    errors         = 0

    print(f"\n{'#':<3} {'Query':<43} {'Exp':<13} {'Got':<13} {'R'} {'Rsp'} {'Esc'} {'Unc'}")
    print("-" * 84)

    for i, (query, expected_route, desc, check_esc, check_unc) in enumerate(TEST_CASES, 1):
        try:
            response = system.handle_query(query)
            conf     = response.output.get("confidence", "N/A")
            got      = response.route

            result_entry = {
                "id":             i,
                "description":    desc,
                "input":          query,
                "expected_route": expected_route,
                "got_route":      got,
                "route_correct":  got == expected_route,
                "confidence":     conf,
                "response_en":    response.response_en,
                "response_ar":    response.response_ar,
                "needs_human":    response.output.get("needs_human"),
                "intent":         response.output.get("intent"),
            }

            scores = score_result(result_entry, check_esc, check_unc)

            # Tally
            for k, v in scores.items():
                if v is not None:
                    checked_total += 1
                    if v:
                        passed_total += 1
            if scores["route_correct"]:
                passed_route += 1

            def fmt(v): return "✅" if v is True else ("❌" if v is False else "—")

            short = (query[:40] + "…") if len(query) > 40 else query
            print(f"{i:<3} {short:<43} {expected_route:<13} {got:<13} "
                  f"{fmt(scores['route_correct'])} {fmt(scores['has_response'])} "
                  f"{fmt(scores['escalation_ok'])} {fmt(scores['uncertainty_ok'])}")

            result_entry["scores"] = scores
            results.append(result_entry)

        except Exception as e:
            errors += 1
            short = (query[:40] + "…") if len(query) > 40 else query
            print(f"{i:<3} {short:<43} {expected_route:<13} {'ERROR':<13} 💥 {e}")
            results.append({"id": i, "input": query, "error": str(e)})

    # ── Summary ──────────────────────────────────────────────────────────────
    route_pct = round(passed_route / len(TEST_CASES) * 100, 1)
    total_pct = round(passed_total / checked_total * 100, 1) if checked_total else 0

    print("\n" + "=" * 78)
    print(f"  Routing accuracy:   {passed_route}/{len(TEST_CASES)}  ({route_pct}%)")
    print(f"  All-rubric score:   {passed_total}/{checked_total} checks  ({total_pct}%)")
    print(f"  Errors:             {errors}")
    print("\n  Rubric columns: R=Route  Rsp=Has Response  Esc=Escalation  Unc=Uncertainty")
    print("=" * 78 + "\n")

    # ── Save JSON ─────────────────────────────────────────────────────────────
    os.makedirs("data", exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"data/eval_results_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_cases":    len(TEST_CASES),
                "passed_route":   passed_route,
                "route_pct":      route_pct,
                "all_rubric_pct": total_pct,
                "errors":         errors,
                "model":          "Groq / llama-3.3-70b-versatile",
                "timestamp":      datetime.now().isoformat(),
            },
            "rubric": {
                "route_correct":  "Router picked the expected tool",
                "has_response":   "Both EN and AR responses are non-empty",
                "escalation_ok":  "Refund/complaint always sets needs_human=True",
                "uncertainty_ok": "Out-of-scope queries return confidence < 0.8",
            },
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    print(f"  Detailed results → {out_path}\n")


if __name__ == "__main__":
    run_evaluation()
