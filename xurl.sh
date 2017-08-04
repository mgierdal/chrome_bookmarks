#!/usr/bin/env sh

grep -o '<DT><A[[:blank:]]*HREF=[^ ]*://[^ ]*' $1 | grep -o '".*"' | tr -d '"'
