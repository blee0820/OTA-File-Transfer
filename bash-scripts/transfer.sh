#!/bin/bash
# In a working environment, thie file is dynamically created and then destroyed upon program termination.
# Retained for visibility.

transfer(){
	mount - / - oremount,rw
	cd /tmp-folder/bash-scripts/transfer-files

	chown root:root transfer-file.php
	chmod 755 transfer-file.php
	echo Copying transfer-file.php to /final-destination-for-php
	cp transfer-file.php /final-destination-for-php || { echo Failed to copy transfer-file.php to /final-destination-for-php; exit 1; }
	cmp -s /final-destination-for-php/transfer-file.php transfer-file.php || { echo Original transfer-file.php and copied transfer-file.php at /final-destination-for-php seem to be different. Aborting file transfer.; exit 1; }

	chown root:root transfer-file.service
	chmod 644 transfer-file.service
	echo Copying tranfer-file.service to /final-destination-for-service
	cp transfer-file.service final-destination-for-service || { echo Failed to copy transfer-file.service to /final-destination-for-service; exit 1; }
	cmp -s /final-destination-for-service/transfer-file.service transfer-file.service || { echo Original transfer-file.service and copied transfer-file.service at /final-destination-for-service seem to be different. Aborting file transfer.; exit 1; }

	# below systemctl enable command refers to transfer-file.service (services are enabled without the .service extension)
	systemctl enable transfer-file
	rm -r /tmp-folder
	mount - / -oremount,ro
}
transfer
