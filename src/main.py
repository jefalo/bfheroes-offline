#!python3.7
import sys, os, time, logging, platform, subprocess
from configobj import ConfigObj
from time import strftime
from twisted.internet import ssl, reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.web import server, resource
from util import json_services
from util.logger import StreamHandler, FileHandler
from fesl import fesl_client_manager, fesl_server_manager
from theater import theater_client_manager, theater_server_manager
from magma import magma_api
from webbrowser import webbrowser_api

def run():

    log = logging.getLogger('root')
    CONFIG = ConfigObj('config.ini')

    if platform.system() != "Windows":
        log.warning('Will not attempt to automatically start the game since we are not running on Windows.')
    else:
        log.debug('Attempting to automatically start the game...')
        try:
            subprocess.STARTF_USESHOWWINDOW = 1
            cmdline = 'cd '+CONFIG['Paths']['GameFolderName']+'&BFHeroes.exe +webBrowser '+CONFIG['WebBrowser']['UseWebBrowser']+' +sessionId '+CONFIG['Settings']['SessionID']+' +ignoreAsserts 1 +magma '+CONFIG['Magma']['UseMagma']+' +magmaProtocol '+CONFIG['Magma']['MagmaProtocol']+' +magmaHost '+CONFIG['Settings']['Hostname']+' /overridessl 0 /overridehostname óíñ╜ú╜ú╜ó'
            subprocess.Popen(cmdline, shell=True)
            log.info('Game started.')
        except Exception as err:
            log.error(err)
            log.error('A strange error occured whilst trying to start the game. Have you renamed any files?')

    services = json_services.services
    for service in services:
        port = services[service]['port']
        
        if service != "MagmaAPI" and service != "WebBrowserAPI":
            try:
                factory = Factory()
                
                if service == "FESLClientManager":
                    factory.protocol = fesl_client_manager.run
               
                elif service == "FESLServerManager":
                    factory.protocol = fesl_server_manager.run
                
                elif service == "TheaterClientManager":
                    factory.protocol = theater_client_manager.run
                    reactor.listenUDP(port, theater_client_manager.run_datagram())
                
                elif service == "TheaterServerManager":
                    factory.protocol = theater_server_manager.run
                    reactor.listenUDP(port, theater_server_manager.run_datagram())
                
                reactor.listenTCP(port, factory)
            
            except Exception as err:
                log.error(err)
                sys.exit(1)
        else:
            
            try:

                if service == "MagmaAPI":
                    site = server.Site(magma_api.run())

                elif service == "WebBrowserAPI":
                    site = server.Site(webbrowser_api.run())

                reactor.listenTCP(port, site)
            
            except Exception as err:
                log.error(err)
                sys.exit(1)
        
        log.info(f'[{service}] Now listening on port {str(port)}')
    reactor.run()

def setup_logging():

    log_file = 'logs/backend-'+strftime('%b-%d-%Y-%H-%M-%S')+'.log'
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    log = logging.getLogger('root')
    log.setLevel('DEBUG')
    log.addHandler(StreamHandler())
    log.addHandler(FileHandler(log_file))

if __name__ == '__main__':
    setup_logging()
    run()

