"""
Chatbot Guardrails Tests
=========================

Unit tests for the safety guardrail post-processor applied to chatbot
explanations before they are returned to clients.
"""

import pytest

from chatbot.api import (
    SAFETY_DENYLIST,
    SAFETY_DENYLIST_RE,
    post_process_guardrails,
    _MANDATORY_DISCLAIMER,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_risk_info():
    """Risk info dict mirroring the shape produced by chatbot implementations."""
    return {
        "state": "Maharashtra",
        "district": "Mumbai",
        "safety_score": 72.5,
        "risk_category": "Moderate Risk",
    }


# ---------------------------------------------------------------------------
# Denylist configuration tests
# ---------------------------------------------------------------------------

class TestSafetyDenylist:
    """Validate the configured denylist patterns."""

    def test_denylist_includes_all_required_phrases(self):
        """All required absolute-safety phrases must be present."""
        required_substrings = [
            "completely",
            "safe",
            "100",
            "risk",
            "perfectly",
            "entirely",
        ]
        joined = " ".join(SAFETY_DENYLIST).lower()
        for needle in required_substrings:
            assert needle in joined, f"Missing denylist coverage for: {needle}"

    def test_denylist_matches_case_insensitively(self):
        """Each denylist phrase must match in any case."""
        cases = [
            "completely safe",
            "COMPLETELY SAFE",
            "Completely Safe",
            "100% safe",
            "100% SAFE",
            "No Risk",
            "NO RISK",
            "perfectly SAFE",
            "Entirely Safe",
        ]
        for text in cases:
            assert SAFETY_DENYLIST_RE.search(text) is not None, (
                f"Denylist failed to match case-insensitively: {text!r}"
            )


# ---------------------------------------------------------------------------
# post_process_guardrails behaviour tests
# ---------------------------------------------------------------------------

class TestPostProcessGuardrails:
    """Validate sanitization + disclaimer behaviour."""

    def test_replaces_completely_safe_phrase(self, sample_risk_info):
        """An explanation containing 'completely safe' must be sanitized."""
        original = (
            "Based on the data, this area is completely safe to walk around at night."
        )

        result = post_process_guardrails(original, sample_risk_info)

        assert "completely safe" not in result.lower()
        assert (
            "has a reported safety score of 72.5/100" in result
        ), "Replacement should use the safety score from risk_info"
        assert "Moderate Risk" in result, (
            "Replacement should reference the risk category from risk_info"
        )

    def test_replaces_all_denylist_phrases(self, sample_risk_info):
        """Every denylist phrase must be replaced."""
        denylisted_text = (
            "It is 100% safe and completely safe, perfectly safe and "
            "entirely safe with no risk at all."
        )

        result = post_process_guardrails(denylisted_text, sample_risk_info)

        # None of the banned phrases survive.
        lowered = result.lower()
        for phrase in (
            "completely safe",
            "100% safe",
            "perfectly safe",
            "entirely safe",
            "no risk",
        ):
            assert phrase not in lowered, f"Banned phrase survived: {phrase}"

    def test_disclaimer_is_always_appended(self, sample_risk_info):
        """Every post-processed output must carry the mandatory disclaimer."""
        samples = [
            "This area has moderate crime rates.",
            "Travel with caution after dark.",
            "",
        ]
        for text in samples:
            result = post_process_guardrails(text, sample_risk_info)
            assert _MANDATORY_DISCLAIMER in result, (
                f"Disclaimer missing for input: {text!r}"
            )

    def test_non_matching_explanation_still_gets_disclaimer(self, sample_risk_info):
        """Explanations without denylist phrases must still receive the disclaimer."""
        original = (
            "The district shows a moderate safety profile. Exercise normal "
            "precautions and remain aware of your surroundings."
        )

        result = post_process_guardrails(original, sample_risk_info)

        assert result.startswith(original), (
            "Non-matching text should be preserved verbatim at the start"
        )
        assert _MANDATORY_DISCLAIMER in result

    def test_preserves_score_and_category_in_replacement(self):
        """Replacement string must interpolate the provided risk_info fields."""
        risk_info = {"safety_score": 41, "risk_category": "High Risk"}
        text = "This area is completely safe."

        result = post_process_guardrails(text, risk_info)

        assert "41/100" in result
        assert "High Risk" in result
        assert _MANDATORY_DISCLAIMER in result

    def test_handles_missing_risk_fields(self):
        """Guardrails should not crash when risk_info lacks optional fields."""
        # The function should fall back gracefully on missing keys.
        result = post_process_guardrails(
            "This area is completely safe.",
            {},
        )
        assert _MANDATORY_DISCLAIMER in result
        # Replacement should still be applied (with fallback values).
        assert "completely safe" not in result.lower()
