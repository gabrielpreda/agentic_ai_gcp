#!/bin/bash

export PYTHONWARNINGS="ignore"
export LOG_LEVEL="debug"

concurrently \
  --names "discovery,routing,agent,client" \
  --prefix "[{name}]" \
  --kill-others-on-fail \
  "uvicorn discovery:application --host 0.0.0.0 --port 10020 --log-level debug --access-log" \
  "uvicorn routing:application --host 0.0.0.0 --port 10021 --log-level debug --access-log" \
  "uvicorn agent:application --host 0.0.0.0 --port 10022 --log-level debug --access-log" \
  "uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug --access-log"