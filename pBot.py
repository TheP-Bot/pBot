import mechanize, re, os, pymongo, json, requests
from fbchat import Client, log
from fbchat.models import *
from datetime import datetime, timedelta
from dateutil.relativedelta import *

# os.chdir("C:\\Users\\asraf\\OneDrive\\programming\\Python\\Practice")


global logstatus, active, currentVersion, newVersion, newSession
currentVersion = 'v1.0.1/n'

def cls():
    import sys,os
    if sys.platform == 'linux' or sys.platform == 'darwin' :
        os.system('clear')
    elif sys.platform == 'win32':
        os.system('cls')

def checkUpdate():

    newVersion = requests.get("https://raw.githubusercontent.com/TheP-Bot/pBot/main/version.info").text

    if newVersion != currentVersion:

        print("Updating..........")
        os.remove("pBot.py")
        code = requests.get("https://raw.githubusercontent.com/TheP-Bot/pBot/main/pBot.py").text
        file = open("pBot.py", "w")
        file.write(code)
        file.close()
        os.system("python pBot.py")


def newLogin():
    
    while True:
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(),max_time=1)
        br.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; fi-fi) AppleWebKit/420+ (KHTML, like Gecko) Safari/419.3')]
        br.open('https://m.facebook.com')
        br._factory.is_html = True
        br.select_form(nr=0)
        br.form['email'] = str(input("- Fb Username : "))
        br.form['pass'] = str(input("- Fb Password : "))
        cls()
        print("- Trying to login.......\n")
        br.submit()
        url = br.geturl()
        if "checkpoint" in url:
            cls()
            print("- Your Id Is In Checkpoin ! Maybe:- \n\n   1. Your Id has 2 Factor enabled. or,\n   2. Your Id Is Locked.\n\n- Please Check and Try Again!!\n \n- Note : You can turn on 2 step again after a sucessfull login!\n\n")
 
        elif 'save-device' in url:
            print("- Login Successful! Please Wait......\n\n")
            break
        
        else:
            cls()
            print("- Maybe Your Id Pass Is Wrong!\n- Please Try Agin!\n\n")



    cookieJar = str(br._ua_handlers['_cookies'].cookiejar)
    c_user = re.findall('c_user=(\d*)\sfor', cookieJar)[0]
    xs = re.findall('xs=(\S*)\sfor', cookieJar)[0]
    cookies = {
    "sb": "xasyYmAoy1tRpMGYvLxgkHBF",
    "fr": "0NxayJuewRHQ30OX3.AWVJwIYNh0Tt8AJv6kSwDamhkoM.BiMrVd.Iu.AAA.0.0.BiMtVZ.AWXMVaiHrpQ",
    "c_user": c_user,
    "datr": "xasyYs51GC0Lq5H5lvXTl5zA",
    "xs": xs
    }
    jsonData = json.dumps(cookies, indent=4)
    with open("cookies.json", "w") as outfile:
        outfile.write(jsonData)
    return cookies

def autoLogin():
    
    global logstatus, cookies, client, c_user, xs, newSession
    try:
        with open('cookies.json') as f:
            print("- Trying to Auto Login......\n")
            cookies = json.load(f)
    except FileNotFoundError:
        cookies = newLogin()
    except Exception as ex:
        print(ex)

    


    for i in range(3):
        try:
            client = ChatBot("",
            "", 
            session_cookies=cookies)
            logstatus = client.isLoggedIn()
            c_user = cookies["c_user"]
            xs = cookies["xs"]
            break
        except FBchatException:
            if i != 2:
                cls()
                continue
            else:
                newSession = True
                cls()
                print("- It seems like your login is expired.. \n- Please login again !")
                os.remove("cookies.json")
                autoLogin()


def detabase():
    myclient = pymongo.MongoClient("mongodb+srv://pBot:%24%24Nabil%24%24@pbot.wttlhxr.mongodb.net/?retryWrites=true&w=majority")
    global mydb, userInfo
    mydb = myclient["Users"]
    users = list([i['c_user'] for i in mydb.userInfo.find({})])
    if c_user not in users:
        print("- Regestaring New user !!")
        info = {
            "name" : client.fetchUserInfo(c_user)[c_user].name,
            "c_user" : c_user,
            "xs" : xs,
            "exp" : datetime(2023, 1, 1),
            "groups" : [],
            "posts" : [],
            "autoRep" : {},
            "offliineMsg" : "I'm Offline Now!!"
        }
        mydb.userInfo.insert_one(info)
        userInfo = mydb.userInfo.find({"c_user" : c_user})
        

    else:
        userInfo = mydb.userInfo.find({"c_user" : c_user})[0]
        name = userInfo["name"]
        print(f"Welcome Back {name}!!")

        try:
            if newSession :
                mydb.userInfo.update_one({"c_user":c_user},{"$set":{"xs":xs}})
        except:
            pass

