# Evaluation pipeline


## Step 1. Run the simple evaluation pipeline

The first test run is with an agent with simple instructions and with a basic evaluation scheme.
Each test will be either pass/fail.

```bash
python evaluate.py
```

Analyze the results. Observe the score.

## Step 2. Replace the instructions in agent.py 

Replace the `simple_instructions` in agent.py with `improved_instructions`.
Run again:

```bash
python evaluate.py
```

Observe the results, score.

## Step 3. Run the DeepEval evaluation pipeline

DeepEval will evaluate multiple metrics (relevance, correctness).

```bash
python deepeval_evaluate.py
```

Analyze the results.

