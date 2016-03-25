'''
    Mpoint HTML Extractor
    Directly parser saved HTML version of Mpoint page
    
    Started: 2/28/2016
    Last update: 3/12/2016
'''
import sys
import os
from collections import OrderedDict
from bs4 import BeautifulSoup
import csv
import re


class MPointHtmlExtractor():
    
    def __init__(self, abspath):
        self.dir = os.path.dirname(abspath)
        self.file = os.path.basename(abspath)
        self.output_file, _ = os.path.splitext(self.file) # 'inputfile.txt -> inputfile .txt, wihch .txt is disgarded'
        self.output_file = self.output_file + '_output' # inputfile -> 'inputfile_output'
        self.output_file = '.'.join([self.output_file,'csv']) # 'inputfile_output' -> 'inputfile_output.csv' 
        self.output_full_path = os.path.join(self.dir, self.output_file)   # 'inputfile_output.csv' to 'c:\blah_foler\inputfile_output.csv'
        
        self.soup = BeautifulSoup(open(abspath))
        
        # list of test IDs that we care about, cal tables will be handled some other ways
#         self.listOftestID = {'7033':'Begin test run',
#                        '7806':'Manual scan',
#                        '7127':'Test application software version',
#                        '7147':'Test station',
#                        '7148':'Fixture',
#                        '7149':'Test site',                        
#                        '7055':'Voltage measurement (Vin)',
#                        '7052':'Voltage measurement (Vout 1)',
#                        '7053':'Voltage measurement (Vout 2)',
#                        '7054':'Voltage measurement (Vout 3)',
#                        '7163':'Voltage measurement (Vout 4)',
#                        '7037':'Verify firmware',
#                        '7041':'Transmit Test - Measured output power',
#                        '7042':'Transmit Test - Measured frequency error',
#                        '7020':'Receive Test - Packet success rate',
#                        '7146':'Test duration', 
#                        '7034':'End test run',
#                        }
        
        self.testIDs = {'7806': self.id_7806, # get scann data: mac ID and p/n
                        '7127': self.id_7127, # test software i.e.NicBlt v2.02                        
                        '7033': self.id_7033, # time stamp for begin test run 
                        '7149': self.id_7149, # test site
                        '7148': self.id_7148, # test fixture
                        '7037': self.id_7037, # dut firmware
                        '7055': self.GetVoltage, # vin
                        '7052': self.GetVoltage, # vout 1
                        '7053': self.GetVoltage, # vout 2
                        '7054': self.GetVoltage, # vout 3
                        '7163': self.GetVoltage, # vout 4
                        '7041': self.id_7041, # Tx power
                        '7042': self.id_7042, # Tx Frequency error
                        '7020': self.id_7020, # Rx success rate
                        '7146': self.id_7146, # test duration
                        '7034': self.id_7034, # time stamp for end test run
                        }
        
        self.rowlist = ['Line',                        
                        'MAC ID',
                        'msg',
                       'PartNumber',
                       'Begin-Date',
                       'Begin-Time',
                        'End-Date',
                        'End-Time',
                        'Test time(s)',
                        'Test SW',
                        'SilverBox',
                        'Fixture',
                        'Test site',
                        'Firmware1',
                        'Firmware2',
                        'Vin',
                        'Vout 1',
                        'Vout 2',
                        'Vout 3',
                        'Vout 4',
                        'TxPwr 900 Mesh 0',
                        'Freq 900 Mesh 0',
                        'Freq Error 900 Mesh 0',
                        'TxPwr 900 Mesh 41',
                        'Freq 900 Mesh 41',
                        'Freq Error 900 Mesh 41',
                        'TxPwr 900 Mesh 82',
                        'Freq 900 Mesh 82',
                        'Freq Error 900 Mesh 82',
                        'TxPwr 900 Mesh Ext 0',
                        'TxPwr 900 Mesh Ext 82',
                        'Rx rate 900 Mesh 0',
                        'Rx pwr 900 Mesh 0',
                        'Rx rate 900 Mesh 82',
                        'Rx pwr 900 Mesh 82',
                        ]
        
        self.CrateCSV()

    
    def InitRow(self, rowlist):
        self.row = OrderedDict()
        # list of name for the csv rows
        for i in rowlist:
            self.row[i]='-'
        
    def CrateCSV(self):        
        with open(self.output_full_path, 'w') as of:            
            writer = csv.DictWriter(of, fieldnames=self.rowlist, lineterminator='\n')
            writer.writeheader()
    
    def WriteRow(self, row):
        with open(self.output_full_path, 'a') as of:
            writer = csv.DictWriter(of, fieldnames=self.rowlist, lineterminator='\n')            
            writer.writerow(row)
            
    
    def SearchByID(self, testID):
        pass
    
    # get voltage measurement from test ID 7055,7052,7053,7054,7163
    def GetVolt(self, testName, testResult):
        re.findall('(?<=Vout)*\d|Vin', testName)
    
    # decipher result line by line. 
    def GetTestResult(self, testPassFail, testID, testName, testChannel, testResult):
        pass
    
    # manual scan
    def id_7806(self):
        macID = re.search('[0-9a-zA-Z]{16}', self.testResult)
        pn = re.search('174[0-9a-zA-Z]{8}', self.testResult)
        if macID is not None:
            #self.macID = macID.group()
            self.row['MAC ID'] = macID.group()
        if pn is not None:
            #self.pn = pn.group()
            self.row['PartNumber'] = pn.group()
    
    # test software 
    def id_7127(self):
        self.row['Test SW'] = self.testResult
            
    
    # Begin test run
    def id_7033(self):        
        date = self.testResult.split()[0]
        time = ' '.join(self.testResult.split()[1:3])
        #self.dateBegin = date
        #self.timeBegin = time
        self.row['Begin-Date'] = date
        self.row['Begin-Time'] = time   
        #print date, time
    
    # fixture
    def id_7148(self):
        # i.e. FIXSB1005, FIXMF1038 
        silverBox = re.search('\w*SB\d*', self.testResult)
        oneUpFixture = re.search('\w*MF\d*', self.testResult)
        if silverBox is not None:
            self.row['SilverBox'] = silverBox.group()
        if oneUpFixture is not None:
            self.row['Fixture'] = oneUpFixture.group()
            
    def id_7149(self):
        testSite = re.search('[A-D1-9]{2}', self.testResult)
        if testSite is not None:
            #self.testSite = testSite.group()
            self.row['Test site'] = testSite.group()        
    
    # dut firmware
    def id_7037(self):
        fw1, fw2 = self.testResult.split(',')
        self.row['Firmware1'] = fw1.strip()
        self.row['Firmware2'] = fw2.strip()
    
    # test duration
    def id_7146(self):
        self.row['Test time(s)'] = self.testResult.split(',')[0] 
        #print self.duration
    
    # End test run
    def id_7034(self):        
        date = self.testResult.split()[0]
        time = ' '.join(self.testResult.split()[1:3])
        #self.dateEnd = date
        #self.timeEnd = time
        self.row['End-Date'] = date
        self.row['End-Time'] = time  
        #print date, time
    
    # Get voltage based on test ID
    def GetVoltage(self):
        testName = {'7055':'Vin',
                    '7052':'Vout 1',
                    '7053':'Vout 2',
                    '7054':'Vout 3',
                    '7163':'Vout 4'
                    }   
        voltage, _ = self.testResult.split(',')
        self.row[testName[self.testID]] = voltage.strip()
    
    # Get Tx power
    def id_7041(self):
        ch = self.testChannel
        radio = self.testRadio        
        radio = radio.replace('External', 'Ext')        
        pwr_offset,_ = self.testResult.split(',')
        pwr = 30 + float(pwr_offset)
        testName1 = 'TxPwr {0} {1}'.format(radio, ch)
        testName2 = 'TxPwr Offset {0} {1}'.format(radio, ch)
        self.row[testName1] = pwr
        #self.row[testName2] = pwr_offset
    
    # Get Tx freq error
    def id_7042(self):
        ch = self.testChannel
        radio = self.testRadio        
        radio = radio.replace('External', 'Ext')
        freqError, freq = self.testResult.split(',')
        testName1 = 'Freq {0} {1}'.format(radio, ch)
        testName2 = 'Freq Error {0} {1}'.format(radio, ch)
        self.row[testName1] = freq.strip()
        self.row[testName2] = freqError.strip()
    
    # Get Rx package rate
    def id_7020(self):
        ch = self.testChannel
        radio = self.testRadio        
        radio = radio.replace('External', 'Ext')
        rate, sens = self.testResult.split(',')
        testName1 = 'Rx rate {0} {1}'.format(radio, ch)
        testName2 = 'Rx pwr {0:1} {1}'.format(radio, ch)
        self.row[testName1] = rate.strip()
        self.row[testName2] = sens.strip()
    
    
    def GetTable(self):
        td = self.soup.find_all('td', {'class':'arial_med'}) # Test Instance : etc etc blah blah
        tb = self.soup.find_all('table', {'class':'arial_sm_black'}) # 
        self.lineNo = 0
        td = td[1:]
        for i in range(len(tb)):  
        #for i in range(10):
            self.lineNo = i+1            
            yield td[i].contents, tb[i].find_all('tr')
    
    def GetMsg(self, td):
        for i in td:
            #print '-'*100            
            #print i.string
            #print '-'*100
            msg = re.search('(?<=msg: \[)\d{4}', i.string)
            
            if msg is not None:
                #print type(str(msg.group()))
                #remove the 4 from msg i.e. 4137 becomes 137
                self.row['msg'] = str(msg.group()[1:])
    
    def GetData(self, td, trow):
        debug = 0
        self.InitRow(self.rowlist)
        self.row['Line'] = self.lineNo
        
        #td process
        self.GetMsg(td)
        
        #trow process
        for i in range(len(trow)):
            #print trow[i].find_all('td')[0]
            #try:
            if len(trow[i].find_all('td')) < 3:
                continue            
            else:
                self.testID = trow[i].find_all('td')[2].string
                # skip certain tests, such as cal tables, will handle the cal tables some other way
                if self.testID in ['7152', '7023', '7132', '7108', '7109'] or len(trow[i].find_all('td')[2].find_parents('td')) > 1:
                    continue
                else:                    
                    self.testPassFail = trow[i].find_all('td')[0].string
                    self.testName = trow[i].find_all('td')[1].string.strip()
                    self.testRadio = trow[i].find_all('td')[3].string
                    self.testChannel = trow[i].find_all('td')[4].string
                    self.testResult = trow[i].find_all('td')[5].string
                    try:
                        self.testResult = trow[i].find_all('td')[5].find('b').string.strip()
                    except AttributeError as e:
                        #print 'AttributeError', e
                        pass
                    except:
                        print 'Unexpected error:', sys.exc_info()[0]
                        raise 
                    #print i, testID, testChannel, testResult
                    if debug == 1:
                        print '{0:6} {2:6} {1:50} {3:20} {4:8} {5:50}'.format(self.testPassFail,
                                                                       self.testName, 
                                                                       self.testID,
                                                                       self.testRadio,
                                                                       self.testChannel, 
                                                                       self.testResult)
                    #print testID
                    try:
                        self.testIDs[self.testID]()
                        #print testID
                    except KeyError:
                        pass
                        #print 'key error', testID
                    #print '{2:6} {1:50}'.format(testPassFail, testName, testID, testChannel, testResult)

        #print 'End!'
        #print self.dateBegin, self.timeBegin, self.dateEnd, self.timeEnd, self.duration, self.macID, self.pn, self.testSite
        print '---'
        #self.PrintValues()
        self.PrintRow()
        self.WriteRow(self.row)
    
    def PrintValues(self):
        for key, value in self.row.items():
            print '{0:30}: {1}'.format(key, value)
    
    def PrintRow(self):
        for key, _ in self.row.items():
            print '{0:<30}'.format(key),       
        
        print ''
        
        for _, value in self.row.items():
            print '{0:<30}'.format(value),
            
        print '\n'

            
        
            
        
        
        

        
        