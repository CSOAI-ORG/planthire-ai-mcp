"""Tests for planthire-ai-mcp's new rent_equipment() agent-callable tool."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from server import rent_equipment


def test_rent_equipment_success():
    """Valid call returns ready_to_confirm with all expected fields."""
    r = rent_equipment("mini_excavator", "SW1A 1AA", 1, False, "2026-07-15")
    assert r["status"] == "ready_to_confirm"
    assert r["search"]["matched"] == 1
    assert r["quote"]["equipment"] == "mini_excavator"
    assert r["quote"]["currency"] == "GBP"
    assert r["quote"]["total_gbp"] > 0
    assert r["booking"]["booking_id"].startswith("PH-")


def test_rent_equipment_with_operator():
    """Operator adds +£420/day."""
    r = rent_equipment("telehandler", "M1 1AA", 1, True, "2026-07-15")
    # telehandler £450/day + operator £420/day + delivery £85 = £955; + 20% VAT = £1146
    assert r["quote"]["daily_rate_gbp"] == 450
    assert r["quote"]["operator_daily_gbp"] == 420
    assert r["quote"]["subtotal_gbp"] == 955
    assert r["quote"]["vat_gbp"] == 191.0
    assert r["quote"]["total_gbp"] == 1146.0


def test_rent_equipment_multi_day():
    """3-day hire of mini_excavator: 220*3 + 85 = 745; + 20% = 894."""
    r = rent_equipment("mini_excavator", "M1 1AA", 3, False, "2026-07-15")
    assert r["quote"]["hire_days"] == 3
    assert r["quote"]["subtotal_gbp"] == 745  # 220*3 + 85
    assert r["quote"]["vat_gbp"] == 149.0
    assert r["quote"]["total_gbp"] == 894.0


def test_rent_equipment_rejects_invalid_postcode():
    r = rent_equipment("mini_excavator", "NOTREAL", 1, False, "2026-07-15")
    assert r["status"] == "rejected"
    assert r["reason"] == "invalid_postcode"


def test_rent_equipment_rejects_zero_days():
    r = rent_equipment("mini_excavator", "M1 1AA", 0, False, "2026-07-15")
    assert r["status"] == "rejected"
    assert r["reason"] == "invalid_hire_days"


def test_rent_equipment_rejects_unknown_type():
    r = rent_equipment("teleportation_device", "M1 1AA", 1, False, "2026-07-15")
    assert r["status"] == "rejected"
    assert r["reason"] == "unknown_equipment_type"
    assert "mini_excavator" in r["valid"]


def test_rent_equipment_rejects_bad_date():
    r = rent_equipment("mini_excavator", "M1 1AA", 1, False, "07/15/2026")
    assert r["status"] == "rejected"
    assert r["reason"] == "invalid_date"


def test_rent_equipment_safety_checklist_present():
    """PUWER 1998 + LOLER 1998 + CITB SMSTS + HSG144."""
    r = rent_equipment("mini_excavator", "M1 1AA", 1, False, "2026-07-15")
    assert "PUWER 1998" in r["safety"]["regulations"]
    assert "LOLER 1998" in r["safety"]["regulations"]
    assert "CITB SMSTS" in r["safety"]["regulations"]
    assert "HSG144" in r["safety"]["regulations"]
    # Checklist has at least 5 items (PUWER requires pre-use + thorough exam + operator + PPE)
    assert len(r["safety"]["checklist"]) >= 5


def test_rent_equipment_agent_metadata():
    """x402 pay-per-call, agent-callable signature."""
    r = rent_equipment("mini_excavator", "M1 1AA", 1, False, "2026-07-15")
    assert r["agent_metadata"]["x402_price_usd"] == 0.05
    assert r["agent_metadata"]["for_agent"] == "other_llm_can_call"
    assert r["agent_metadata"]["tool_id"] == "planthire.rent_equipment.v1"


def test_rent_equipment_all_equipment_types_priced():
    """Every documented equipment type produces a non-zero quote."""
    types = [
        "mini_excavator", "1t_dumper", "3t_dumper", "telehandler",
        "roller", "scissor_lift", "boom_lift", "genset", "compactor",
    ]
    for et in types:
        r = rent_equipment(et, "M1 1AA", 1, False, "2026-07-15")
        assert r["status"] == "ready_to_confirm", f"{et} should succeed"
        assert r["quote"]["daily_rate_gbp"] > 0, f"{et} should have a rate"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))