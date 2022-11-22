import os, requests, time
os.chdir("C:\\Users\\asraf\\OneDrive\\programming\\Python\\Practice")

url = "https://raw.githubusercontent.com/TheP-Bot/pBot/main/version.info"

currentVersion = "v1.0.0"

newVersion = requests.get(url).text


if newVersion != currentVersion:
   print("Update Found!!")
   os.remove("test2.py")
   code = requests.get("").text
   file = open("test2.py", "w")
   file.write(code)
   file.close()

   