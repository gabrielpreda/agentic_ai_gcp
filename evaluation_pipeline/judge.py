import logging
import re

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    text = text.lower()

    # Remove commas inside numbers, e.g. 980,000 -> 980000
    text = re.sub(r"(?<=\d),(?=\d)", "", text)

    return text


def run_rule_eval(test_case, answer):
    logger.info("Running rule evaluation for test_case_id=%s", test_case.get("id"))

    answer_normalized = normalize_text(answer)

    missing_keywords = [
        keyword
        for keyword in test_case["expected_keywords"]
        if normalize_text(keyword) not in answer_normalized
    ]

    forbidden_matches = [
        keyword
        for keyword in test_case["must_not_include"]
        if normalize_text(keyword) in answer_normalized
    ]

    passed = (
        len(missing_keywords) == 0
        and len(forbidden_matches) == 0
    )

    logger.info(
        "Evaluation completed for test_case_id=%s passed=%s missing_keywords=%s forbidden_matches=%s",
        test_case.get("id"),
        passed,
        missing_keywords,
        forbidden_matches,
    )

    return {
        "passed": passed,
        "missing_keywords": missing_keywords,
        "forbidden_matches": forbidden_matches,
    }