from __future__ import annotations

from typing import Any, Dict, List, Tuple, Optional

from app.models import Ticket, Rule, RoutingDecision


# -------------------------
# Helpers
# -------------------------

def _get_field_value(ticket: Ticket, field: str) -> Any:
    """
    Extracts a field value from the Ticket.
    Special field: 'text' -> ticket.text (title + description lowercased).
    """
    if field == "text":
        return ticket.text

    # Pydantic models support attribute access; fallback to dict access
    if hasattr(ticket, field):
        return getattr(ticket, field)

    data = ticket.model_dump()
    return data.get(field)


def _normalize_str(val: Any) -> str:
    return str(val).lower().strip()


def _contains(haystack: Any, needle: Any) -> bool:
    if haystack is None:
        return False
    return _normalize_str(needle) in _normalize_str(haystack)


def _contains_any(haystack: Any, needles: List[Any]) -> Tuple[bool, List[str]]:
    """
    Returns (matched?, matched_keywords)
    """
    if haystack is None:
        return False, []

    hay = _normalize_str(haystack)
    matched = []
    for n in needles:
        kw = _normalize_str(n)
        if kw and kw in hay:
            matched.append(kw)

    return len(matched) > 0, matched


# -------------------------
# DSL Condition Evaluation
# -------------------------

def evaluate_condition(ticket: Ticket, condition: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Evaluates a single condition:
      {"field": "department", "op": "eq", "value": "IT"}
      {"field": "text", "op": "contains_any", "value": ["vpn", "wifi"]}
    Returns: (result, evidence)
    """
    field = condition.get("field")
    op = condition.get("op")
    expected = condition.get("value")

    if not field or not op:
        return False, {"error": "Invalid condition: missing 'field' or 'op'", "condition": condition}

    actual = _get_field_value(ticket, field)

    evidence: Dict[str, Any] = {
        "field": field,
        "op": op,
        "expected": expected,
        "actual": actual,
    }

    # Operators
    if op == "eq":
        result = actual == expected
        return result, evidence

    if op == "neq":
        result = actual != expected
        return result, evidence

    if op == "in":
        # expected should be list-like
        if not isinstance(expected, list):
            return False, {**evidence, "error": "Operator 'in' expects list in 'value'"}
        result = actual in expected
        return result, evidence

    if op == "contains":
        result = _contains(actual, expected)
        return result, evidence

    if op == "contains_any":
        if not isinstance(expected, list):
            return False, {**evidence, "error": "Operator 'contains_any' expects list in 'value'"}
        result, matched_keywords = _contains_any(actual, expected)
        evidence["matched_keywords"] = matched_keywords
        return result, evidence

    return False, {**evidence, "error": f"Unsupported operator '{op}'"}


def evaluate_conditions(ticket: Ticket, conditions: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Evaluates group conditions:
      {"all": [cond1, cond2]}  -> AND
      {"any": [cond1, cond2]}  -> OR

    Returns (matched?, evidence)
    """
    if not isinstance(conditions, dict):
        return False, {"error": "Conditions must be a dict", "conditions": conditions}

    if "all" in conditions:
        cond_list = conditions.get("all") or []
        evidence_list = []
        for c in cond_list:
            ok, ev = evaluate_condition(ticket, c)
            evidence_list.append({"ok": ok, "evidence": ev})
            if not ok:
                return False, {"mode": "all", "checks": evidence_list}
        return True, {"mode": "all", "checks": evidence_list}

    if "any" in conditions:
        cond_list = conditions.get("any") or []
        evidence_list = []
        for c in cond_list:
            ok, ev = evaluate_condition(ticket, c)
            evidence_list.append({"ok": ok, "evidence": ev})
            if ok:
                return True, {"mode": "any", "checks": evidence_list}
        return False, {"mode": "any", "checks": evidence_list}

    return False, {"error": "Conditions must contain either 'all' or 'any'", "conditions": conditions}


# -------------------------
# Rule Matching + Routing
# -------------------------

def match_rule(ticket: Ticket, rule: Rule) -> Tuple[bool, Dict[str, Any]]:
    """
    Returns (matched?, evidence)
    """
    if not rule.enabled:
        return False, {"skipped": True, "reason": "rule disabled", "rule_id": rule.id}

    matched, evidence = evaluate_conditions(ticket, rule.conditions)
    evidence["rule_id"] = rule.id
    evidence["rule_name"] = rule.name
    evidence["priority_order"] = rule.priority_order
    return matched, evidence


def route_ticket(ticket: Ticket, rules: List[Rule]) -> RoutingDecision:
    """
    First-match-wins routing engine.
    Evaluates enabled rules in ascending priority_order.
    Returns RoutingDecision with explainability.
    """
    # Sort by priority_order (low first)
    ordered = sorted(rules, key=lambda r: r.priority_order)

    evaluated = 0
    for rule in ordered:
        evaluated += 1
        matched, evidence = match_rule(ticket, rule)

        if matched:
            team = rule.action.get("route_to_team")
            decision = RoutingDecision(
                team=team,
                matched_rule_id=rule.id,
                matched_rule_name=rule.name,
                reason={
                    "matched": True,
                    "evidence": evidence,
                },
                meta={
                    "evaluated_rules": evaluated,
                    "mode": "first_match_wins",
                },
            )
            return decision

    # No match fallback
    return RoutingDecision(
        team=None,
        matched_rule_id=None,
        matched_rule_name=None,
        reason={
            "matched": False,
            "message": "No routing rule matched the ticket",
        },
        meta={
            "evaluated_rules": evaluated,
            "mode": "first_match_wins",
        },
    )