import logging
import os
import sys
import json
import shutil
import cherrypy
import re
import time
import datetime
import urllib
import socket
import hashlib
import uuid

#from splunk import AuthorizationFailed as AuthorizationFailed
import splunk
import splunk.appserver.mrsparkle.controllers as controllers
import splunk.appserver.mrsparkle.lib.util as util
import splunk.input as input
import splunk.bundle as bundle
import splunk.entity as entity
from splunk.appserver.mrsparkle.lib import jsonresponse
from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path
import splunk.clilib.bundle_paths as bundle_paths
from splunk.util import normalizeBoolean as normBool
from splunk.appserver.mrsparkle.lib.decorators import expose_page
from splunk.appserver.mrsparkle.lib.routes import route
import splunk.rest as rest

dir = os.path.join(util.get_apps_dir(), 'risk_manager', 'bin', 'lib')
if not dir in sys.path:
    sys.path.append(dir)    

#sys.stdout = open('/tmp/stdout2', 'w')
#sys.stderr = open('/tmp/stderr2', 'w')    


def setup_logger(level):
    """
    Setup a logger for the REST handler.
    """

    logger = logging.getLogger('splunk.appserver.risk_manager.controllers.Helpers')
    logger.propagate = False # Prevent the log messages from being duplicated in the python.log file
    logger.setLevel(level)

    file_handler = logging.handlers.RotatingFileHandler(make_splunkhome_path(['var', 'log', 'splunk', 'risk_manager_helpers_controller.log']), maxBytes=25000000, backupCount=5)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger(logging.DEBUG)

from splunk.models.base import SplunkAppObjModel
from splunk.models.field import BoolField, Field



class Helpers(controllers.BaseController):

    @expose_page(must_login=True, methods=['GET']) 
    def get_indexes(self, **kwargs):
        logger.info("Get indexes")

        user = cherrypy.session['user']['name']
        sessionKey = cherrypy.session.get('sessionKey')

        
        uri = '/services/admin/indexes?output_mode=json'
        serverResponse, serverContent = rest.simpleRequest(uri, sessionKey=sessionKey, method='GET')
        #logger.debug("response: %s" % serverContent)
        entries = json.loads(serverContent)
        
        index_list = []
        if len(entries['entry']) > 0:
            for entry in entries['entry']:
                index_list.append(entry['name'])
        

        return json.dumps(index_list)

    @expose_page(must_login=True, methods=['GET']) 
    def get_savedsearch_description(self, savedsearch, app, **kwargs):
        user = cherrypy.session['user']['name']
        sessionKey = cherrypy.session.get('sessionKey')

        uri = '/servicesNS/nobody/%s/admin/savedsearch/%s?output_mode=json' % (app, savedsearch)
        serverResponse, serverContent = rest.simpleRequest(uri, sessionKey=sessionKey, method='GET')

        savedSearchContent = json.loads(serverContent)

        if savedSearchContent["entry"][0]["content"]["description"]:
            return savedSearchContent["entry"][0]["content"]["description"]
        else:
            return ""

    @expose_page(must_login=True, methods=['POST']) 
    def save_risks(self, contents, **kwargs):

        logger.info("Saving risks...")

        user = cherrypy.session['user']['name']
        sessionKey = cherrypy.session.get('sessionKey')
        splunk.setDefault('sessionKey', sessionKey)
        

        config = {}
        config['index'] = 'risks'
        
        restconfig = entity.getEntities('configs/risk_manager', count=-1, sessionKey=sessionKey)
        if len(restconfig) > 0:
            if 'index' in restconfig['settings']:
                config['index'] = restconfig['settings']['index']

        logger.debug("Global settings: %s" % config)

        # Parse the JSON
        parsed_contents = json.loads(contents)
        logger.debug("Contents: %s" % contents)

        for entry in parsed_contents:
            if '_key' in entry and entry['_key'] != None:

                uri = '/servicesNS/nobody/risk_manager/storage/collections/data/risks/' + entry['_key']
                
                # Get current risk
                serverResponse, risk = rest.simpleRequest(uri, sessionKey=sessionKey)
                logger.debug("Current risk: %s" % risk)
                risk = json.loads(risk)

                # Update risk if score has changed
                if int(risk['risk_score']) != int(entry['risk_score']):
                    logger.info("Updating risk_object_type=%s risk_object=%s to score=%s." % (entry['risk_object_type'], entry['risk_object'], entry['risk_score']))
                    del entry['_key']
                    if 'risk_id' in risk:
                        entry['risk_id'] = risk['risk_id']
                    else:
                        entry['risk_id'] = str(uuid.uuid4())
                        risk['risk_id'] = entry['risk_id']
                    entryStr = json.dumps(entry)

                    serverResponse, serverContent = rest.simpleRequest(uri, sessionKey=sessionKey, jsonargs=entryStr)
                    logger.debug("Updated entry. serverResponse was ok")

                    now = datetime.datetime.now().isoformat()
                    event = 'time="%s" risk_id="%s" action="update_risk_score" alert="Risk Score Tuner" user="%s" risk_object_type="%s" risk_object="%s" risk_score="%s" previous_risk_score="%s"' % (now, risk['risk_id'], user, entry['risk_object_type'], entry['risk_object'], entry['risk_score'], risk['risk_score'])
                    logger.debug("Event will be: %s" % event)
                    input.submit(event, hostname = socket.gethostname(), sourcetype = 'risk_scoring', source = 'helpers.py', index = config['index'])
                else:
                    logger.info("Won't update risk_object_type=%s risk_object=%s, since score didn't change." % (entry['risk_object_type'], entry['risk_object']))

        return 'Done'
