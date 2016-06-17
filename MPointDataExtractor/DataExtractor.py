import re
import csv
from datetime import datetime
from collections import OrderedDict
import os



class MPointDataExtractor():
    '''
        Sample Mpoint data
    
        [8] MAC : 001350FFFE082348 NOT FOUND IN THE MASTER DB
        
        MAC : 001350FFFE10125F [174000123-00-6] (dev id:10686719) BIRTH DATE: 2010-11-02 23:13:51 at Plexus
        - Test Instance : 10790613 station: S002|0 time: 2010-11-02 23:13:51 conf: [10071] fw: [2.0.5005] msg: [4100] PASS
        - Test Instance : 26458709 station: S002|0 time: 2015-04-03 08:39:11 conf: [11203] fw: [2.6.5009] msg: [4116] 900 MHz SSN [channel 82]: Tx power error -3.13 is NOT within acceptable bounds [-3.00 2.00]. Power (measured -2.36 dBm + loss 29.23 dBm) = 26.87 dBm.
        - Test Instance : 26470751 station: S002|0 time: 2015-04-07 08:14:10 conf: [11203] fw: [2.6.5009] msg: [4116] 900 MHz SSN [channel 82]: Tx power error -3.12 is NOT within acceptable bounds [-3.00 2.00]. Power (measured -2.35 dBm + loss 29.23 dBm) = 26.88 dBm.
        - Test Instance : 26490309 station: S002|0 time: 2015-04-10 10:47:40 conf: [11203] fw: [2.6.5009] msg: [4101] Cannot read from UUT0; sent ate1 but received no response
        
        MAC : 001350FFFE100F3F [174000123-00-6] (dev id:10686239) BIRTH DATE: 2010-11-02 20:24:11 at Plexus
        - Test Instance : 10789985 station: S002|2 time: 2010-11-02 20:24:11 conf: [10071] fw: [2.0.5005] msg: [4116] 900 MHz SSN, channel 0 TX power error (2.04525069376) is not within acceptable bounds [-3, 2] (-25.96474930624dBm + loss (58.01) = 32.04525069376dBm)
        - Test Instance : 10792117 station: S002|0 time: 2010-11-03 05:27:43 conf: [10071] fw: [2.0.5005] msg: [4100] PASS
        - Test Instance : 26460611 station: S002|0 time: 2015-04-03 21:02:01 conf: [10147] fw: [2.0.5005] msg: [4102] Unexpected response from UUT0; expected: OK in response to ath=14 got: ERROR
        - Test Instance : 26490389 station: S002|0 time: 2015-04-10 10:51:51 conf: [11203] fw: [2.6.5009] msg: [4100] PASS
        
        MAC : 001350FFFE106007 [174000123-00-7] (dev id:12001151) BIRTH DATE: 2011-10-03 09:47:06 at Plexus
        - Test Instance : 12354897 station: S002|0 time: 2011-10-03 10:46:36 conf: [10229] fw: [2.0.5005] msg: [4100] PASS
        - Test Instance : 12354987 station: S002|2 time: 2011-10-03 12:39:57 conf: [0] fw: [?.?.?] msg: [4005] Scan Failed: User Invalidated MAC
        - Test Instance : 26490271 station: S002|0 time: 2015-04-10 10:43:52 conf: [11203] fw: [2.6.5009] msg: [4178] Tx Calibration Failed: FAIL_UNABLE_TO_REACH_MAXIMUM_POWER
        - Test Instance : 26511909 station: S002|0 time: 2015-04-13 14:37:04 conf: [11203] fw: [2.6.5009] msg: [4178] Tx Calibration Failed: FAIL_UNABLE_TO_REACH_MAXIMUM_POWER

    '''
    def __init__(self, abspath):
        self.dir = os.path.dirname(abspath)
        self.file = os.path.basename(abspath)
        self.output_file, _ = os.path.splitext(self.file) # 'inputfile.txt -> inputfile .txt, wihch .txt is disgarded'
        self.output_file = self.output_file + '_output' # inputfile -> 'inputfile_output'
        self.output_file = '.'.join([self.output_file,'csv']) # 'inputfile_output' -> 'inputfile_output.csv' 
        self.output_path = os.path.join(self.dir, self.output_file)   # 'inputfile_output.csv' to 'c:\blah_foler\inputfile_output.csv'
    
    def GetMac(self, line):
        pattern = r"[0-9A-F]{16}" # i.e. 001350FFFE109263
        found = re.search(pattern, line)
        if found:
            return found.group(0)
    
    def GetBoardRev(self, line):
        pattern = r"(?<=([0-9]|[A-F]){16} \[).*(?=\])" # i.e. 001350FFFE082384 [174000123-00-B] 
        found = re.search(pattern, line)
        if found:
            return found.group(0)
    
    def GetBDay(self, line):
        pattern = r"(?<=BIRTH DATE\:\s)20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]" # i.e. BIRTH DATE: 2011-07-14
        found = re.search(pattern, line)
        if found:
            return found.group(0)
    
    def GetBDayLoc(self, line):
        pattern = r"(?<=at ).*$" # i.e. at Plexus
        found = re.search(pattern, line)
        if found:
            return found.group(0)
    
    def GetStation(self, line):
        pattern = r"(?<=station: ).*(?=\|)" # i.e. station: S002|
        found = re.search(pattern, line)
        if found:
            return found.group(0)
            
        #TODO: need to get date
    def GetTestDate(self, line): #Get date stamp from Test Instance (Birth Date will not count)
        pattern = r"time\: (?P<Y>20[0-9][0-9])-(?P<M>[0-1][0-9])-(?P<D>[0-3][0-9])\s(?P<HH>[0-2][0-9]):(?P<MM>[0-5][0-9]):(?P<SS>[0-5][0-9])"
        found = re.search(pattern, line)
        #print "Did I find anything: ", found
        if found:
            return found.group("Y"), found.group("M"), found.group("D"), found.group("HH"), found.group("MM"), found.group("SS")
                
    def GetTMsg(self, line): #Get all the msg from the whole file
        pattern = r"(?<=msg\: \[)\d{4}(?=\])" # i.e. msg: [4100] msg: [4178]
        found = re.search(pattern, line)
        if found:
            return found.group(0)
        
    def GetFW(self, line): #Get fw from the file
        pattern = r"(?<=fw\: \[)([\d|\?]\.?)*(?=\])" #i.e. 2.0.5005 or ?.?.?
        found = re.search(pattern, line)
        if found:
            return found.group(0)
    
    def GetUniqueMsgs(self):
        self.totalMsgs = []
        self.uniqueMsgs = set()
        with open('\\'.join([self.dir,self.file])) as data:
            for line in data.readlines():
                msg = self.GetTMsg(line)
                if msg is not None:
                    self.totalMsgs.append(msg)
        self.uniqueMsgs = set(self.totalMsgs)
        return self.uniqueMsgs

    def GetAllMacs(self):
        self.allMacs = []
        with open('\\'.join([self.dir,self.file])) as data:
            for line in data.readlines():
                mac = self.GetMac(line)
                if mac is not None:
                    self.allMacs.append(mac)
                    
    def GetFirstBLTDate(self):
        self.allMacs = []
        with open('\\'.join([self.dir,self.file])) as data:
            for line in data.readlines():
                mac = self.GetMac(line)
                if mac is not None:
                    self.allMacs.append(mac)
    
    def GetDeltaDaytime(self, year0, month0, day0, hour0, minute0, second0, year1, month1, day1, hour1, minute1, second1):
        d0 = datetime(int(year0), int(month0), int(day0), int(hour0), int(minute0), int(second0))
        d1 = datetime(int(year1), int(month1), int(day1), int(hour1), int(minute1), int(second1))
        delta = d1 - d0
        return delta.days
        
            
    def LineProcess(self): #this func populates macNmsg
        self.GetUniqueMsgs() # get msg IDs from the whole mpoint data sheet, no duplication.
        
        self.macNmsg = []
        #self.macNmsg = OrderedDict()
        #self.macNmsg.append(OrderedDict({ } ))
        #self.macNmsg['MACs'] = list(self.uniqueMsgs)
                
        with open('\\'.join([self.dir,self.file])) as data:
            self.listOfMacNMsg = []
            
            year0, month0, day0, hour0, minute0, second0 = 0, 0, 0, 0, 0, 0   
            
            for line in data.readlines(): # read line by line.
                bday = self.GetBDay(line)
                bdayloc = self.GetBDayLoc(line)
                board = self.GetBoardRev(line)
                msg = self.GetTMsg(line)
                date = self.GetTestDate(line)
                mac = self.GetMac(line)
                
                if mac is not None:
                    if len(self.macNmsg) > 0: # make sure there are content of macNmsg
                        self.listOfMacNMsg.append(self.macNmsg) # a new Mac is found, append the previous mac dictionary to the list
                    self.currentMac = mac
                    self.macNmsg = {'MAC':self.currentMac}
                                       
                    #initialize msg codes to 0 when mac is found.
                    for i in self.uniqueMsgs:
                        self.macNmsg[i] = 0
                        
                    #initialize first BLT and last BLT date when mac is found.
                    self.macNmsg['Birthday'] = 'None'
                    self.macNmsg['Birth Place'] = 'None'
                    self.macNmsg['Board#'] = 'None'
                    self.macNmsg['FirstBLTdate'] = 'None'
                    self.macNmsg['LastBLTdate'] = 'None'
                    self.macNmsg['No.ofBLT'] = 0
                    self.macNmsg['Delta Day(s)'] = 'None'
                
                if bday is not None:
                    self.macNmsg['Birthday'] = bday
                
                if bdayloc is not None:
                    self.macNmsg['Birth Place'] = bdayloc
                                    
                if board is not None:
                    self.macNmsg['Board#'] = board
                    
                if msg is not None:
                    self.macNmsg[msg] += 1
                                           
                if date is not None:
                    #date[0] year, date[1] month, date[2] day, date[3] hour, date[4] minute, date[5] second
                    bltDate = '-'.join([date[0], date[1], date[2]]) + ' ' + ':'.join([date[3], date[4], date[5]])
                    if self.macNmsg['FirstBLTdate'] == 'None':
                        self.macNmsg['FirstBLTdate'] = bltDate
                        year0, month0, day0, hour0, minute0, second0 = date[0], date[1], date[2], date[3], date[4], date[5]
                    self.macNmsg['LastBLTdate'] = bltDate
                    self.macNmsg['No.ofBLT'] += 1
                    self.macNmsg['Delta Day(s)'] = self.GetDeltaDaytime(year0 = year0, 
                                                                    month0 = month0, 
                                                                    day0 = day0,
                                                                    hour0 = hour0,
                                                                    minute0 = minute0,
                                                                    second0 = second0,
                                                                    year1 = date[0], 
                                                                    month1 = date[1], 
                                                                    day1 = date[2],
                                                                    hour1 = date[3],
                                                                    minute1 = date[4],
                                                                    second1 = date[5],)                    
            
            #at the end of loop, append the last mac to the list
            self.listOfMacNMsg.append(self.macNmsg)
            

    def WriteCSV(self):        
        with open(self.output_path, 'w') as csvOut:
            fieldnames = ['MAC', 'Birthday', 'Birth Place', 'Board#'] + list(self.uniqueMsgs) + ['FirstBLTdate', 'LastBLTdate', 'No.ofBLT', 'Delta Day(s)']
            writter = csv.DictWriter(csvOut, fieldnames = fieldnames, lineterminator='\n')
            writter.writeheader()
            writter.writerows(self.listOfMacNMsg)
        