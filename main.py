import websocket
import requests
import json
import re
import settings


class Hitbox:

    def __init__(self):

        self.ws = websocket.WebSocket()
        self.auth_token = None

    def __enter__(self):

        server_list = requests.get(settings.hitbox_api.format(api=settings.server_list_path))

        if not server_list.ok:

            print "Could not get server list!"
            return None

        server_id = server_list.json()[0]['server_ip']
        socket_id = self.get_websocket_conn_id(server_id)

        self.ws.connect(socket_id)
        self.auth_token = self.get_auth_token()
        self.join_channel(settings.channel, self.auth_token)

        return self

    def __exit__(self, exctype, value, traceback):

        self.ws.close()

    def main(self):

        while self.ws.connected:
            rec = self.ws.recv()

            if rec == '2::':
                self.ws.send("2::")

            elif rec == "1::":
                pass

            else:
                chat_data = json.loads(json.loads(rec.strip("5:"))['args'][0])

                if chat_data['method'] == 'chatMsg':
                    msg = chat_data['params']['text']
                    print chat_data['params']['name'] + ": " + msg

                    if re.search("(.png)|(.jpg)|(.jpeg)|(.gif)$", msg):
                        pass
 #                       self.send_message('chaosargate', msg)
                    elif msg == '!test':
                        print "123"
#                        self.send_message('chaosargate', 'This is a test')

    def get_websocket_conn_id(self, server_id):

        url = '{http}{server_id}{socket}'.format(http=settings.http_head,
                                                 server_id=server_id,
                                                 socket=settings.socket_base)
        ws_url = '{ws}{server_id}{socket}{conn_id}'

        conn_resp = requests.get(url.format(server_id=server_id))

        if conn_resp.ok:
            conn_id = conn_resp.content.split(":")[0]
            return ws_url.format(ws=settings.ws_head,
                                 server_id=server_id,
                                 socket=settings.socket_base,
                                 conn_id="websocket/{id}".format(id=conn_id))

        else:
            return None

    def join_channel(self, channel, auth_token):

        request = '''5:::{
        "name":"message",
        "args":[
            {
                "method":"joinChannel",
                "params":{
                    "channel":"%s",
                    "name":"%s",
                    "token":"%s"
                }
            }
        ]
        }''' % (channel, settings.username, auth_token)

        self.ws.send(request)

        return None

    def get_auth_token(self):

        request = '''{
        "login":"%s",
        "pass":"%s",
        "app":"desktop"
        }''' % (settings.username, settings.password)

        auth = requests.post(url=settings.hitbox_api.format(api=settings.auth_token_path), data=request)

        if auth.ok:
            return auth.json()['authToken']

        else:
            return None

    def send_message(self, channel, msg):

        request = '''5:::{
        "name":"message",
        "args":[
            {
                "method":"chatMsg",
                "params":{
                    "channel":"%s",
                    "name":"%s",
                    "nameColor":"D44F38",
                    "text":"%s"
                }
            }
        ]
        }''' % (channel, settings.username, msg)

        self.ws.send(request)

        return None


if __name__ == '__main__':
    with Hitbox() as hb:
        hb.main()
