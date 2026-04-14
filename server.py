"""
PlantHire.AI MCP Server - Construction Equipment AI
Built by MEOK AI Labs | https://planthire.ai

Intelligent construction equipment search, rental quoting,
availability checking, booking, safety, and transport costing.
"""


import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import math
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "planthire-ai")

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
_RATE_LIMITS = {
    "free": {"requests_per_hour": 60, "bookings_per_day": 5},
    "pro": {"requests_per_hour": 10000, "bookings_per_day": 500},
}
_request_log: list[float] = []
_tier = "free"


def _check_rate_limit() -> bool:
    now = time.time()
    _request_log[:] = [t for t in _request_log if now - t < 3600]
    if len(_request_log) >= _RATE_LIMITS[_tier]["requests_per_hour"]:
        return False
    _request_log.append(now)
    return True


# ---------------------------------------------------------------------------
# Equipment catalog - real UK plant hire data
# ---------------------------------------------------------------------------
_EQUIPMENT_CATALOG = {
    # Mini/Midi Excavators
    "micro_excavator": {
        "name": "Micro Excavator (0.8-1t)",
        "category": "excavators",
        "subcategory": "micro",
        "weight_tonnes": 0.9,
        "dig_depth_m": 1.5,
        "bucket_capacity_m3": 0.02,
        "transport_class": "trailer",
        "rates": {"daily": 95, "weekly": 380, "monthly": 1140},
        "fuel_type": "diesel",
        "requires_licence": False,
        "typical_uses": ["landscaping", "utility trenches", "indoor demolition"],
    },
    "mini_excavator_1.5t": {
        "name": "Mini Excavator (1.5t)",
        "category": "excavators",
        "subcategory": "mini",
        "weight_tonnes": 1.5,
        "dig_depth_m": 2.2,
        "bucket_capacity_m3": 0.04,
        "transport_class": "trailer",
        "rates": {"daily": 120, "weekly": 480, "monthly": 1440},
        "fuel_type": "diesel",
        "requires_licence": False,
        "typical_uses": ["driveways", "footings", "drainage"],
    },
    "mini_excavator_3t": {
        "name": "Mini Excavator (3t)",
        "category": "excavators",
        "subcategory": "mini",
        "weight_tonnes": 3.0,
        "dig_depth_m": 3.0,
        "bucket_capacity_m3": 0.08,
        "transport_class": "flatbed",
        "rates": {"daily": 160, "weekly": 640, "monthly": 1920},
        "fuel_type": "diesel",
        "requires_licence": False,
        "typical_uses": ["house foundations", "swimming pools", "site clearance"],
    },
    "midi_excavator_5t": {
        "name": "Midi Excavator (5t)",
        "category": "excavators",
        "subcategory": "midi",
        "weight_tonnes": 5.0,
        "dig_depth_m": 3.8,
        "bucket_capacity_m3": 0.15,
        "transport_class": "low_loader",
        "rates": {"daily": 220, "weekly": 880, "monthly": 2640},
        "fuel_type": "diesel",
        "requires_licence": False,
        "typical_uses": ["commercial foundations", "road works", "demolition"],
    },
    "excavator_8t": {
        "name": "Tracked Excavator (8t)",
        "category": "excavators",
        "subcategory": "standard",
        "weight_tonnes": 8.0,
        "dig_depth_m": 4.5,
        "bucket_capacity_m3": 0.28,
        "transport_class": "low_loader",
        "rates": {"daily": 320, "weekly": 1280, "monthly": 3840},
        "fuel_type": "diesel",
        "requires_licence": True,
        "typical_uses": ["large excavations", "demolition", "bulk earthworks"],
    },
    "excavator_14t": {
        "name": "Tracked Excavator (14t)",
        "category": "excavators",
        "subcategory": "standard",
        "weight_tonnes": 14.0,
        "dig_depth_m": 5.8,
        "bucket_capacity_m3": 0.5,
        "transport_class": "low_loader",
        "rates": {"daily": 450, "weekly": 1800, "monthly": 5400},
        "fuel_type": "diesel",
        "requires_licence": True,
        "typical_uses": ["major earthworks", "quarry", "infrastructure"],
    },
    "excavator_20t": {
        "name": "Tracked Excavator (20t)",
        "category": "excavators",
        "subcategory": "heavy",
        "weight_tonnes": 20.0,
        "dig_depth_m": 6.5,
        "bucket_capacity_m3": 0.9,
        "transport_class": "heavy_haulage",
        "rates": {"daily": 600, "weekly": 2400, "monthly": 7200},
        "fuel_type": "diesel",
        "requires_licence": True,
        "typical_uses": ["motorway construction", "quarry", "large demolition"],
    },
    # Dumpers
    "site_dumper_1t": {
        "name": "High-Tip Skip Dumper (1t)",
        "category": "dumpers",
        "subcategory": "site",
        "weight_tonnes": 1.0,
        "payload_tonnes": 1.0,
        "transport_class": "trailer",
        "rates": {"daily": 75, "weekly": 300, "monthly": 900},
        "fuel_type": "diesel",
        "requires_licence": False,
        "typical_uses": ["site muck-away", "landscaping", "material movement"],
    },
    "site_dumper_3t": {
        "name": "Swivel Skip Dumper (3t)",
        "category": "dumpers",
        "subcategory": "site",
        "weight_tonnes": 2.8,
        "payload_tonnes": 3.0,
        "transport_class": "flatbed",
        "rates": {"daily": 110, "weekly": 440, "monthly": 1320},
        "fuel_type": "diesel",
        "requires_licence": False,
        "typical_uses": ["housing sites", "road construction", "material movement"],
    },
    "site_dumper_6t": {
        "name": "Forward Tip Dumper (6t)",
        "category": "dumpers",
        "subcategory": "site",
        "weight_tonnes": 5.5,
        "payload_tonnes": 6.0,
        "transport_class": "low_loader",
        "rates": {"daily": 160, "weekly": 640, "monthly": 1920},
        "fuel_type": "diesel",
        "requires_licence": True,
        "typical_uses": ["large housing developments", "earthworks", "infrastructure"],
    },
    "site_dumper_9t": {
        "name": "Cabbed Dumper (9t)",
        "category": "dumpers",
        "subcategory": "site",
        "weight_tonnes": 8.0,
        "payload_tonnes": 9.0,
        "transport_class": "low_loader",
        "rates": {"daily": 220, "weekly": 880, "monthly": 2640},
        "fuel_type": "diesel",
        "requires_licence": True,
        "typical_uses": ["motorway works", "large earthmoving", "quarry"],
    },
    # Telehandlers
    "telehandler_6m": {
        "name": "Telehandler 6m / 2.5t",
        "category": "telehandlers",
        "subcategory": "compact",
        "weight_tonnes": 5.5,
        "max_lift_height_m": 6.0,
        "max_lift_capacity_kg": 2500,
        "transport_class": "low_loader",
        "rates": {"daily": 180, "weekly": 720, "monthly": 2160},
        "fuel_type": "diesel",
        "requires_licence": True,
        "typical_uses": ["house building", "roofing", "material handling"],
    },
    "telehandler_10m": {
        "name": "Telehandler 10m / 3.5t",
        "category": "telehandlers",
        "subcategory": "standard",
        "weight_tonnes": 8.0,
        "max_lift_height_m": 10.0,
        "max_lift_capacity_kg": 3500,
        "transport_class": "low_loader",
        "rates": {"daily": 250, "weekly": 1000, "monthly": 3000},
        "fuel_type": "diesel",
        "requires_licence": True,
        "typical_uses": ["commercial builds", "steelwork", "cladding"],
    },
    "telehandler_14m": {
        "name": "Telehandler 14m / 4t",
        "category": "telehandlers",
        "subcategory": "heavy",
        "weight_tonnes": 11.0,
        "max_lift_height_m": 14.0,
        "max_lift_capacity_kg": 4000,
        "transport_class": "low_loader",
        "rates": {"daily": 340, "weekly": 1360, "monthly": 4080},
        "fuel_type": "diesel",
        "requires_licence": True,
        "typical_uses": ["multi-storey", "industrial builds", "heavy lifting"],
    },
    # Rollers
    "roller_single_drum": {
        "name": "Single Drum Roller (2.5t)",
        "category": "compaction",
        "subcategory": "roller",
        "weight_tonnes": 2.5,
        "drum_width_mm": 1200,
        "transport_class": "flatbed",
        "rates": {"daily": 130, "weekly": 520, "monthly": 1560},
        "fuel_type": "diesel",
        "requires_licence": False,
        "typical_uses": ["road sub-base", "trench reinstatement", "car parks"],
    },
    "roller_tandem": {
        "name": "Tandem Roller (2.5t)",
        "category": "compaction",
        "subcategory": "roller",
        "weight_tonnes": 2.5,
        "drum_width_mm": 1000,
        "transport_class": "flatbed",
        "rates": {"daily": 140, "weekly": 560, "monthly": 1680},
        "fuel_type": "diesel",
        "requires_licence": False,
        "typical_uses": ["asphalt finishing", "car parks", "footpaths"],
    },
    # Generators
    "generator_20kva": {
        "name": "Silenced Generator 20kVA",
        "category": "power",
        "subcategory": "generator",
        "output_kva": 20,
        "weight_tonnes": 0.6,
        "transport_class": "van",
        "rates": {"daily": 55, "weekly": 220, "monthly": 660},
        "fuel_type": "diesel",
        "requires_licence": False,
        "typical_uses": ["site welfare", "small tools", "temporary power"],
    },
    "generator_60kva": {
        "name": "Silenced Generator 60kVA",
        "category": "power",
        "subcategory": "generator",
        "output_kva": 60,
        "weight_tonnes": 1.2,
        "transport_class": "flatbed",
        "rates": {"daily": 95, "weekly": 380, "monthly": 1140},
        "fuel_type": "diesel",
        "requires_licence": False,
        "typical_uses": ["tower cranes", "concrete pumps", "site compounds"],
    },
    "generator_100kva": {
        "name": "Silenced Generator 100kVA",
        "category": "power",
        "subcategory": "generator",
        "output_kva": 100,
        "weight_tonnes": 2.0,
        "transport_class": "flatbed",
        "rates": {"daily": 140, "weekly": 560, "monthly": 1680},
        "fuel_type": "diesel",
        "requires_licence": False,
        "typical_uses": ["large sites", "events", "data centres"],
    },
    # Access
    "scissor_lift_8m": {
        "name": "Electric Scissor Lift (8m)",
        "category": "access",
        "subcategory": "scissor_lift",
        "working_height_m": 8.0,
        "weight_tonnes": 1.8,
        "transport_class": "flatbed",
        "rates": {"daily": 95, "weekly": 380, "monthly": 1140},
        "fuel_type": "electric",
        "requires_licence": True,
        "typical_uses": ["fit-out", "M&E installation", "painting"],
    },
    "cherry_picker_12m": {
        "name": "Articulated Boom Lift (12m)",
        "category": "access",
        "subcategory": "boom_lift",
        "working_height_m": 12.0,
        "weight_tonnes": 5.5,
        "transport_class": "low_loader",
        "rates": {"daily": 180, "weekly": 720, "monthly": 2160},
        "fuel_type": "diesel",
        "requires_licence": True,
        "typical_uses": ["cladding", "steelwork", "tree surgery"],
    },
    # Skid Steer
    "skid_steer": {
        "name": "Skid Steer Loader",
        "category": "loaders",
        "subcategory": "skid_steer",
        "weight_tonnes": 3.2,
        "bucket_capacity_m3": 0.4,
        "transport_class": "flatbed",
        "rates": {"daily": 170, "weekly": 680, "monthly": 2040},
        "fuel_type": "diesel",
        "requires_licence": True,
        "typical_uses": ["site clearance", "landscaping", "snow clearing"],
    },
}

