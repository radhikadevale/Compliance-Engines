from product_data import product

from applicability import (
    determine_applicability
)

from checker import (
    check_product,
    get_overall_status
)


# ============================================================
# Run PackCheck
# ============================================================

def main():

    print()
    print("========================================")
    print("       PackCheck Compliance Engine")
    print("========================================")


    # ========================================================
    # STEP 1 — Applicability
    # ========================================================

    print()
    print("STEP 1: APPLICABILITY")
    print("----------------------------------------")

    applicability_result = (
        determine_applicability(
            product
        )
    )

    print(
        "Status:",
        applicability_result["status"]
    )

    print(
        "Reason:",
        applicability_result["reason"]
    )


    # ========================================================
    # Stop if product is not applicable
    # ========================================================

    if not applicability_result[
        "applicable"
    ]:

        print()
        print(
            "No Chapter II rules will be checked."
        )

        return


    # ========================================================
    # STEP 2 — Applicable Rules
    # ========================================================

    print()
    print("STEP 2: APPLICABLE RULES")
    print("----------------------------------------")

    applicable_rules = (
        applicability_result[
            "applicable_rule_ids"
        ]
    )

    for rule_id in applicable_rules:

        print(
            "✓",
            rule_id
        )


    # ========================================================
    # STEP 3 — Checker
    # ========================================================

    print()
    print("STEP 3: COMPLIANCE CHECKER")
    print("----------------------------------------")

    results = check_product(
        product,
        applicability_result
    )


    # ========================================================
    # STEP 4 — Overall result
    # ========================================================

    overall_status = (
        get_overall_status(
            results
        )
    )


    print()
    print("========================================")
    print(
        "OVERALL RESULT:",
        overall_status
    )
    print("========================================")


    # ========================================================
    # Individual rule results
    # ========================================================

    print()

    for result in results:

        print(
            result["rule_number"],
            "|",
            result["field"],
            "|",
            result["status"]
        )

        print(
            "Value:",
            result["value"]
        )

        print(
            "Confidence:",
            result["confidence"]
        )

        print(
            "Reason:",
            result["reason"]
        )

        print("----------------------------------------")


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    main()