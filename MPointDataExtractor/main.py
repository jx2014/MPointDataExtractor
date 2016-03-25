import DataExtractor as DE
import MpointHTMLExtractor as HE

#dataDir = r"C:\Users\jxue\Documents\Projects_LocalDrive\Bridge2.0\"
#BLTData = "MPoint_data1.txt"

#datafile = r"C:\TEMP\mpoint test\Test Results for 0013500700000861.html"
#datafile = r"C:\Users\jxue\Documents\Projects_LocalDrive\Gen5_Qualification\data\00086F\mpoint\Test Results for 001350070000086F.html"
#datafile = r"C:\Users\jxue\Documents\Projects_LocalDrive\Gen5_Qualification\data\000861\mpoint\Test Results for 0013500700000861.html"
datafile = r'C:\Users\jxue\Documents\Projects_LocalDrive\Gen5_Qualification\data\000880\mpoint\Test Results for 0013500700000880_Prion_100-to--10.html'

MpointData = 0 # basic .txt data
MpointHTML = 1 # get mpoint data from html page with complete tests

if MpointData == 1:
    BLT = DE.MPointDataExtractor(datafile)
    BLT.LineProcess()
    
    for i in BLT.listOfMacNMsg:
        print i
    
    BLT.WriteCSV()

elif MpointHTML == 1:
    BLT = HE.MPointHtmlExtractor(datafile)
    for td, tb in BLT.GetTable():

        BLT.GetData(td, tb)