# Simulated depot locations
_DEPOTS = {
    "london": {"name": "London (Barking)", "lat": 51.54, "lon": 0.08},
    "birmingham": {"name": "Birmingham (Aston)", "lat": 52.50, "lon": -1.88},
    "manchester": {"name": "Manchester (Trafford)", "lat": 53.46, "lon": -2.27},
    "bristol": {"name": "Bristol (Avonmouth)", "lat": 51.50, "lon": -2.70},
    "glasgow": {"name": "Glasgow (Rutherglen)", "lat": 55.83, "lon": -4.21},
    "leeds": {"name": "Leeds (Stourton)", "lat": 53.77, "lon": -1.52},
    "cardiff": {"name": "Cardiff (Tremorfa)", "lat": 51.48, "lon": -3.15},
    "edinburgh": {"name": "Edinburgh (Newbridge)", "lat": 55.94, "lon": -3.40},
}

# In-memory bookings
_bookings: dict[str, dict] = {}

# Simulated availability (all equipment starts available)
_availability: dict[str, list[dict]] = {}  # equipment_id -> list of booked periods


# ---------------------------------------------------------------------------
# Safety checklists - based on real HSE / CPCS guidelines
# ---------------------------------------------------------------------------
_SAFETY_CHECKLISTS = {
    "excavators": {
        "name": "Excavator Pre-Use Inspection",
        "regulation": "PUWER 1998, LOLER 1998",
        "checks": [
            {"item": "Walk-around visual inspection for damage/leaks", "critical": True},
            {"item": "Check hydraulic hoses and fittings for wear/leaks", "critical": True},
            {"item": "Inspect tracks/wheels for damage and correct tension", "critical": True},
            {"item": "Check bucket teeth and cutting edge wear", "critical": False},
            {"item": "Test all controls from operator seat before moving", "critical": True},
            {"item": "Check mirrors and reversing camera function", "critical": True},
            {"item": "Verify ROPS/FOPS cab protection intact", "critical": True},
            {"item": "Check seatbelt condition and function", "critical": True},
            {"item": "Test horn, beacons, and work lights", "critical": True},
            {"item": "Check engine oil, coolant, hydraulic fluid levels", "critical": True},
            {"item": "Inspect quick-hitch mechanism and safety pin", "critical": True},
            {"item": "Check fire extinguisher present and in-date", "critical": True},
            {"item": "Verify ground conditions suitable for operation", "critical": True},
            {"item": "Check for overhead power lines and underground services", "critical": True},
            {"item": "Confirm exclusion zone established", "critical": True},
        ],
    },
    "dumpers": {
        "name": "Site Dumper Pre-Use Inspection",
        "regulation": "PUWER 1998, HSE GS6",
        "checks": [
            {"item": "Walk-around visual check for damage and leaks", "critical": True},
            {"item": "Check tyre pressures and condition", "critical": True},
            {"item": "Test brakes (service and parking)", "critical": True},
            {"item": "Check steering for excessive play", "critical": True},
            {"item": "Test skip tip mechanism and lock", "critical": True},
            {"item": "Verify ROPS fitted and secure", "critical": True},
            {"item": "Check seatbelt present and functional", "critical": True},
            {"item": "Test horn, lights, and beacons", "critical": True},
            {"item": "Check engine oil and coolant levels", "critical": True},
            {"item": "Inspect haul routes for gradients and obstructions", "critical": True},
            {"item": "Check load limit marking visible", "critical": False},
            {"item": "Verify driver holds valid CPCS/NPORS card", "critical": True},
        ],
    },
    "telehandlers": {
        "name": "Telehandler Pre-Use Inspection",
        "regulation": "PUWER 1998, LOLER 1998, BS 7121",
        "checks": [
            {"item": "Walk-around visual inspection", "critical": True},
            {"item": "Check boom and extension for damage/wear", "critical": True},
            {"item": "Inspect hydraulic hoses and cylinders", "critical": True},
            {"item": "Check tyre pressures and condition (all four)", "critical": True},
            {"item": "Test load moment indicator (LMI) function", "critical": True},
            {"item": "Verify rated capacity chart visible in cab", "critical": True},
            {"item": "Test all boom functions through full range", "critical": True},
            {"item": "Check attachment locking mechanism", "critical": True},
            {"item": "Test brakes and steering", "critical": True},
            {"item": "Check mirrors, cameras, and proximity sensors", "critical": True},
            {"item": "Verify ROPS/FOPS protection", "critical": True},
            {"item": "Check seatbelt", "critical": True},
            {"item": "Test horn, beacons, and lights", "critical": True},
            {"item": "Check ground conditions and outriggers if fitted", "critical": True},
            {"item": "Confirm CPCS A17 or equivalent held by operator", "critical": True},
        ],
    },
    "compaction": {
        "name": "Roller Pre-Use Inspection",
        "regulation": "PUWER 1998",
        "checks": [
            {"item": "Visual inspection for damage and leaks", "critical": True},
            {"item": "Check drum(s) for damage and scraper bar clearance", "critical": True},
            {"item": "Test vibration system engagement/disengagement", "critical": True},
            {"item": "Check water spray system and tank level", "critical": False},
            {"item": "Test brakes (service and parking)", "critical": True},
            {"item": "Check steering function", "critical": True},
            {"item": "Test horn and beacons", "critical": True},
            {"item": "Check ROPS if fitted", "critical": True},
            {"item": "Verify operator competence (CPCS or NPORS)", "critical": True},
        ],
    },
    "access": {
        "name": "MEWP Pre-Use Inspection",
        "regulation": "PUWER 1998, LOLER 1998, IPAF guidelines",
        "checks": [
            {"item": "Visual inspection of structure for damage/cracks", "critical": True},
            {"item": "Check platform guardrails and gate secure", "critical": True},
            {"item": "Test ground controls and platform controls", "critical": True},
            {"item": "Check emergency lowering system", "critical": True},
            {"item": "Test tilt alarm/cut-out", "critical": True},
            {"item": "Check outriggers/stabilisers if fitted", "critical": True},
            {"item": "Inspect hydraulic hoses and cylinders", "critical": True},
            {"item": "Test function through full range of travel", "critical": True},
            {"item": "Check battery charge (electric) or fuel (diesel)", "critical": True},
            {"item": "Verify harness and lanyard condition", "critical": True},
            {"item": "Check ground conditions and gradient", "critical": True},
            {"item": "Confirm IPAF PAL card held by operator", "critical": True},
            {"item": "Check for overhead obstructions", "critical": True},
        ],
    },
    "power": {
        "name": "Generator Pre-Use Inspection",
        "regulation": "PUWER 1998, Electricity at Work Regulations 1989",
        "checks": [
            {"item": "Visual inspection for damage, leaks, loose panels", "critical": True},
            {"item": "Check fuel level and condition", "critical": True},
            {"item": "Check engine oil and coolant levels", "critical": True},
            {"item": "Inspect electrical connections and cable condition", "critical": True},
            {"item": "Test RCD/ELCB trip function", "critical": True},
            {"item": "Check earthing/grounding connection", "critical": True},
            {"item": "Verify output voltage and frequency correct", "critical": True},
            {"item": "Check exhaust system routing (CO risk)", "critical": True},
            {"item": "Ensure adequate ventilation around unit", "critical": True},
            {"item": "Check fire extinguisher present nearby", "critical": True},
        ],
    },
    "loaders": {
        "name": "Skid Steer / Loader Pre-Use Inspection",
        "regulation": "PUWER 1998",
        "checks": [
            {"item": "Walk-around visual inspection", "critical": True},
            {"item": "Check hydraulic hoses and connections", "critical": True},
            {"item": "Inspect tyres/tracks for damage", "critical": True},
            {"item": "Test safety bar/restraint system", "critical": True},
            {"item": "Check bucket/attachment locking pins", "critical": True},
            {"item": "Test all controls and safety interlocks", "critical": True},
            {"item": "Check mirrors and rear visibility", "critical": True},
            {"item": "Test horn, beacons, and lights", "critical": True},
            {"item": "Check fluid levels (engine oil, hydraulic, coolant)", "critical": True},
            {"item": "Verify ROPS/FOPS intact", "critical": True},
            {"item": "Confirm operator holds CPCS A23 or equivalent", "critical": True},
        ],
    },
}

