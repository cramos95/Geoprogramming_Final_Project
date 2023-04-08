import arcpy
from arcpy import analysis #if I don't import this separately, arcpy.analysis.TabulateIntersection() won't work
import sys

#INITIAL SETUP
#project path will be removed before importing to script tool
projectPath = r'C:\Users\lives\OneDrive\TexasStateGrad\Spring2023\GIS_Python\FinalProject\Data\GEO5419_PopEstimate\GEO5419_PopEstimate.aprx'
arcpy.env.workspace=r'C:\Users\lives\OneDrive\TexasStateGrad\Spring2023\GIS_Python\FinalProject\Data\GEO5419_PopEstimate\GEO5419_PopEstimate.gdb'
arcpy.env.overwriteOutput = True

#path for living atlas layer
dataPath = r'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_2020_Redistricting_Blocks/FeatureServer'


##---------------------------------------------------------------------------------------------------
#CREATE FUNCTION TO ADD MESSAGES THROUGHOUT SCRIPT, taken from arcpy documentation
def AddMsgAndPrint(msg, severity=0):
    # Adds a Message (in case this is run as a tool)
    # and also prints the message to the screen (standard output)
    print(msg)

    # Split the message on \n first, so that if it's multiple lines,
    # a GPMessage will be added for each line
    try:
        for string in msg.split('\n'):
            # Add appropriate geoprocessing message
            if severity == 0:
                arcpy.AddMessage(string)
            elif severity == 1:
                arcpy.AddWarning(string)
            elif severity == 2:
                arcpy.AddError(string)
    except:
        pass


##---------------------------------------------------------------------------------------------------
##USER INPUT STUDY AREA
#inArea1=arcpy.GetParameterAsText(0) #required
#inAreaDissField=arcpy.GetParameterAsText(1) #optional


##---------------------------------------------------------------------------------------------------
##ERROR CHECKS AND MESSAGES ON USER INPUT STUDY AREA

##check input for type polygon-stolen from arcpy documentation
# inArea1Desc=arcpy.Describe(inArea1)
# if inArea1Desc.shapeType != "Polygon" :
#     AddMsgAndPrint("Input Study Area must be of type polygon.", 2)
#     sys.exit()

##check input study area for >1 features, if so, require dissolve field
# if arcpy.management.GetCount(inArea1) > 1:
#     if inAreaDissField == "":
#         AddMsgAndPrint("Input Study Area has more than 1 feature, dissolve field required.", 2)
#         sys.exit()

##Only one dissolve field-also stolen from documentation
#if inAreaDissField != "":
#     if inAreaDissField.find(";") > -1 or inAreaDissField.find(";") > -1:
#         AddMsgAndPrint("A maximum of one dissolve field is allowed.", 2)
#         sys.exit()


##---------------------------------------------------------------------------------------------------
##If user input dissolve field, dissolve with field, else dissolve all, wrap in try/except with messages
##Either way, set output equal to inAreaFinal variable
# if inAreaDissField != "":
#     try:
#         inAreaFinal=arcpy.management.Dissolve(inArea1, inAreaFinal.shp, inAreaDissField)
#     except:
#         AddMsgAndPrint("Dissolve Failed.", 2)
#         sys.exit()
# elif inAreaDissField == "":
#     try:
#         inAreaFinal = arcpy.management.Dissolve(inArea1, inAreaFinal.shp)
#     except:
#         AddMsgAndPrint("Dissolve Failed.", 2)
#         sys.exit()
#

#for testing
inAreaFinal=r'C:\Users\lives\OneDrive\TexasStateGrad\Spring2023\GIS_Python\FinalProject\Data\GEO5419_PopEstimate\Shapefiles\Kyle\Jurisdiction.shp'
inAreaDissField=""
popLyr1=""

#NEED TO WRAP BOTH POPULATION, USER SUBMITTED AND NON, IN IF/ELSE TO MOVE TO DEFAULT IF USER DOES NOT ADD DATA
##---------------------------------------------------------------------------------------------------
##USER PROVIDES POPULATION DATA

# #popLyr1=arcpy.GetParameterAsText(2) #optional
# #popLyrField=arcpy.GetParameterAsText(3) #optional

# ##ERROR CHECKS AND MESSAGES ON USER INPUT POPULATION DATA
# #check for shape=polygon
# if popLyr1 != "":
#     popLyrDesc = arcpy.Describe(popLyr1)
#     if popLyr1Desc.shapeType != "Polygon" :
#     AddMsgAndPrint("User submitted population data must be of type polygon.", 2)
#     sys.exit()

# #check for input population field
# if popLyr1 != "" and popLyrField == "":
#     AddMsgAndPrint("If user submits population data, population field must be provided.", 2)
#     sys.exit()

# #check input population field for validity, null values, and non-integer values
# try:
#     with arcpy.da.SearchCursor(popLyr1,popLyrField) as cur1:
#         for row in cur1:
#             if isinstance(row[0], int) != True:
#                 AddMsgAndPrint("Population field contains null or non-integer values.", 2)
#                 sys.exit()
# except:
#     AddMsgAndPrint("Population field is not a valid field", 2)
#     AddMsgAndPrint(arcpy.Getmessages(),0)
#     sys.exit()

#set input variable to popLyrFinal
#popLyrFinal=popLyr1


##---------------------------------------------------------------------------------------------------
#USER DOES NOT PROVIDE POPULATION DATA, DEFAULT TO LIVING ATLAS LAYER


