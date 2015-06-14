import sys
import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import splunk
import splunk.auth as auth
import splunk.entity as entity
import splunk.Intersplunk as intersplunk
import splunk.rest as rest
import splunk.search as search
import splunk.input as input
import splunk.util as util
import urllib
import json
import socket
import logging
import time
import datetime
import hashlib
import re

sys.stdout = open('/tmp/stdout2', 'a')
sys.stderr = open('/tmp/stderr2', 'a')


#
# Init
#
start = time.time()

if len(sys.argv) < 9:
    print "Wrong number of arguments provided, aborting."
    sys.exit(1)

# Setup logger
log = logging.getLogger('alert_manager')
lf = os.path.join(os.environ.get('SPLUNK_HOME'), "var", "log", "splunk", "risk_handler.log")
fh     = logging.handlers.RotatingFileHandler(lf, maxBytes=25000000, backupCount=5)
formatter = logging.Formatter("%(asctime)-15s %(levelname)-5s %(message)s")
fh.setFormatter(formatter)
log.addHandler(fh)
log.setLevel(logging.DEBUG)

# Parse arguments
job_path = sys.argv[8]

if os.name == "nt":
    match = re.search(r'dispatch\\([^\\]+)\\', job_path)
else:
    match = re.search(r'dispatch\/([^\/]+)\/', job_path)

job_id = match.group(1)

stdinArgs = sys.stdin.readline()
stdinLines = stdinArgs.strip()
sessionKeyOrig = stdinLines[11:]
sessionKey = urllib.unquote(sessionKeyOrig).decode('utf8')
alert = sys.argv[4]

log.debug("Parsed arguments: job_path=%s job_id=%s sessionKey=%s alert=%s" % (job_path, job_id, sessionKey, alert))

# Need to set the sessionKey (input.submit() doesn't allow passing the sessionKey)
splunk.setDefault('sessionKey', sessionKey)

# Finished initialization

log.info("alert_handler started because alert '%s' with id '%s' has been fired." % (alert, job_id))

#
# Get/set global settings
#

config = {}
config['index']                        = 'risks'