# Transport cost matrix
_TRANSPORT_COSTS = {
    "van": {"base": 45, "per_mile": 1.20, "max_distance_miles": 100},
    "trailer": {"base": 65, "per_mile": 1.50, "max_distance_miles": 150},
    "flatbed": {"base": 120, "per_mile": 2.00, "max_distance_miles": 250},
    "low_loader": {"base": 220, "per_mile": 3.20, "max_distance_miles": 400},
    "heavy_haulage": {"base": 450, "per_mile": 5.50, "max_distance_miles": 500},
}


# ===========================================================================
# MCP Tools
# ===========================================================================


@mcp.tool()
def search_equipment(
    query: Optional[str] = None,
    category: Optional[str] = None,
    max_weight_tonnes: Optional[float] = None,
    min_dig_depth_m: Optional[float] = None,
    max_daily_rate: Optional[float] = None,
    requires_licence: Optional[bool] = None, api_key: str = "") -> dict:
    """Search the construction equipment catalog.

    Filter by category, weight, capabilities, and price. Categories include:
    excavators, dumpers, telehandlers, compaction, power, access, loaders.

    Args:
        query: Free-text search (matches name, uses, category).
        category: Equipment category filter.
        max_weight_tonnes: Maximum operating weight in tonnes.
        min_dig_depth_m: Minimum dig depth (excavators only).
        max_daily_rate: Maximum daily hire rate in GBP.
        requires_licence: Filter by licence requirement.

    Returns:
        Matching equipment with specs and rates.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _check_rate_limit():
        return {"error": "Rate limit exceeded. Upgrade to Pro at https://planthire.ai/pricing"}

    results = []
    for eq_id, eq in _EQUIPMENT_CATALOG.items():
        # Category filter
        if category and eq["category"] != category.lower():
            continue

        # Weight filter
        if max_weight_tonnes and eq["weight_tonnes"] > max_weight_tonnes:
            continue

        # Dig depth filter
        if min_dig_depth_m and eq.get("dig_depth_m", 0) < min_dig_depth_m:
            continue

        # Rate filter
        if max_daily_rate and eq["rates"]["daily"] > max_daily_rate:
            continue

        # Licence filter
        if requires_licence is not None and eq["requires_licence"] != requires_licence:
            continue

        # Free-text search
        if query:
            q = query.lower()
            searchable = f"{eq['name']} {eq['category']} {eq['subcategory']} {' '.join(eq['typical_uses'])}".lower()
            if q not in searchable:
                continue

        results.append({"equipment_id": eq_id, **eq})

    return {
        "results": results,
        "count": len(results),
        "filters_applied": {
            "query": query,
            "category": category,
            "max_weight_tonnes": max_weight_tonnes,
            "min_dig_depth_m": min_dig_depth_m,
            "max_daily_rate": max_daily_rate,
        },
        "powered_by": "planthire.ai",
    }


@mcp.tool()
def get_rental_quote(
    equipment_id: str,
    duration_days: int,
    include_insurance: bool = True,
    include_fuel: bool = False,
    operator_required: bool = False, api_key: str = "") -> dict:
    """Calculate rental pricing for equipment.

    Applies tiered pricing: daily rate for 1-6 days, weekly rate for 7-27,
    monthly rate for 28+. Includes optional insurance, fuel, and operator costs.

    Args:
        equipment_id: ID from search_equipment results.
        duration_days: Number of hire days.
        include_insurance: Add damage waiver insurance (default True).
        include_fuel: Include estimated fuel costs.
        operator_required: Include CPCS-carded operator.

    Returns:
        Detailed pricing breakdown in GBP.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _check_rate_limit():
        return {"error": "Rate limit exceeded."}

    eq = _EQUIPMENT_CATALOG.get(equipment_id)
    if not eq:
        return {"error": f"Equipment '{equipment_id}' not found. Use search_equipment to find valid IDs."}

    rates = eq["rates"]

    # Calculate base hire cost using tiered rates
    if duration_days >= 28:
        months = duration_days // 28
        remaining = duration_days % 28
        base = months * rates["monthly"]
        if remaining >= 7:
            weeks = remaining // 7
            days = remaining % 7
            base += weeks * rates["weekly"] + days * rates["daily"]
        else:
            base += remaining * rates["daily"]
    elif duration_days >= 7:
        weeks = duration_days // 7
        days = duration_days % 7
        base = weeks * rates["weekly"] + days * rates["daily"]
    else:
        base = duration_days * rates["daily"]

    breakdown = {"base_hire": round(base, 2)}

    # Insurance: typically 10-15% of hire cost
    if include_insurance:
        insurance = round(base * 0.12, 2)
        breakdown["damage_waiver_insurance"] = insurance
    else:
        insurance = 0
        breakdown["damage_waiver_note"] = "Not included - hirer liable for all damage"

    # Fuel estimate
    fuel = 0
    if include_fuel and eq["fuel_type"] == "diesel":
        # Rough fuel consumption per day based on weight class
        litres_per_day = eq["weight_tonnes"] * 4  # approx 4L per tonne per day
        fuel_price_per_litre = 1.45  # GBP
        fuel = round(litres_per_day * fuel_price_per_litre * duration_days, 2)
        breakdown["estimated_fuel"] = fuel
        breakdown["fuel_note"] = f"Based on ~{litres_per_day:.0f}L/day at {fuel_price_per_litre}/L"

    # Operator
    operator_cost = 0
    if operator_required:
        operator_daily = 280  # CPCS operator day rate
        operator_cost = operator_daily * duration_days
        breakdown["operator_cost"] = operator_cost
        breakdown["operator_note"] = f"CPCS-carded operator at {operator_daily}/day"

    total = base + insurance + fuel + operator_cost

    return {
        "equipment": eq["name"],
        "equipment_id": equipment_id,
        "duration_days": duration_days,
        "pricing": {
            "breakdown": breakdown,
            "subtotal": round(total, 2),
            "vat_20pct": round(total * 0.20, 2),
            "total_inc_vat": round(total * 1.20, 2),
            "currency": "GBP",
        },
        "rate_card": {
            "daily": rates["daily"],
            "weekly": rates["weekly"],
            "monthly": rates["monthly"],
        },
        "notes": [
            "Prices subject to availability",
            "Delivery and collection charged separately",
            f"{'Operator licence required' if eq['requires_licence'] else 'No licence required'}",
        ],
        "powered_by": "planthire.ai",
    }


