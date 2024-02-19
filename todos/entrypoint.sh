#!/bin/sh

while true; do
	aerich upgrade
	if [ "$?" -eq "0" ]; then
		break
	fi

	echo "Database upgrade failed, retrying in 5 seconds..."
	sleep 5
done

exec supervisord -n
