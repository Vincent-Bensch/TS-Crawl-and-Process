import time
import threading
import requests

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
errorstrings = ["<h3>please try again in a minute</h3>","<p>Our search machines are under too much load to handle your request right now","<h2>Our CDN was unable to reach our servers</h2>"]

abslowtil = 1230000000
abslowonion = 1220000000
abshigh = 1483000000
MaxThreads = 500
Found = 0
Error = 0

class CrawlThread (threading.Thread):
    def __init__(self, threadID, url, outfile):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.url = url
        self.outfile = outfile
    def run(self):
        global RemainingThreads
        global RunningThreads
        global CompletedThreads
        
        RunningThreads = RunningThreads + 1
        ReturnedTitles=crawl_search(get_page(self.url))
        if len(ReturnedTitles) is not 0:
            ResultFileStream=open(self.outfile, "a")
            for Title in ReturnedTitles:
                ResultFileStream.write(Title)
            ResultFileStream.close()
        RunningThreads = RunningThreads - 1
        CompletedThreads = CompletedThreads + 1
        RemainingThreads = RemainingThreads - 1

class CheckThread (threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        
    def run(self):
        time.sleep(1)        
        while(RunningThreads > 0):
            time.sleep(1)
            print (str(RemainingThreads) + "/" + str(RunningThreads) + "/" + str(CompletedThreads) + "-" + str(Found) + "/" + str(Error)) 
        print ("Run Completed")

class SubReddit:
    Name = ""
    OutputFile = ""
    LowLimit = 0
    HighLimit = 0
    JumpSize = 0

def get_page(url):
    try:
        response = requests.get(url, headers=headers)
        page = str(response.content)
    except:
        return get_page(url)
    
    if "<p>use the following search parameters to narrow your results:</p>" in page:
        return page

    for errorstring in errorstrings:
        if errorstring in page:
            time.sleep(5)
            return get_page(url)
    error("Unknown Error",url)
    wtf = open(str(M)+".txt", "a")
    wtf.write(page)
    wtf.close()
    return ""
        
def error(message,url="Q"):
    global Error
    Error = Error + 1
    logfile = open("log.txt", "a")
    logfile.write(message+"\n")
    logfile.close()

    if url is not "Q":
        skipfile = open("skipped.txt", "a")
        skipfile.write(url+"\n")
        skipfile.close()

def crawl_search(page):
    global Found
    global Error
    Titles = []
    ResultStart = 0
    deliniate = " $&@&$ "
    pattern = '%Y-%m-%dT%H:%M:%S'
    while True:
        ResultStart = page.find('<header class="search-result-header"><a href=',ResultStart + 1)
        if ResultStart is -1:
            if len(Titles)>=25:
                error("Too many responses per page")
            return Titles

        TitleStart = page.find('>',ResultStart + 45) + 1
        TitleEnd = page.find('<',TitleStart)
        Title = page[TitleStart:TitleEnd]

        TimeStart = page.find('datetime="',ResultStart) + 10
        TimeEnd = page.find('"',TimeStart)
        Time = page[TimeStart:TimeEnd-6]
        Epoch = str(int(time.mktime(time.strptime(Time, pattern))))
        
        LinkStart = ResultStart + 46
        LinkEnd = page.find('"',LinkStart)
        Link = page[LinkStart:LinkEnd]

        Found = Found + 1
        Titles.append(Title + deliniate + Epoch + deliniate + Link + "\n")

def crawl_subs(SubReddits):
    global RemainingThreads
    global RunningThreads
    global CompletedThreads
    RemainingThreads = 0
    RunningThreads = 0
    CompletedThreads = 0
    i = 0
    
    threads = [CheckThread(0)]
    threadpreps = []
    
    print ("Making URLs")
    for SubReddit in SubReddits:
        for LocalLowLimit in range(SubReddit.LowLimit,SubReddit.HighLimit,SubReddit.JumpSize):
            LocalHighLimit = LocalLowLimit + SubReddit.JumpSize
            threadpreps.append(["http://reddit.com/r/" + SubReddit.Name + "/search?sort=new&q=timestamp%3A" + str(LocalLowLimit) + ".." + str(LocalHighLimit) + "&restrict_sr=on&syntax=cloudsearch", SubReddit.OutputFile])
    
    print ("Making Threads")
    
    for threadprep in threadpreps:
        i = i + 1
        threads.append(CrawlThread(i,threadprep[0],threadprep[1]))
        RemainingThreads = RemainingThreads + 1
    print ("Starting Threads")
    
    for thread in threads:
        while(RunningThreads>MaxThreads-1):
            time.sleep(0.01)
        thread.start()
    print ("Main Thread Exited")


TIL = SubReddit()
TIL.Name = "TodayILearned"
TIL.LowLimit = abslowtil
TIL.HighLimit = abshigh
TIL.JumpSize = 1000
TIL.OutputFile = "Output-G1-TIL-2016-12-24 Take-2.txt"

NTO = SubReddit()
NTO.Name = "NotTheOnion"
NTO.LowLimit = abslowonion
NTO.HighLimit = abshigh
NTO.JumpSize = 1000
NTO.OutputFile = "Output-G1-NTO-2016-12-24 Take-2.txt"


#print (crawl_search(get_page("https://www.reddit.com/r/todayilearned/search?sort=new&q=timestamp%3A1482205106..1482215106&restrict_sr=on&syntax=cloudsearch")))
#crawl_subs([TIL,NTO])
