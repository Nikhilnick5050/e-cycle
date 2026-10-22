"""
E-Cycle — rule-based segregation and recommendation engine.

This is a deterministic, rule-based classifier (NOT machine learning).
It maps an item type + condition to a category and a plain-language
recommendation. Recommendations are preliminary; final handling must
always follow local rules and authorised recycler guidance.
"""


def classify(item_type, condition):
    """Return (category, recommendation) for a submitted item."""
    item_type = (item_type or "").strip()
    condition = (condition or "").strip()

    # Rule 4 — Batteries always need separate, special handling.
    if item_type.lower() == "battery":
        return (
            "Special Handling",
            "Batteries must always be handled separately. Never open, crush, "
            "burn, or throw them in ordinary household waste. Store them in a "
            "cool, dry place and hand them over to an authorised e-waste "
            "collection facility.",
        )

    # Rule 5 — Chargers and cables go for material recovery.
    if item_type.lower() in ("charger / cable", "charger", "cable"):
        return (
            "Recyclable",
            "Chargers and cables should be collected for responsible recovery "
            "of electronic materials (copper, plastic, etc.). Take them to an "
            "authorised collection point.",
        )

    # Rule 6 — TVs and monitors need careful handling.
    if item_type.lower() in ("television / monitor", "television", "monitor"):
        return (
            "Recyclable",
            "Televisions and monitors need careful handling to prevent "
            "breakage and unsafe disposal. Hand them over to an authorised "
            "collection facility for safe recycling.",
        )

    # Rule 1 — Working devices: reuse / donation / refurbishment.
    if condition.lower() == "working":
        return (
            "Reusable",
            "This item is working. Consider reuse, donation, or refurbishment "
            "to extend its life. If you no longer need it, drop it at an "
            "authorised collection point for responsible reuse.",
        )

    # Rule 2 — Repairable devices: repair first, else recycle.
    if condition.lower() == "repairable":
        return (
            "Repairable",
            "This item can be repaired. Try professional repair first to "
            "extend its life. If repair is impractical, send it to an "
            "authorised recycler.",
        )

    # Rule 3 — Damaged devices: safe handling + authorised facility.
    if condition.lower() in ("damaged / not working", "damaged"):
        return (
            "Recyclable",
            "This item is damaged. Handle it safely and deliver it to an "
            "authorised e-waste collection facility. Do not burn or dismantle "
            "it at home.",
        )

    # Fallback — never leave an item unclassified.
    return (
        "Recyclable",
        "Handle this item safely and deliver it to an authorised e-waste "
        "collection facility.",
    )