@mcp.tool()
def check_availability(
    equipment_id: str,
    start_date: str,
    end_date: str,
    depot: str = "london", api_key: str = "") -> dict:
    """Check equipment availability for a date range.

    Args:
        equipment_id: Equipment ID from catalog.
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).
        depot: Depot location (london, birmingham, manchester, bristol, glasgow, leeds, cardiff, edinburgh).

    Returns:
        Availability status and alternative suggestions if unavailable.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _check_rate_limit():
        return {"error": "Rate limit exceeded."}

    eq = _EQUIPMENT_CATALOG.get(equipment_id)
    if not eq:
        return {"error": f"Equipment '{equipment_id}' not found."}

    depot_info = _DEPOTS.get(depot.lower())
    if not depot_info:
        return {"error": f"Depot '{depot}' not found. Options: {', '.join(_DEPOTS.keys())}"}

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    if end <= start:
        return {"error": "End date must be after start date."}

    # Check against booked periods
    booked = _availability.get(f"{equipment_id}_{depot}", [])
    conflicts = []
    for booking in booked:
        b_start = datetime.strptime(booking["start"], "%Y-%m-%d")
        b_end = datetime.strptime(booking["end"], "%Y-%m-%d")
        if start < b_end and end > b_start:
            conflicts.append(booking)

    available = len(conflicts) == 0
    duration = (end - start).days

    result = {
        "equipment": eq["name"],
        "equipment_id": equipment_id,
        "depot": depot_info["name"],
        "requested_period": {"start": start_date, "end": end_date, "days": duration},
        "available": available,
    }

    if not available:
        result["conflicts"] = [{"booked_from": c["start"], "booked_until": c["end"]} for c in conflicts]
        # Suggest alternatives: same category equipment
        alternatives = [
            {"equipment_id": eid, "name": e["name"], "daily_rate": e["rates"]["daily"]}
            for eid, e in _EQUIPMENT_CATALOG.items()
            if e["category"] == eq["category"] and eid != equipment_id
        ]
        result["alternatives"] = alternatives[:3]

    result["powered_by"] = "planthire.ai"
    return result


@mcp.tool()
def create_booking(
    equipment_id: str,
    start_date: str,
    end_date: str,
    depot: str = "london",
    customer_name: str = "",
    customer_email: str = "",
    customer_phone: str = "",
    include_insurance: bool = True,
    operator_required: bool = False,
    delivery_address: Optional[str] = None, api_key: str = "") -> dict:
    """Create an equipment booking.

    Args:
        equipment_id: Equipment ID from catalog.
        start_date: Hire start date (YYYY-MM-DD).
        end_date: Hire end date (YYYY-MM-DD).
        depot: Collection depot.
        customer_name: Booking contact name.
        customer_email: Contact email.
        customer_phone: Contact phone number.
        include_insurance: Add damage waiver insurance.
        operator_required: Book with CPCS operator.
        delivery_address: If provided, equipment will be delivered (extra cost).

    Returns:
        Booking confirmation with reference number.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _check_rate_limit():
        return {"error": "Rate limit exceeded."}

    # Verify availability first
    avail = check_availability(equipment_id, start_date, end_date, depot)
    if not avail.get("available"):
        return {"error": "Equipment not available for requested dates.", "availability": avail}

    eq = _EQUIPMENT_CATALOG.get(equipment_id)
    duration = avail["requested_period"]["days"]

    # Get quote
    quote = get_rental_quote(equipment_id, duration, include_insurance, operator_required=operator_required)

    booking_ref = f"PH-{uuid.uuid4().hex[:8].upper()}"

    booking = {
        "booking_reference": booking_ref,
        "status": "confirmed",
        "equipment": eq["name"],
        "equipment_id": equipment_id,
        "depot": depot,
        "period": {"start": start_date, "end": end_date, "days": duration},
        "customer": {
            "name": customer_name,
            "email": customer_email,
            "phone": customer_phone,
        },
        "pricing": quote["pricing"],
        "includes_insurance": include_insurance,
        "operator_included": operator_required,
        "delivery_address": delivery_address,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "terms": [
            "Hirer responsible for security of equipment on site",
            "Equipment must be returned clean and in working order",
            "Minimum hire period: 1 day",
            "Cancellation: free up to 48h before start, 50% charge within 48h",
        ],
    }

    # Record booking and block availability
    _bookings[booking_ref] = booking
    key = f"{equipment_id}_{depot}"
    if key not in _availability:
        _availability[key] = []
    _availability[key].append({"start": start_date, "end": end_date, "ref": booking_ref})

    return {**booking, "powered_by": "planthire.ai"}


