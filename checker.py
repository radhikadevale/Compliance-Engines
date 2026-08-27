import json
import re
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
# Thresholds
# ============================================================

IMAGE_QUALITY_THRESHOLD = 0.60

OCR_CONFIDENCE_THRESHOLD = 0.60


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
# Get field information
# ============================================================

def get_field_info(product, field):

    value = product.get(field)

    # New OCR format
    if isinstance(value, dict):

        return {
            "value": value.get("value"),
            "confidence": value.get("confidence"),
            "detected": value.get("detected"),
            "field_visibility": value.get(
                "field_visibility",
                "uncertain"
            )
        }

    # Old/simple format
    if value is not None:

        return {
            "value": value,
            "confidence": 1.0,
            "detected": True,
            "field_visibility": "clear"
        }

    return {
        "value": None,
        "confidence": None,
        "detected": False,
        "field_visibility": "uncertain"
    }


# ============================================================
# Check image quality
# ============================================================

def image_is_reliable(product):

    quality = product.get(
        "image_quality"
    )

    if quality is None:

        return False

    try:

        return float(quality) >= IMAGE_QUALITY_THRESHOLD

    except (ValueError, TypeError):

        return False


# ============================================================
# Check evidence quality
# ============================================================

def evidence_is_reliable(
    product,
    field_info
):

    # Image quality
    if not image_is_reliable(product):

        return False


    # Field visibility
    visibility = field_info.get(
        "field_visibility"
    )

    if visibility == "uncertain":

        return False


    # OCR confidence
    confidence = field_info.get(
        "confidence"
    )

    if confidence is not None:

        try:

            if float(confidence) < OCR_CONFIDENCE_THRESHOLD:

                return False

        except (ValueError, TypeError):

            return False

    return True


# ============================================================
# Validate MRP
# ============================================================

def validate_mrp(value):

    if value is None:

        return False

    text = str(value).strip()

    if not text:

        return False

    # Obvious OCR uncertainty

    if "?" in text:
        return False

    if "..." in text:
        return False

    # Basic MRP format

    pattern = r"(₹|Rs\.?|INR)?\s*\d+(?:\.\d{1,2})?"

    return bool(
        re.fullmatch(
            pattern,
            text,
            flags=re.IGNORECASE
        )
    )


# ============================================================
# Validate generic field
# ============================================================

def validate_field(
    field,
    value
):

    if value is None:

        return False

    text = str(value).strip()

    if not text:

        return False

    if field == "mrp":

        return validate_mrp(value)

    return True


# ============================================================
# Check whether field is required
# ============================================================

def is_required(rule):

    return rule.get(
        "required",
        True
    )


# ============================================================
# Check one applicable rule
# ============================================================

def check_rule(
    product,
    rule
):

    field = rule.get(
        "field"
    )

    field_info = get_field_info(
        product,
        field
    )

    value = field_info["value"]

    confidence = field_info["confidence"]

    detected = field_info["detected"]

    visibility = field_info[
        "field_visibility"
    ]


    # ========================================================
    # STEP 1
    # Evidence quality
    # ========================================================

    if not evidence_is_reliable(
        product,
        field_info
    ):

        return {
            "rule_id": rule["rule_id"],
            "rule_number": rule["rule_number"],
            "field": field,
            "status": "NEEDS_VERIFICATION",
            "value": value,
            "confidence": confidence,
            "reason": (
                "Image/OCR evidence is insufficient "
                "to reliably determine compliance."
            )
        }


    # ========================================================
    # STEP 2
    # Field detected
    # ========================================================

    if detected is True:

        if validate_field(
            field,
            value
        ):

            return {
                "rule_id": rule["rule_id"],
                "rule_number": rule["rule_number"],
                "field": field,
                "status": "PASS",
                "value": value,
                "confidence": confidence,
                "reason": (
                    "Required information was clearly "
                    "detected and passed validation."
                )
            }

        return {
            "rule_id": rule["rule_id"],
            "rule_number": rule["rule_number"],
            "field": field,
            "status": "NEEDS_VERIFICATION",
            "value": value,
            "confidence": confidence,
            "reason": (
                "Information was detected, but the "
                "extracted value could not be reliably validated."
            )
        }


    # ========================================================
    # STEP 3
    # Field definitely absent
    # ========================================================

    if detected is False:

        if visibility == "clear":

            if is_required(rule):

                return {
                    "rule_id": rule["rule_id"],
                    "rule_number": rule["rule_number"],
                    "field": field,
                    "status": "FAIL",
                    "value": None,
                    "confidence": confidence,
                    "reason": (
                        "The required information was "
                        "clearly absent from the visible label."
                    )
                }

            return {
                "rule_id": rule["rule_id"],
                "rule_number": rule["rule_number"],
                "field": field,
                "status": "PASS",
                "value": None,
                "confidence": confidence,
                "reason": (
                    "The field is not required "
                    "for this applicable rule."
                )
            }


    # ========================================================
    # STEP 4
    # Cannot determine
    # ========================================================

    return {
        "rule_id": rule["rule_id"],
        "rule_number": rule["rule_number"],
        "field": field,
        "status": "NEEDS_VERIFICATION",
        "value": value,
        "confidence": confidence,
        "reason": (
            "The available evidence is insufficient "
            "to determine compliance."
        )
    }


# ============================================================
# Check applicable rules
# ============================================================

def check_product(
    product,
    applicability_result
):

    rules_data = load_rules()

    results = []

    applicable_rule_ids = (
        applicability_result.get(
            "applicable_rule_ids",
            []
        )
    )

    for rule in rules_data.get(
        "rules",
        []
    ):

        if rule["rule_id"] in applicable_rule_ids:

            result = check_rule(
                product,
                rule
            )

            results.append(
                result
            )

    return results


# ============================================================
# Overall result
# ============================================================

def get_overall_status(results):

    # FAIL has highest priority

    for result in results:

        if result["status"] == "FAIL":

            return "FAIL"


    # Verification next

    for result in results:

        if result["status"] == "NEEDS_VERIFICATION":

            return "NEEDS_VERIFICATION"


    # Everything passed

    if results:

        return "PASS"

    return "NEEDS_VERIFICATION"