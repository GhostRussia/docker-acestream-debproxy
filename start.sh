#!/bin/bash

/opt/acestream/acestreamengine --client-console --cache-dir /tmp/state/.ACEStream --live-cache-type memory --live-cache-size 52428800 --state-dir /tmp/state/.ACEStream --core-sandbox-max-peers 15 --live-buffer 20 --vod-cache-type memory --vod-buffer 20 --vod-drop-max-age 120