@mcp.tool()
def get_safety_checklist(equipment_type: str, api_key: str = "") -> dict:
    """Get pre-use safety inspection checklist for equipment type.

    Based on HSE, CPCS, and IPAF guidelines. Categories: excavators,
    dumpers, telehandlers, compaction, access, power, loaders.

    Args:
        equipment_type: Equipment category (e.g. 'excavators', 'telehandlers').

    Returns:
        Detailed checklist with regulatory references.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _check_rate_limit():
        return {"error": "Rate limit exceeded."}

    checklist = _SAFETY_CHECKLISTS.get(equipment_type.lower())
    if not checklist:
        return {
            "error": f"No checklist for '{equipment_type}'.",
            "available_types": list(_SAFETY_CHECKLISTS.keys()),
        }

    critical_count = sum(1 for c in checklist["checks"] if c["critical"])

    return {
        **checklist,
        "total_checks": len(checklist["checks"]),
        "critical_checks": critical_count,
        "instructions": [
            "Complete ALL checks before starting work each day/shift",
            "Do NOT operate if any CRITICAL item fails - report to supervisor",
            "Record results on plant inspection sheet and retain for 3 months",
            "Report any defects immediately, even if non-critical",
        ],
        "emergency_contacts": {
            "hse_incident": "0345 300 9923",
            "site_emergency": "Contact site manager",
        },
        "powered_by": "planthire.ai",
    }


@mcp.tool()
def calculate_transport(
    equipment_id: str,
    distance_miles: float,
    depot: str = "london",
    return_trip: bool = True, api_key: str = "") -> dict:
    """Estimate transport costs for equipment delivery/collection.

    Pricing based on equipment size/weight class and distance.

    Args:
        equipment_id: Equipment ID from catalog.
        distance_miles: One-way distance in miles from depot to site.
        depot: Collection depot.
        return_trip: Include return collection cost (default True).

    Returns:
        Transport cost estimate with vehicle type.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _check_rate_limit():
        return {"error": "Rate limit exceeded."}

    eq = _EQUIPMENT_CATALOG.get(equipment_id)
    if not eq:
        return {"error": f"Equipment '{equipment_id}' not found."}

    transport_class = eq["transport_class"]
    costs = _TRANSPORT_COSTS[transport_class]

    if distance_miles > costs["max_distance_miles"]:
        return {
            "error": f"Distance exceeds maximum for {transport_class} ({costs['max_distance_miles']} miles). "
            "Contact us for special haulage arrangements.",
        }

    one_way = round(costs["base"] + (distance_miles * costs["per_mile"]), 2)
    total = one_way * 2 if return_trip else one_way

    transport_vehicles = {
        "van": "Transit-size van",
        "trailer": "Plant trailer (towed)",
        "flatbed": "Flatbed lorry (7.5t)",
        "low_loader": "Low-loader (18t)",
        "heavy_haulage": "Heavy haulage (40t+ with escort)",
    }

    return {
        "equipment": eq["name"],
        "weight_tonnes": eq["weight_tonnes"],
        "transport_class": transport_class,
        "vehicle": transport_vehicles[transport_class],
        "distance_miles": distance_miles,
        "pricing": {
            "one_way": one_way,
            "return_collection": one_way if return_trip else 0,
            "subtotal": round(total, 2),
            "vat_20pct": round(total * 0.2, 2),
            "total_inc_vat": round(total * 1.2, 2),
            "currency": "GBP",
        },
        "notes": [
            "Delivery times subject to driver availability",
            "Site must have suitable access for delivery vehicle",
            f"{'Escort vehicle required for heavy haulage' if transport_class == 'heavy_haulage' else ''}",
            "Weekend/bank holiday delivery available at +50% surcharge",
        ],
        "powered_by": "planthire.ai",
    }


if __name__ == "__main__":
    mcp.run()
