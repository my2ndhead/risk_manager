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
import uuid

sys.stdout = open('/tmp/stdout2', 'a')
sys.stderr = open('/tmp/stderr2', 'a')

dir = os.path.join(os.path.join(os.environ.get('SPLUNK_HOME')), 'etc', 'apps', 'risk_manager', 'bin', 'lib')
if not dir in sys.path:
    sys.path.append(dir)

from CsvLookup import *
from CsvResultParser import *

# Get result_id depending of digest mode
def getResultId(digest_mode, job_path):
    if digest_mode == False:
            result_id = re.search("tmp_(\d+)\.csv\.gz", job_path).group(1)
            return result_id
    else:
            return 0

# Get alert results
def getResults(job_path, risk_id):
    parser = CsvResultParser(job_path)
    results = parser.getResults({ "risk_id": risk_id })

    return results

# Get risk_score for risk_object
def getRiskScore(risk_object):
    risk = {}
    risk['risk_score'] = '0'

    query = {}
    query['risk_object'] = risk_object

    log.debug("Query for risk object: %s" % urllib.quote(json.dumps(query)))
    uri = '/servicesNS/nobody/risk_manager/storage/collections/data/risks?query=%s' % urllib.quote(json.dumps(query))
    serverResponse, serverContent = rest.simpleRequest(uri, sessionKey=sessionKey)
    log.debug("Risk object: %s" % serverContent)
    risk = json.loads(serverContent)
    if len(risk) > 0:
        log.info("Found risk_object %s" % risk_object)
        key = risk[0]['_key']
        risk_score = int(risk[0]['risk_score'])
        if (risk_score < 0):
	    risk_score = 0

        return key, risk_score 
    else:
        log.info("No risks_object %s found, switching back to defaults." % alert)
        return "null" ,0

# Update risk score for risk object
def updateRiskScore(key, risk_id, risk_object_type, risk_object, risk_score , current_risk_score):
    risk = {}
    log.debug("Risk Score: %s" % risk_score) 
    log.debug("Current Risk Score: %s" % current_risk_score) 
    risk_score = int(risk_score) + current_risk_score

    #risk['_key'] = key
    risk['risk_id'] = risk_id
    risk['risk_object_type'] = risk_object_type
    risk['risk_object'] = risk_object
    risk['risk_score'] = risk_score
  
    risk_scoring = json.dumps(risk)
    log.debug("Risk Scoring: %s" % risk_scoring)
    if (key=="null"): 
        uri = '/servicesNS/nobody/risk_manager/storage/collections/data/risks/'  
    else:
        uri = '/servicesNS/nobody/risk_manager/storage/collections/data/risks/'+key
    serverResponse, serverContent = rest.simpleRequest(uri, sessionKey=sessionKey, jsonargs=risk_scoring)  
    log.debug("Risk Score updated to collection: %s" % risk_scoring) 

def writeRiskScoringEventToIndex(risk_id, alert, job_id, risk_object_type, risk_object, risk_score , current_risk_score):
    log.info("Attempting Risk Scoring Event write to index=%s" % config['index'])
    now = datetime.datetime.now().isoformat()
    risk_score = risk_score + current_risk_score
    if (risk_score < 0):
        risk_score = 0

    risk_scoring_event=('time="%s" risk_id="%s" alert="%s" job_id="%s" action="update_risk_score" risk_object_type="%s" risk_object="%s" risk_score="%s" previous_risk_score="%s"' % (now, risk_id, alert, job_id, risk_object_type, risk_object, risk_score , current_risk_score))

    input.submit(risk_scoring_event, hostname = socket.gethostname(), sourcetype = 'risk_scoring', source = 'risk_handler.py', index = config['index'])
    log.info("Risk Scoring Event written to index=%s" % config['index'])

# Write risk_result to collection
def writeResultToCollection(results):
    risk_result = json.dumps(results)
    log.debug("Result: %s" % risk_result)
    uri = '/servicesNS/nobody/risk_manager/storage/collections/data/risk_results'
    serverResponse, serverContent = rest.simpleRequest(uri, sessionKey=sessionKey, jsonargs=risk_result)
    log.debug("Results for risk_id=%s written to collection." % (risk_id))


# Init
#
start = time.time()

if len(sys.argv) < 9:
    print "Wrong number of arguments provided, aborting."
    sys.exit(1)

# Setup logger
log = logging.getLogger('risk_manager')
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

log.info("risk_handler started because alert '%s' with id '%s' has been fired." % (alert, job_id))