#Will need to use mapObject.addDataFromPath() to add living atlas layer
#Therfore, must first create a project object, preferably with "CURRENT"
#create arcPro Project object with "CURRENT", should work inside a toolbox script tool
#aprx=arcpy.mp.ArcGISProject("CURRENT") #after testing, this should work inside tool
aprx=arcpy.mp.ArcGISProject(projectPath) #need to have map project closed and then save at end of script for this to work during testing

#Set map object to variable, preferably with activeMap method
#m=aprx.activeMap #after testing, this should work inside tool
m=aprx.listMaps()[0]

#add the living atlas layer from path, with method on map object
m.addDataFromPath(dataPath) #works up to this point

#get newly added layer as popLyrFinal variable
#Note, the layer imports as a group layer, and the sublayer needed is called 'Blocks', which is
#is pretty generic and it seems inconsistent, somtimes called 'USA_BLOCK_GROUPS//Blocks, therefore, will get the layer into a variable by counting the number of features
#for every layer in the map, if is feature layer and if count==8174955, its the layer we want. tested in arcPro
for maplayer in m.listLayers():
    if maplayer.isFeatureLayer:
        if str(arcpy.management.GetCount(maplayer))=='8174955':
            popLyrFinal=maplayer #set popLyrFinal equal to blocks layer



##---------------------------------------------------------------------------------------------------
#USING popLyrFinal FROM EITHER USER INPUT OR LIVING ATLAS, SELECT BY LOCATION

#at this point, the following variables will be set
#inAreaFinal #the user submitted study area
#popLyrFinal #eithe the user submitted or default population layer
#inAreaDissField #may be blank if not user-submitted

#Extract population data intersecting input polygons to cut down on runtime, living atlas layer has 8 million features
arcpy.management.SelectLayerByLocation(popLyrFinal,'',inAreaFinal) #setting this equal to a new variable does not work, I think I would need to copyFeatuers and set that to a new variable

print(arcpy.management.GetCount(popLyrFinal))

##---------------------------------------------------------------------------------------------------
##PASS SELECTED POPULATION FEATURES AND DISSOLVED INPUT POLYGONS INTO TABULATE INTERSECTIONS TOOL
##Use Input polygons as zone layer, dissolve field or object id as zone fields, pop layer as class layer
##pop layer oid as class field, and pop total or population field as sum field

#explicit variable setup
in_zone_features=inAreaFinal

#for zone fields, either dissolve field or OID, need to get OID with oid_fieldname = arcpy.Describe(fc).OIDFieldName
if inAreaDissField == "": #i.e., no dissolve field, get oid field name
    zone_fields=arcpy.Describe(in_zone_features).OIDFieldName
else:
    zone_fields=inAreaDissField

#class features are the population polygons
in_class_features=popLyrFinal

#class fields are the objectIDs of the population polygons
class_fields=arcpy.Describe(in_class_features).OIDFieldName

#sum fields are the field containing the population data,
if popLyr1 == "": #if no user submitted population data
    sum_fields='P0010001'
else: #user submitted population data
    sum_fields=popLyrField

#out_table=arcpy.GetParameterAsText(4) #after testing
out_table=r'C:\Users\lives\OneDrive\TexasStateGrad\Spring2023\GIS_Python\FinalProject\Data\GEO5419_PopEstimate\GEO5419_PopEstimate.gdb\tabtable'
arcpy.analysis.TabulateIntersection(in_zone_features, zone_fields, in_class_features, out_table , class_fields, sum_fields)


##---------------------------------------------------------------------------------------------------
#PASS TABULATE FEATURES TABLE INTO Statistics to do a sum and group by input area.

#use this to make sure path to input is correct
ttdesc=arcpy.Describe(out_table)
ttpath=ttdesc.catalogPath

#finalOutput=arcpy.GetParameterAsText(5) #after testing
finalOutput=r'C:\Users\lives\OneDrive\TexasStateGrad\Spring2023\GIS_Python\FinalProject\Data\GEO5419_PopEstimate\GEO5419_PopEstimate.gdb\finalOutput'

#run analysis
#arcpy.analysis.Statistics(ttpath, finalOutput, [[sum_fields,"SUM"],["AREA","SUM"],["PERCENTAGE","SUM"]],zone_fields)
arcpy.analysis.Statistics(ttpath, finalOutput, [[sum_fields,"SUM"]],zone_fields)

##---------------------------------------------------------------------------------------------------
##OUTPUT STATS TABLE AS FINAL OUTPUT, need to clean up fields, change POO10001 to popTotal, remove extras etc.

#drop 'FREQUENCY' FIELD
arcpy.management.DeleteField(finalOutput,['FREQUENCY'])

#change field beginning with 'SUM_' to popTotal
#get SUM_field to variable, will be different depending on user submitted or default population data, but will always start with 'SUM_'
fields=arcpy.ListFields(finalOutput)
for field in fields:
    if field.name.startswith('SUM_'):
        alterField=field.name

arcpy.management.AlterField(finalOutput, alterField, 'popTotal')








#STILL NEED TO DO

#change SUM_P0010001 to PopTotal
#drop fields FREQUENCY, and maybe sum_area, sum_percentage
#change zone fields name (2nd field in output table, can reference by index?) to (post dissolve) StudyArea_OID, or
#dissolve field if user submitted dissolve field
#join by zone_field OID/diss field name to dissolve shp?
#and maybe add functionality for multiple study areas. Merge incoming polygon layers, keep OID only
#to account for different schemas?

#2020 Census Kyle:45,697
#Our Estimate: 46,204
#%diff=1.109%
#Select All intersecting blocks: 54,942
#%diff=20.23%
#Select All blocks completely within: 36,604
#%diff=24.84%

aprx.save()