def expired():
    exp = mydb.userInfo.find({"c_user" : c_user})[0]["exp"]
    cdate = datetime.now()
    if exp > cdate:
        return False
    else:
        return True
        

class ChatBot(Client):
    active = True
    def onMessage(self, mid=None, author_id=None, message_object=None, thread_id=None, thread_type=ThreadType.USER, **kwargs):
        if author_id == self.uid:
            fullmsg = str(message_object.text)
            command = fullmsg.split(" ")[0].lower()
            msg = fullmsg.replace(fullmsg.split(" ")[0],"")

            if "?addgroup" == command or "?ag" == command:
                groups = mydb.userInfo.find({"c_user" : c_user})[0]["groups"]
                groups.append(thread_id)
                mydb.userInfo.update_one({"c_user":c_user},{"$set":{"groups":groups}})
                self.send(Message(text="- Group Added! [ pBot ]"),thread_id=thread_id, thread_type=thread_type)

            elif "?removegroup" == command or "?rg" == command:
                groups = mydb.userInfo.find({"c_user" : c_user})[0]["groups"]
                groups.remove(thread_id)
                mydb.userInfo.update_one({"c_user":c_user},{"$set":{"groups":groups}})
                self.send(Message(text="- Group Removed ! [ pBot ] "),thread_id=thread_id, thread_type=thread_type)

            elif "?post" in command:
                if not expired():
                    try:
                        postNo = int(command.split()[-1]) + 1
                    except:
                        postNo = 0
                    groups = mydb.userInfo.find({"c_user" : c_user})[0]["groups"]
                    post = mydb.userInfo.find({"c_user" : c_user})[0]["posts"][postNo]
                    for group in groups:
                        try:
                            self.send(Message(text=post+"\n\n[ pBot ]"),thread_id=group, thread_type=thread_type)
                        except:
                            continue
                else:

                    self.send(Message(text="- Sorry Sir,\n- Your Subscription Is Expired!\n\n[ pBot ]"),thread_id=group, thread_type=thread_type)



                
            elif "?addpost" == command:
                posts = mydb.userInfo.find({"c_user" : c_user})[0]["posts"]
                posts.append(msg)
                mydb.userInfo.update_one({"c_user":c_user},{"$set":{"posts": posts}})
                self.send(Message(text="- Post Added! [ pBot ]"),thread_id=thread_id, thread_type=thread_type)

            elif "?offlinereply" == command or command == "?or" :
                if len(msg) != 0:
                    mydb.userInfo.update_one({"c_user":c_user},{"$set":{"offliineMsg":msg}})
                    self.send(Message(text="- Offline Msg Updated! [ pBot ]"),thread_id=thread_id, thread_type=thread_type)

            elif command == "?offline":
                self.active = False

            elif command == "?online":
                self.active = True

            
        

        else:
            
                if self.active == False:
                    if thread_type == ThreadType.USER:
                        if not expired():
                            offlineMsg = mydb.userInfo.find({"c_user" : c_user})[0]["offliineMsg"]
                            self.send(Message(text=offlineMsg+"\n\n[ pBot ]"),thread_id=thread_id, thread_type=thread_type)

                    elif thread_type == ThreadType.GROUP:
                        try:
                            if self.uid in [mentioned.thread_id for mentioned in message_object.mentions]:
                                if not expired():
                                    offlineMsg = mydb.userInfo.find({"c_user" : c_user})[0]["offliineMsg"]
                                    self.send(Message(text=offlineMsg+"\n\n[ pBot ]"),thread_id=thread_id, thread_type=thread_type)
                        except:
                            pass
                            
            

                




cls()
checkUpdate()
autoLogin()

if logstatus:
    detabase()
    while True:
        command = int(input('- Choose What To Do : \n\n- 1. See Your Expiry Date.\n- 2. See Your Posts.\n- 3. See Auto Replies.\n- 4. Start Listening Commands.\n\n- Reply With Number : '))
        if command == 1:
            cls()
            exDate = userInfo["exp"]
            print(f"- Your Exp Date Is: {exDate.day}-{exDate.month}-{exDate.year}\n\n")
            
        elif command == 2:
            cls()
            posts = [post[0:30] for post in userInfo["posts"]]
            print([print(i+1,".",j,"\n") for i,j in zip(range(len(posts)),posts)])
            print("\n\n")

        elif command == 3:
            cls()
            print(userInfo["autoRep"])
            print("\n\n")
            
        elif command == 4:
            client.listen()
    