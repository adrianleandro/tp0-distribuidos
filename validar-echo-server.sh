#!/bin/bash

SERVER_NAME="server"
SERVER_PORT="12345"

NETWORK_NAME="tp0_testing_net"

MESSAGE_TO_SEND="is this thing on?"
NETWORK_TEST_OUTPUT=$(echo "$MESSAGE_TO_SEND" | docker run --rm -i --network "$NETWORK_NAME" busybox:latest nc "$SERVER_NAME" "$SERVER_PORT")
RESULT_MESSAGE="action: test_echo_server | result:"

if [ "$MESSAGE_TO_SEND" = "$NETWORK_TEST_OUTPUT" ]; then
  RESULT="success"
else
  RESULT="fail"
fi

echo "$RESULT_MESSAGE" "$RESULT"