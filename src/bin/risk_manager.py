import sys
import os
import logging, logging.handlers
import splunk
import json

# We know where the libs are so we just append them to the path
SPLUNK_HOME = os.environ['SPLUNK_HOME']
sys.path.append(os.path.join(SPLUNK_HOME, 'etc', 'apps', 'risk_manager', 'lib'))
sys.path.append(os.path.join(SPLUNK_HOME, 'etc', 'apps', 'risk_manager', 'lib', 'splunklib'))


def setup_logging():
    logger = logging.getLogger('splunk.risk_manager')    
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = "risk_manager.log"
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
    LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
    splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a') 
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger


# Import Splunk Enterprise SDK
import splunklib.client as client

# Import csv results parser modules
from CsvLookup import CsvLookup
from CsvResultParser import CsvResultParser

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        #sys.stdout = open('/tmp/stdout2', 'a')
        #sys.stderr = open('/tmp/stderr2', 'a')
        logger=setup_logging()
        try:
            logger.info('action="starting"')
        except:
            logger.exception(self, message="Logger Exception")

        #
        # Setup Payload
        #
        payload = json.loads(sys.stdin.read())

        session_key = payload.get('session_key')
        job_id = payload.get('sid')
        search_name = payload.get('search_name')

        logger.info('session_key="{session_key}"'.format(session_key=session_key))
        logger.info('job_id="{job_id}"'.format(job_id=job_id))
    