import re

def normalize_text(text: str) -> str:
    text = text.lower()

    # remove commas inside numbers
    text = re.sub(r'(?<=\d),(?=\d)', '', text)

    return text



def run_rule_eval(
    test_case,
    answer,
):

    answer_normalized = normalize_text(answer)

    missing_keywords = [
        keyword
        for keyword in test_case["expected_keywords"]
        if normalize_text(keyword) not in answer_normalized
    ]

    forbidden_matches = [
        keyword
        for keyword in test_case["must_not_include"]
        if keyword.lower() in answer_normalized
    ]

    passed = (
        len(missing_keywords) == 0
        and len(forbidden_matches) == 0
    )

    return {
        "passed": passed,
        "missing_keywords": missing_keywords,
        "forbidden_matches": forbidden_matches,
    }