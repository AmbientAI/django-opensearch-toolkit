#/bin/bash
set -ex

./scripts/integration_test_helper.sh start
./scripts/integration_test_helper.sh check
./scripts/integration_test_helper.sh stop
