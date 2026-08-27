import json
from pathlib import Path

from product_data import product


# ==================================================
# 1. Location of rules.json
# ==================================================

RULES_FILE = (
    Path(__file__).parent
    / "PackCheck"
    / "compliance_engine"
    / "rules"
    / "rules.json"
)


# ==================================================
# 2. Load rules.json
# ==================================================

def load_rules():

    with open(RULES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# ==================================================
# 3. Check whether product field contains information
# ==================================================

def check_field(product, field):

    value = product.get(field)

    if value is not None and str(value).strip() != "":
        return "PASS"

    return "NEEDS_VERIFICATION"


# ==================================================
# 4. Check one rule from rules.json
# ==================================================

def check_rule(product, rule):

    field = rule.get("field")

    # Check whether the required field exists
    if field not in product:

        return {
            "rule_id": rule["rule_id"],
            "rule_number": rule["rule_number"],
            "field": field,
            "status": "NEEDS_VERIFICATION",
            "reason": (
                "Required information was not provided "
                "in product data."
            )
        }

    # Check whether information is present
    status = check_field(product, field)

    if status == "PASS":

        reason = (
            "Information was detected in the "
            "product data."
        )

    else:

        reason = (
            "Information was not detected. "
            "Missing OCR/data does not by itself "
            "prove legal non-compliance."
        )

    return {
        "rule_id": rule["rule_id"],
        "rule_number": rule["rule_number"],
        "field": field,
        "status": status,
        "reason": reason
    }


# ==================================================
# 5. Check prototype rules from rules.json
# ==================================================

def check_product(product):

    rules_data = load_rules()

    results = []

    # Get selected rules from rules.json
    prototype_rule_ids = rules_data.get(
        "prototype_priority_rules",
        []
    )

    # Read all rules from rules.json
    for rule in rules_data.get("rules", []):

        # Only check rules selected for prototype
        if rule["rule_id"] in prototype_rule_ids:

            result = check_rule(product, rule)

            results.append(result)

    return results


# ==================================================
# 6. Calculate overall compliance status
# ==================================================

def get_overall_status(results):

    # FAIL has highest priority
    for result in results:

        if result["status"] == "FAIL":
            return "FAIL"

    # NEEDS_VERIFICATION has second priority
    for result in results:

        if result["status"] == "NEEDS_VERIFICATION":
            return "NEEDS_VERIFICATION"

    # Everything passed
    return "PASS"


# ==================================================
# 7. Run Compliance Engine
# ==================================================

if __name__ == "__main__":

    try:

        # Load product data
        results = check_product(product)

        # Calculate overall result
        overall_status = get_overall_status(results)

        print()
        print("========================================")
        print("     PackCheck Compliance Engine")
        print("========================================")

        print()
        print("Product data:")
        print("----------------------------------------")
        print(product)

        print()
        print(f"Overall Status: {overall_status}")

        print()
        print("Rule Checks:")
        print("----------------------------------------")

        for result in results:

            print(
                f"{result['rule_number']} | "
                f"{result['field']} | "
                f"{result['status']}"
            )

            print(
                f"Reason: {result['reason']}"
            )

            print()

    except FileNotFoundError:

        print()
        print("ERROR:")
        print()
        print("rules.json was not found.")
        print("Expected location:")
        print(RULES_FILE)

    except json.JSONDecodeError:

        print()
        print("ERROR:")
        print()
        print("rules.json contains invalid JSON.")

    except Exception as e:

        print()
        print("ERROR:")
        print(e)