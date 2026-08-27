import json
from pathlib import Path


# ============================================================
# Location of rules.json
# ============================================================

RULES_FILE = (
    Path(__file__).parent
    / "rules"
    / "rules.json"
)


# ============================================================
# Load rules
# ============================================================

def load_rules():

    with open(
        RULES_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# Get product field
# ============================================================

def get_product_value(product, field):

    value = product.get(field)

    # Handle OCR object format
    #
    # Example:
    #
    # "mrp": {
    #     "value": "₹50",
    #     "confidence": 0.96
    # }

    if isinstance(value, dict):

        return value.get("value")

    return value


# ============================================================
# Evaluate one applicability condition
# ============================================================

def evaluate_condition(product, condition):

    field = condition.get("field")

    operator = condition.get("operator")

    expected_value = condition.get("value")

    actual_value = get_product_value(
        product,
        field
    )

    # --------------------------------------------------------
    # equals
    # --------------------------------------------------------

    if operator == "equals":

        return actual_value == expected_value


    # --------------------------------------------------------
    # greater_than
    # --------------------------------------------------------

    if operator == "greater_than":

        try:

            return float(actual_value) > float(
                expected_value
            )

        except (TypeError, ValueError):

            return False


    # --------------------------------------------------------
    # less_than
    # --------------------------------------------------------

    if operator == "less_than":

        try:

            return float(actual_value) < float(
                expected_value
            )

        except (TypeError, ValueError):

            return False


    # --------------------------------------------------------
    # Unknown operator
    # --------------------------------------------------------

    return False


# ============================================================
# Check primary applicability
# ============================================================

def check_primary_applicability(
    product,
    applicability_data
):

    conditions = applicability_data.get(
        "scope_conditions",
        []
    )

    # All primary conditions must be satisfied.

    for condition in conditions:

        if not evaluate_condition(
            product,
            condition
        ):

            return False

    return True


# ============================================================
# Check exclusions
# ============================================================

def check_exclusions(
    product,
    applicability_data
):

    exclusions = applicability_data.get(
        "exclusions",
        []
    )

    triggered_exclusions = []

    for exclusion in exclusions:

        if evaluate_condition(
            product,
            exclusion
        ):

            triggered_exclusions.append(
                exclusion["exclusion_id"]
            )

    return triggered_exclusions


# ============================================================
# Determine overall applicability
# ============================================================

def determine_applicability(product):

    rules_data = load_rules()

    applicability_data = rules_data.get(
        "applicability",
        {}
    )

    # --------------------------------------------------------
    # Step 1: Check primary scope
    # --------------------------------------------------------

    primary_scope = check_primary_applicability(
        product,
        applicability_data
    )

    if not primary_scope:

        return {
            "applicable": False,
            "status": "NOT_APPLICABLE",
            "reason": (
                "The product does not satisfy "
                "the primary applicability conditions."
            ),
            "applicable_rule_ids": []
        }


    # --------------------------------------------------------
    # Step 2: Check exclusions
    # --------------------------------------------------------

    triggered_exclusions = check_exclusions(
        product,
        applicability_data
    )

    if triggered_exclusions:

        return {
            "applicable": False,
            "status": "NOT_APPLICABLE",
            "reason": (
                "An applicability exclusion was established."
            ),
            "triggered_exclusions": triggered_exclusions,
            "applicable_rule_ids": []
        }


    # --------------------------------------------------------
    # Step 3: Select applicable rules
    # --------------------------------------------------------

    applicable_rules = []

    for rule in rules_data.get("rules", []):

        rule_applicability = rule.get(
            "applicability",
            {}
        )

        rule_type = rule_applicability.get(
            "type"
        )

        # Chapter II rules
        if rule_type == "chapter_ii":

            applicable_rules.append(
                rule["rule_id"]
            )

        # Conditional rules are not automatically included.
        #
        # They need their trigger condition to be
        # evaluated separately.
        elif rule_type == "conditional":

            trigger = rule_applicability.get(
                "trigger"
            )

            # Prototype handling:
            # conditional rules are sent for
            # verification rather than automatically
            # assumed applicable.

            if trigger:

                applicable_rules.append(
                    rule["rule_id"]
                )

    return {
        "applicable": True,
        "status": "APPLICABLE",
        "reason": (
            "The product satisfies the primary "
            "applicability conditions and no "
            "defined exclusion was established."
        ),
        "triggered_exclusions": [],
        "applicable_rule_ids": applicable_rules
    }