import os
import urequests as requests
from temp.stats import stats
import time


def update(server, file):
    URL = server + file
    resp = requests.get(URL).text
    with open(file, "w") as file:
        file.write(resp)
        print("Suceed") 

def date_and_time_string(t = time.localtime(), title_date="", title_time="", sep_date_n_time="", sep_date="", sep_time=""):
    tm = ""
    print(str(t))
    for i in t[:6]:
        if len(str(i)) == 1:
            se = "0" + str(i)
        else:
            se = str(i)
        tm += se
    date_and_time_string = title_date + sep_date + tm[:4] + sep_date + tm[4:6] + tm[6:8] + sep_date_n_time + \
                           title_time + tm[8:10] + sep_time + tm[10:12] + sep_time + tm[12:14]
    return date_and_time_string



def get_mod_info_on(server,file):
    URL = server + file
    try:
        r = requests.head(URL)
        url_time = r.headers['Last-Modified']
    except:
        url_time = "Thu, 01 Jan 1970 00:00:00 GMT"
    return url_time



def parse_requested_time(url_time):
    ulist = url_time.split(",")[1].strip().split(" ")
    yyyy = ulist[2]
    dd = "0" + str(ulist[0]) if len(ulist[0]) == 1 else str(ulist[0])
    m = 1+["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(ulist[1])
    mm = str(m) if m > 9 else "0" + str(m)
    hhmmss = ""
    for t in ulist[3].split(":"):
        tt = "0" + t if len(t) == 1 else t
        hhmmss = hhmmss + tt
    timeobj = time.mktime((int(yyyy), m, int(dd), int(hhmmss[:2]),  int(hhmmss[2:4]), int(hhmmss[4:]), 0, 0))
    timeobj = timeobj + (3600 * 13)
    thistime = time.localtime(timeobj)
    # print(thistime)
    print("\r.", end="", sep="")
    return timeobj, thistime

def is_not_folder(fileInfo):
    return fileInfo[1] == 32768
    
 
if __name__ == "__main__":
    # wlan = lan_connect(ssid="SPARK-FDMF9F", psd="LUU2W5DSME")
    server = "http://192.168.1.75:8000/"
    for ft in os.ilistdir():
        if is_not_folder(ft):
            f = ft[0]
            try:
                url_time = get_mod_info_on(server, f)
            except:
                url_time = "Thu, 01 Jan 1970 00:00:00 GMT"
            objtime, _ = parse_requested_time(url_time)
            stat = stats(f)
            sta = [stat.file, str(stat.dt_ctime), str(stat.dt_mtime), str(stat.dt_atime)]
            # print("Localfile: " + str(sta) + "\n")
            [my,mm,md] = sta[2].split(" ")[0].split("-")
            [mh,mmin,ms] = sta[2].split(" ")[1].split(":")
            dttp = (int(my),int(mm),int(md),int(mh),int(mmin),int(ms),0,0)
            localmtime = time.mktime(dttp)
            # print(f, " : ", objtime, localmtime)
            if objtime > localmtime:
                print("Updated", f)
                update(server, f)
            else:
                # print(f, "not update")
                pass
  