#
# Get/set global settings
#

config = {}
config['index']                        = 'risks'

restconfig = splunk.entity.getEntities('configs/risk_manager', count=-1, sessionKey=sessionKey)
if len(restconfig) > 0:
    for cfg in config.keys():
        if cfg in restconfig['settings']:
            if restconfig['settings'][cfg] == '0':
                config[cfg] = False
            elif restconfig['settings'][cfg] == '1':
                config[cfg] = True
            else:
                config[cfg] = restconfig['settings'][cfg]

log.debug("Parsed global risk handler settings: %s" % json.dumps(config))


#
# Get per risk settings
#
risk_config = {}
risk_config['risk_object']             = ''
risk_config['risk_score']              = ''
risk_config['collect_contributing_data']        = False
query = {}
query['alert'] = alert
log.debug("Query for alert settings: %s" % urllib.quote(json.dumps(query)))
uri = '/servicesNS/nobody/risk_manager/storage/collections/data/risk_settings?query=%s' % urllib.quote(json.dumps(query))
serverResponse, serverContent = rest.simpleRequest(uri, sessionKey=sessionKey)
log.debug("Risk settings: %s" % serverContent)
risk_settings = json.loads(serverContent)
if len(risk_settings) > 0:
    log.info("Found risk settings for %s" % alert)
    for key, val in risk_settings[0].iteritems():
        risk_config[key] = val
else:
    log.info("No risk settings found for %s, switching back to defaults." % alert)

log.debug("Risk config after getting settings: %s" % json.dumps(risk_config))

log.debug("risk_object=%s" % risk_config["risk_object"])

#
# Alert metadata
#
# Get alert metadata
uri = '/services/search/jobs/%s' % job_id
serverResponse, serverContent = rest.simpleRequest(uri, sessionKey=sessionKey, getargs={'output_mode': 'json'})
job = json.loads(serverContent)
alert_app = job['entry'][0]['acl']['app']
result_count = job['entry'][0]['content']['resultCount']
log.info("Found job for alert %s. Context is '%s' with %s results." % (alert, alert_app, result_count))

# Get savedsearch settings
uri = '/servicesNS/nobody/%s/admin/savedsearch/%s' % (alert_app, urllib.quote(alert))
try:
    savedsearchResponse, savedsearchContent = rest.simpleRequest(uri, sessionKey=sessionKey, getargs={'output_mode': 'json'})
except splunk.ResourceNotFound, e:
    log.error("%s not found in saved searches, so we're not able to get digest mode. Have to stop here. Exception: %s" % (alert, e))
    sys.exit(1)
except:
    log.error("Unable to get savedsearch. Unexpected error: %s" % sys.exc_info()[0])

savedsearchContent = json.loads(savedsearchContent)
log.debug("Parsed savedsearch settings: digest_mode=%s" % savedsearchContent['entry'][0]['content']['alert.digest_mode'] )

# Add attributes id to alert metadata
job['job_id']    = job_id

# Set globals
alert_time = job['entry'][0]['published']
digest_mode = savedsearchContent['entry'][0]['content']['alert.digest_mode']

###############################
# Risk creation starts here

# Create unique id
risk_id = str(uuid.uuid4())

results = getResults(job_path, risk_id)
result_id = getResultId(digest_mode, job_path)

# Check if we have to store contributing data
log.info("Collect_contributing_data=%s" % (risk_config['collect_contributing_data']))
if (risk_config['collect_contributing_data'] == True):
  writeResultToCollection(results)
  log.info("Alert results for job_id=%s risk_id=%s result_id=%s written to collection risk_results" % (job_id, risk_id, str(result_id)))

# Get current Risk Score
risk_object_value = results['fields'][0][risk_config["risk_object"]]
key, current_risk_score = getRiskScore(risk_object_value)

log.debug("key=%s risk_object=%s risk_object_value=%s risk_score=%s" % (key, risk_config["risk_object"], risk_object_value, risk_config["risk_score"]))

updateRiskScore(key, risk_id, risk_config["risk_object"], risk_object_value, risk_config["risk_score"], current_risk_score)

writeRiskScoringEventToIndex(risk_id, alert, job_id, risk_config["risk_object"], risk_object_value, int(risk_config["risk_score"]), current_risk_score)

# Done creating risks

#
# Finish
#
end = time.time()
duration = round((end-start), 3)
log.info("Risk handler finished. duration=%ss" % duration)

