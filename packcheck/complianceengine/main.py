# ============================================================
# PackCheck - Main
# ============================================================

from product_data import product

from applicability import (
    determine_applicability
)

from checker import (
    check_product,
    get_overall_status
)


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print("           PackCheck Compliance Engine")
    print("=" * 60)


    # ========================================================
    # STEP 1 — APPLICABILITY
    # ========================================================

    print()
    print("STEP 1 — APPLICABILITY")
    print("-" * 60)


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
    # If product is not applicable
    # ========================================================

    if applicability_result[
        "status"
    ] == "NOT_APPLICABLE":

        print()
        print(
            "Product is outside the applicable "
            "scope."
        )

        return


    # ========================================================
    # If applicability is uncertain
    # ========================================================

    if applicability_result[
        "status"
    ] == "NEEDS_VERIFICATION":

        print()
        print(
            "Applicability could not be "
            "reliably determined."
        )

        return


    # ========================================================
    # STEP 2 — APPLICABLE RULES
    # ========================================================

    print()
    print("STEP 2 — APPLICABLE RULES")
    print("-" * 60)


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
    # Rules needing applicability verification
    # ========================================================

    verification_rules = (
        applicability_result.get(
            "verification_rule_ids",
            []
        )
    )


    if verification_rules:

        print()

        print(
            "Rules needing applicability "
            "verification:"
        )

        for rule_id in verification_rules:

            print(
                "⚠",
                rule_id
            )


    # ========================================================
    # STEP 3 — CHECKER
    # ========================================================

    print()
    print("STEP 3 — COMPLIANCE CHECKER")
    print("-" * 60)


    results = check_product(
        product,
        applicability_result
    )


    # ========================================================
    # STEP 4 — OVERALL RESULT
    # ========================================================

    overall_status = (
        get_overall_status(
            results
        )
    )


    print()
    print("=" * 60)
    print(
        "OVERALL RESULT:",
        overall_status
    )
    print("=" * 60)


    # ========================================================
    # Individual results
    # ========================================================

    print()
    print("INDIVIDUAL RULE RESULTS")
    print("-" * 60)


    for result in results:

        print()

        print(
            "Rule:",
            result["rule_number"]
        )

        print(
            "Rule ID:",
            result["rule_id"]
        )

        print(
            "Field:",
            result["field"]
        )

        print(
            "Status:",
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

        print("-" * 60)


# ============================================================
# Start application
# ============================================================

if __name__ == "__main__":

    main()