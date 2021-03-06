#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
app = Flask(__name__)

from pydbus import SessionBus
bus = SessionBus()
try:
    player = bus.get("github.zhangn1985.dbplay")
except:
    from playthread import Mpvplayer
    player = Mpvplayer()
    player.start()

import json
import types

from ykdl.common import url_to_module

@app.route('/play', methods=['POST', 'GET'])
def play():
    if request.method == 'POST':
        url = request.form['url']
        try:
            islist = request.form['list']
            islist = islist == "True"
        except:
            islist = False
        m,u = url_to_module(url)
        if not islist:
            parser = m.parser
        else:
            parser = m.parser_list
        try:
           info = parser(u)
        except AssertionError as e:
           return str(e)
        if type(info) is types.GeneratorType or type(info) is list:
            for i in info:
                player_args = i.extra
                player_args['title'] = i.title
                urls = i.streams[i.stream_types[0]]['src']
                video = json.dumps({"urls": urls, "args": player_args})
                player.play(video)
        else:
            player_args = info.extra
            player_args['title'] = info.title
            urls = info.streams[info.stream_types[0]]['src']
            video = json.dumps({"urls": urls, "args": player_args})
            player.play(video)
        return "OK"
    else:
        return "curl --data-urlencode \"url=<URL>\" http://IP:5000/play"

@app.route('/stop')
def stop():
    player.stop()
    return "OK"

@app.route('/')
def index():
    string = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Web YKDL</title>
</head>
<body>
<style>form{float:left;}</style>
<form action="/play" method="post" target="_blank">
  输入视频网址: <input type="text" name="url" />
播放列表？<input type="checkbox" name="list" value="True" />
  <input type="submit" value="播放" />
</form>
<form action="/stop" method="get" target="_blank">
  <input type="submit" value="停止" />
</form>

</body>
</html>
"""
    return string
if __name__ == '__main__':
    app.run(host='0.0.0.0')
