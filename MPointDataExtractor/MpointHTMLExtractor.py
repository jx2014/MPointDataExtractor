'''
    Mpoint HTML Extractor
    Directly parser saved HTML version of Mpoint page
    
    2/28/2016
'''
import sys
import os
from collections import OrderedDict
from bs4 import BeautifulSoup
import re


class MPointHtmlExtractor():
    
    def __init__(self, abspath):
        self.dir = os.path.dirname(abspath)
        self.file = os.path.basename(abspath)
        self.output_file, _ = os.path.splitext(self.file) # 'inputfile.txt -> inputfile .txt, wihch .txt is disgarded'
        self.output_file = self.output_file + '_output' # inputfile -> 'inputfile_output'
        self.output_file = '.'.join([self.output_file,'csv']) # 'inputfile_output' -> 'inputfile_output.csv' 
        self.output_path = os.path.join(self.dir, self.output_file)   # 'inputfile_output.csv' to 'c:\blah_foler\inputfile_output.csv'
        
        self.soup = BeautifulSoup(open(abspath))
        
        # list of test IDs that we care about, cal tables will be handled some other ways
        self.listOftestID = {'7033':'Begin test run',
                       '7806':'Manual scan',
                       '7127':'Test application software version',
                       '7147':'Test station',
                       '7148':'Fixture',
                       '7149':'Test site',                        
                       '7055':'Voltage measurement (Vin)',
                       '7052':'Voltage measurement (Vout 1)',
                       '7053':'Voltage measurement (Vout 2)',
                       '7054':'Voltage measurement (Vout 3)',
                       '7163':'Voltage measurement (Vout 4)',
                       '7037':'Verify firmware',
                       '7041':'Transmit Test - Measured output power',
                       '7042':'Transmit Test - Measured frequency error',
                       '7020':'Receive Test - Packet success rate',
                       '7146':'Test duration', 
                       '7034':'End test run',
                       }
        
        self.testIDs = {'7806': self.id_7806,
                        '7033': self.id_7033,
                        '7149': self.id_7149,
                        '7146': self.id_7146,
                        '7034': self.id_7034,
                        }
        
        # list of name for the csv rows
        self.row = {'Begin-Date':None,
                    'Begin-Time':None,
                    'End-Date':None,
                    'End-Time':None,
                    'Duration':None,
                    'MAC ID':None,
                    'PartNumber':None,
                    'Fixture':None,
                    'Test site':None,
                    'Firmware':None,
                    'Vin':None,
                    'Vout 1':None,
                    'Vout 2':None,
                    'Vout 3':None,
                    'Vout 4':None,
                    }
    
    def Print2Of(self, stuff):
        with open(self.output_path, 'w') as of:
            of.write(stuff)
    
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
        silverBox = re.search('', self.testResult)
    
    def id_7149(self):
        testSite = re.search('[A-D1-9]{2}', self.testResult)
        if testSite is not None:
            #self.testSite = testSite.group()
            self.row['Test site'] = testSite.group()        
    
    def id_7146(self):
        self.row['Duration'] = self.testResult.split(',')[0] 
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
            
        
    
    def Test(self):
        
#         print '---input file:'
#         print self.dir
#         print self.file + '\n'
#         
#         print '---output file:'
#         print self.output_path
#         print self.output_file
#         
#         print '\n\n'
#         #print self.soup.find("table", {'class':'arial_med'})
#         #print self.soup.find_all("td")

        # one test instance        
        tb = self.soup.find_all('table', {'class':'arial_sm_black'})

        trow = tb[0].find_all('tr')
        
        
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
                    print '{0:6} {2:6} {1:50} {3:8} {4:50}'.format(self.testPassFail, 
                                                                   self.testName, 
                                                                   self.testID, 
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
        self.PrintRow()
    
    def PrintRow(self):
        for key, value in self.row.items():
            print '{0:15}: {1}'.format(key, value)

            
        
            
        
        
        

        
        