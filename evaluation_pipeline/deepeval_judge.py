import logging
import os

from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from judge import run_rule_eval

logger = logging.getLogger(__name__)

EVAL_MODEL_NAME = "gemini-2.5-flash"

eval_model = GeminiModel(
    model=EVAL_MODEL_NAME,
    project=os.getenv("GOOGLE_CLOUD_PROJECT", "gemini-first-439812"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    temperature=0,
)


def run_deepeval_eval(test_case: dict, answer: str) -> dict:
    llm_test_case = LLMTestCase(
        input=test_case["prompt"],
        actual_output=answer,
        expected_output=test_case["expected_output"],
    )

    answer_relevancy = AnswerRelevancyMetric(
        threshold=0.7,
        model=eval_model,
        include_reason=True,
    )

    correctness = GEval(
        name="Sales Answer Correctness",
        criteria=(
            "Evaluate whether the actual output correctly answers the user's question "
            "using only the expected sales facts. Penalize wrong numbers, invented "
            "countries, missing requested values, and unnecessary extra facts."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.8,
        model=eval_model,
    )

    answer_relevancy.measure(llm_test_case)
    correctness.measure(llm_test_case)

    rule_eval = run_rule_eval(test_case, answer)

    passed = (
        rule_eval["passed"]
        and answer_relevancy.is_successful()
        and correctness.is_successful()
    )

    return {
        "passed": passed,
        "rule_eval": rule_eval,
        "deepeval": {
            "model": EVAL_MODEL_NAME,
            "provider": "vertex_ai",
            "answer_relevancy": {
                "score": answer_relevancy.score,
                "passed": answer_relevancy.is_successful(),
                "reason": answer_relevancy.reason,
            },
            "correctness": {
                "score": correctness.score,
                "passed": correctness.is_successful(),
                "reason": correctness.reason,
            },
        },
    }