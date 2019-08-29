import logging, time, os, json
from configobj import ConfigObj
from twisted.web import resource
from util import json_personas

class run(resource.Resource):
    def __init__(self):
        self.name = "MagmaAPI"
        self.log = logging.getLogger('root')
        self.config = ConfigObj('config.ini')
        self.abilitiesOwned = []

    isLeaf = True

    def render_GET(self, request):
        uri=request.uri.decode()
        self.log.info(f"[{self.name}] GET uri={uri}")
        request.setHeader('content-type', 'text/xml; charset=utf-8')

        if uri == '/nucleus/authToken':
            reply = '<success><token code="NEW_TOKEN">'+self.config['Settings']['SessionID']+'</token></success>'
            self.log.info(f"[{self.name}] GET reply={reply}")
            return reply.encode('utf-8', 'ignore')

        elif '/nucleus/check/user/' in uri:
            if uri.split('/')[-1] == '1000':
                reply = '<name>test-server</name>'
            else:
                reply = '<name>'+json_personas.global_stats.get('name', 'undefined')+'</name>'
            self.log.info(f"[{self.name}] GET reply={reply}")
            return reply.encode('utf-8', 'ignore')

        elif uri.split(':')[0] == '/relationships/roster/nucleus':
            reply = '<update><id>1</id><name>Test</name><state>ACTIVE</state><type>server</type><status>Online</status><realid>'+uri.split(':')[1]+'</realid></update>'
            self.log.info(f"[{self.name}] GET reply={reply}")
            return reply.encode('utf-8', 'ignore')

        elif uri == '/ofb/products':
            reply = open("src/xml/products.xml", "r")
            self.log.info(f"[{self.name}] GET reply=xml/products.xml")
            return reply.read().encode('utf-8', 'ignore')
        
        elif uri.find('/nucleus/entitlements/') == 0:
            reply = open("src/xml/entitlements.xml", "r")
            self.log.info(f"[{self.name}] GET reply=xml/entitlements.xml")
            return reply.read().encode('utf-8', 'ignore')

        elif '/nucleus/wallets/' in uri:
            persona_id = uri.split('/nucleus/wallets/')[1]
            pjson = json.load(open(json_personas.path+persona_id+'.json', "r"))
            reply = open("src/xml/wallets.xml", "r").read()
            reply = reply.replace('[vp]', str(pjson.get('c_wallet_valor', '0')))
            reply = reply.replace('[hp]', str(pjson.get('c_wallet_hero', '0')))
            reply = reply.replace('[bf]', str(pjson.get('c_wallet_battlefunds', '0')))
            self.log.info(f"[{self.name}] GET reply=xml/wallets.xml")
            return reply.encode('utf-8', 'ignore')

    def render_POST(self, request):
        uri=request.uri.decode()
        self.log.info(f"[{self.name}] POST uri={uri}")

        if uri.split(':')[0] == '/relationships/status/nucleus':
            request.setHeader('content-type', 'text/plain; charset=utf-8')
            reply = '<update><id>1</id><name>Test</name><state>ACTIVE</state><type>server</type><status>Online</status><realid>' + uri.split(':')[1] + '</realid></update>'
            self.log.info(f"[{self.name}] POST reply={reply}")
            return reply.encode('utf-8', 'ignore')

        elif '/ofb/purchase/' in uri:
            entitlement_id = uri.split('/ofb/purchase/')[1].split('/')[1]
            if 2999 > int(entitlement_id) > 2000:
                self.abilitiesOwned.append(entitlement_id)
            reply = '<success></success>'
            self.log.info(f"[{self.name}] POST reply={reply}")
            return reply.encode('utf-8', 'ignore')

        elif '/nucleus/refundAbilities/' in uri:
            if self.abilitiesOwned == []:
                reply = '<success code="NO_CHANGE"></success>'
            else:
                persona_id = uri.split('/nucleus/refundAbilities/')[1].split('/')[0]
                pjson = json.load(open(json_personas.path+persona_id+'.json', "r"))
                reply = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><success code="REFUNDED"><walletAccount><currency>_DH</currency><balance>'+str(pjson.get('c_wallet_hero', '0'))+'</balance></walletAccount><refunded>'
                for ability in self.abilitiesOwned:
                    reply += '<item>'+ability+'</item>'
                reply += '</refunded></success>'
                self.abilitiesOwned.clear()
            self.log.info(f"[{self.name}] POST reply={reply}")
            return reply.encode('utf-8', 'ignore')