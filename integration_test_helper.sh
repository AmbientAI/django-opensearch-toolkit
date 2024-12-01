#/bin/bash


_usage() {
    echo "Usage: $0 <mode:start|check|stop>"
    exit 1
}


if [[ $# -ne 1 || ( "$1" != "start" && "$1" != "check" && "$1" != "stop" ) ]]; then
    _usage
    return 1
fi


set -x


MODE=$1
DOCKER_IMAGE=opensearchproject/opensearch:2.10.0
DOCKER_CONTAINER=dot_opensearch
HOST=localhost
PORT=9200


_download_docker_image() {
    docker pull $DOCKER_IMAGE
    return $?
}


_launch_docker_container() {
    docker run \
        -d \
        --rm \
        --name $DOCKER_CONTAINER \
        -p $PORT:$PORT \
        -e "discovery.type=single-node" \
        -e "plugins.security.disabled=true" \
        $DOCKER_IMAGE
    return $?
}


_stop_docker_container() {
    docker stop $DOCKER_CONTAINER
    return $?
}


_wait_for_opensearch_to_be_available() {
  # Parameters (optional: pass URL and max tries)
  url=${1:-"http://$HOST:9200"}
  max_tries=${2:-10}
  sleep_time=${3:-3}

  # Initial attempt
  try=1

  # Loop for up to max_tries
  while [ $try -le $max_tries ]; do
    echo "Attempt $try: Checking OpenSearch availability at $url..."

    # Call curl and check if the exit code is non-zero (curl returns 0 for success)
    curl --silent --head "$url"
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
      echo "SUCCESS: OpenSearch is available."
      break
    else
      echo "OpenSearch is unavailable (exit code: $exit_code). Trying again..."
    fi

    # Wait before the next try
    sleep $sleep_time

    # Increment try counter
    try=$((try + 1))
  done

  if [ $try -gt $max_tries ]; then
    echo "Maximum number of tries ($max_tries) reached."
    return 1
  fi

  return 0
}


_run_migrations() {
    PYTHONPATH=. python sample_project/manage.py opensearch_runmigrations sample_app --nodry
    return $?
}


_display_migrations() {
    PYTHONPATH=. python sample_project/manage.py opensearch_displaymigrations sample_app
    return $?
}


_run_api_server() {
    PYTHONPATH=. python sample_project/manage.py runserver 10000 &
}


_stop_api_server() {
    kill -9 $(lsof -t -i:10000)
}


_list_merchants() {
    curl -s localhost:10000/api/v1/merchants/ | jq
    return $?
}


_create_merchant() {
    curl -s -X POST localhost:10000/api/v1/merchants/ \
        -d '{"name": "Sony", "description": "Electronics manufacturer", "website": "sony.com"}'| jq
    return $?
}


case "$MODE" in
    start)
        _download_docker_image
        _launch_docker_container
        _wait_for_opensearch_to_be_available
        ;;
    check)
        _run_migrations
        sleep 1
        _display_migrations
        _run_api_server
        sleep 1
        _list_merchants
        _create_merchant
        sleep 1
        _list_merchants
        ;;
    stop)
        _stop_api_server
        _stop_docker_container
        ;;
esac
