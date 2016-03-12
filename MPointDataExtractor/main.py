import DataExtractor as DE
import MpointHTMLExtractor as HE

#dataDir = r"C:\Users\jxue\Documents\Projects_LocalDrive\Bridge2.0\"
#BLTData = "MPoint_data1.txt"

datafile = r"C:\Users\jxue\Documents\Projects_LocalDrive\Bridge2.0\mPoint.txt"
htmlfile = r"C:\Users\jxue\Documents\Projects_LocalDrive\Gen5_Qualification\Test Results for 0013500700000880.html"

MpointData = 0 # basic .txt data
MpointHTML = 1 # get mpoint data from html page with complete tests

if MpointData == 1:
    BLT = DE.MPointDataExtractor(datafile)
    BLT.LineProcess()
    
    for i in BLT.listOfMacNMsg:
        print i
    
    BLT.WriteCSV()

elif MpointHTML == 1:
    BLT = HE.MPointHtmlExtractor(htmlfile)
    for i in BLT.GetTable():
        BLT.GetData(i)
