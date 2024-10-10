#/bin/bash
set -ex

./integration_test_helper.sh start
./integration_test_helper.sh check
./integration_test_helper.sh stop
