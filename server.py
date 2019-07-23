#!/usr/bin/python3

import os
import asyncio
import websockets
import ssl
import pathlib
import urllib
import queue
import threading
from datetime import datetime
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler,HTTPServer

FLAG_QUEUE = queue.Queue()
RECENTS = {}
THROTTLE = {
        'red': {
            'secs': 5,
            'count': 2
        },
        'blue': {
            'secs': 5,
            'count': 2
        },
        'orange': {
            'secs': 5,
            'count': 2
        },
        'green': {
            'secs': 5,
            'count': 2
        },
}

def is_valid_team(team):
    return team in ('red', 'orange', 'blue', 'green')

class ThreadingServer(ThreadingMixIn, HTTPServer):
    pass
class SimpleHandler(BaseHTTPRequestHandler):
    def set_headers(self, http_code):
            self.send_response(http_code)
            self.send_header('Content-Type','text/html')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
    def do_GET(self):
        global THROTTLE
        print("request")
        cmd = self.path.split("/")[1].split('?')[0]
        params = {}
        if "?" in self.path:
            params = dict(urllib.parse.parse_qsl(self.path.split("?")[1], True))
        if cmd == 'capture':
            if not params.get('flag', None):
                self.set_headers(500)
                self.wfile.write(bytes(r'''
                <html><body>
                    <h1>No team name specified</h1><p>In order to score, set the <code>flag</code> parameter to the color of your team.
                </body></html''', 'ascii'))
                return
            team = params['flag']
            if not is_valid_team(team):
                self.set_headers(500)
                self.wfile.write(bytes(r'''
                <html><body>
                    <h1>Bad team name specified</h1><p>In order to score, set the <code>flag</code> parameter to the color of your team.
                </body></html''', 'ascii'))
                return
            global FLAG_QUEUE
            global RECENTS
            if not RECENTS.get(team, None):
                RECENTS[team] = {'count':0, 'first_capture':datetime.now()}
            RECENTS[team]['count'] += 1

            if RECENTS[team]['count'] > THROTTLE[team]['count'] and (datetime.now() - RECENTS[team]['first_capture']).seconds < THROTTLE[team]['secs']:
                print("throttling")
                RECENTS[team]['first_capture'] = datetime.now()
                self.set_headers(429)
                self.wfile.write(bytes("<html><body><h1>throttled! try again in %s seconds</h1></body></html>\n" % str(THROTTLE[team]['secs']), 'ascii'))
                return
            else:
                FLAG_QUEUE.put(team)
                if RECENTS[team]['count'] > THROTTLE[team]['count']:
                    RECENTS.pop(team)
                self.set_headers(200)
                self.wfile.write(bytes("<html><body><h1>captured the flag for %s team!</h1></body></html>\n" % str(team), 'ascii'))
            print(RECENTS)
        elif cmd == 'throttle':
            print('here0')
            if not params.get('captures', None):
                self.set_headers(500)
                self.wfile.write(bytes(r'''
                <html><body>
                    <h1>Missing <i>captures</i> parameter</h1>.
                </body></html''', 'ascii'))
                return
            print('here1')
            if not params.get('duration', None):
                self.set_headers(500)
                self.wfile.write(bytes(r'''
                <html><body>
                    <h1>Missing <i>duration</i> parameter</h1>.
                </body></html''', 'ascii'))
                return
            if not params.get('flag', None):
                self.set_headers(500)
                self.wfile.write(bytes(r'''
                <html><body>
                    <h1>Missing <i>flag</i> parameter</h1>.
                </body></html''', 'ascii'))
                return
            captures = int(params.get('captures'))
            duration = int(params.get('duration'))
            team = params.get('flag')
            if not is_valid_team(team):
                self.wfile.write(bytes(r'''
                <html><body>
                    <h1>Bad team flag color specified</h1>.
                </body></html''', 'ascii'))
                self.set_headers(500)
                return
            THROTTLE[team]['secs'] = duration
            THROTTLE[team]['count'] = captures
            print(THROTTLE)
            self.set_headers(200)
            self.wfile.write(bytes(r'''
            <html><body>
                <h1>Throttling <span style='color:%s'>%s</span> to %s capture%s every %s second%s!!!</h1>.
            </body></html''' % (team, team, captures, captures > 1 and 's' or '', duration, duration > 1 and 's' or ''), 'ascii'))
        elif cmd == 'showthrottles':
            self.set_headers(200)
            self.wfile.write(bytes(r'''
            <html><body>
                <h1>Active throttles</h1>
                <br />
                <table style='text-align:right'>
                    <thead style='font-weight:bold'><td>Team</td><td>Captures</td><td>Duration</td></thead>
                    <tr><td style='color:red'>Red</td><td>%d</td><td>%d</td></tr>
                    <tr><td style='color:blue'>Blue</td><td>%d</td><td>%d</td></tr>
                    <tr><td style='color:orange'>Orange</td><td>%d</td><td>%d</td></tr>
                    <tr><td style='color:green'>Green</td><td>%d</td><td>%d</td></tr>
                </table>
            </body></html''' % (
                THROTTLE['red']['count'], THROTTLE['red']['secs'],
                THROTTLE['blue']['count'], THROTTLE['blue']['secs'],
                THROTTLE['orange']['count'], THROTTLE['orange']['secs'],
                THROTTLE['green']['count'], THROTTLE['green']['secs']),
            'ascii'))
        else:
            self.set_headers(200)
            self.wfile.write(bytes(r'''
                <html><body>
                <h1>Supported commands</h1>
                <ol>
                    <li><b>Capture flag</b>
                        <ul><li>Path: /capture</li>
                        <br />
                        <li>Parameter name: flag</li>
                        <li>Parameter value: <i>team</i></li></ul>
                    </li>
                    <br />
                    <li><b>Configure throttle</b>
                        <ul><li>Path: /throttle</li>
                        <br />
                        <li>Parameter name: captures</li>
                        <li>Parameter value: <i>capture limit</i></li>
                        <br />
                        <li>Parameter name: duration</li>
                        <li>Parameter value: <i>throttle period</i> (in seconds)</li>
                        <br />
                        <li>Parameter name: flag</li>
                        <li>Parameter value: <i>team</i> (team to apply throttle on)</li></ul>
                    </li>
                </ol>
                </body></html>
            ''', 'ascii'))

class CommandServer(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
        while True:
            try:
                ThreadingServer(("0.0.0.0", 3389), SimpleHandler).serve_forever()
            except KeyboardInterrupt:
                print('shutting down server')

async def hello(websocket, path):
    global FLAG_QUEUE
    for flag in iter(FLAG_QUEUE.get, None):
        try:
            await asyncio.wait_for(websocket.send(flag), timeout=2)
        except asyncio.TimeoutError:
            print("timeout, closing connection")
            try:
                await websocket.close()
            except:
                print("double timeout")
        print("sending current color:", flag)

class WebSocketServer(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            start_server = websockets.serve(hello, '*', 80, origins=None, timeout=2)
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()

wss = WebSocketServer('wss')
cmdserver = CommandServer('cmdserver')

cmdserver.start()
wss.start()

wss.join()
cmdserver.join()
