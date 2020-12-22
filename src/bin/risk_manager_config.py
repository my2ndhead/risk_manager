
import splunk.admin as admin
import splunk.entity as entity
    

class RiskHandlerApp(admin.MConfigHandler):
    '''
    Set up supported arguments
    '''
    
    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in ['index']:
                self.supportedArgs.addOptArg(arg)
        pass

    def handleList(self, confInfo):
        confDict = self.readConf("risk_manager")
        if None != confDict:
            for stanza, settings in confDict.items():
                for key, val in settings.items():
                    #if key in ['save_results']:
                    #    if int(val) == 1:
                    #        val = '1'
                    #    else:
                    #        val = '0'
                    if key in ['index'] and val in [None, '']:
                        val = ''                            

                    confInfo[stanza].append(key, val)

    def handleEdit(self, confInfo):
        name = self.callerArgs.id
        args = self.callerArgs
        
        if self.callerArgs.data['index'][0] in [None, '']:
            self.callerArgs.data['index'][0] = ''
        
        #if int(self.callerArgs.data['save_results'][0]) == 1:
        #    self.callerArgs.data['save_results'][0] = '1'
        #else:
        #    self.callerArgs.data['save_results'][0] = '0'             
                
        self.writeConf('risk_manager', 'settings', self.callerArgs.data)                        
                    
# initialize the handler
admin.init(RiskHandlerApp, admin.CONTEXT_APP_AND_USER)
