#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <gamma_value_between_0_and_1>"
  exit 2
fi

value="$1"
if [[ ! "$value" =~ ^(0(\.[0-9]+)?|1(\.0+)?)$ ]]; then
  echo "invalid gamma value: $value"
  exit 1
fi

echo "gamma coefficient $value is valid"
