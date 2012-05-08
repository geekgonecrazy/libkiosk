#!/usr/bin/env bash

exec ck-launch-session &
exec matchbox-window-manager &
exec start-kiosk 
