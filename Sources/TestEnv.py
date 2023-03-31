import arcpy
import sys

#project path will be removed before importing to script tool
projectPath = r'C:\Users\lives\OneDrive\TexasStateGrad\Spring2023\GIS_Python\FinalProject\Data\GEO5419_PopEstimate\GEO5419_PopEstimate.aprx'

#path for living atlas layer
dataPath = r'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_2020_Redistricting_Blocks/FeatureServer'


#############################################################
#CREATE FUNCTION TO ADD MESSAGES THROUGHOUT SCRIPT
#shamelessly stolen from arcpy documentation

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





#############################################################
##USER INPUT STUDY AREA
#inArea1=arcpy.GetParameterAsText(0) #required
#inAreaDissField=arcpy.GetParameterAsText(1) #optional

##ERROR CHECKS AND MESSAGES ON USER INPUT STUDY AREA

##check input for type polygon-stolen from arcpy documentation
# inArea1Desc=arcpy.Describe(inArea1)
# if inArea1Desc.shapeType != "Polygon" :
#     AddMsgAndPrint("Input Study Area must be of type polygon.", 2)
#     sys.exit()
#
##check input study area for >1 features, if so, require dissolve field
# if arcpy.management.GetCount(inArea1) > 1:
#     if inAreaDissField == "":
#         AddMsgAndPrint("Input Study Area has more than 1 feature, dissolve field required.", 2)
#         sys.exit()
#
##Only one dissolve field-also stolen from documentation
#if inAreaDissField != "":
#     if inAreaDissField.find(";") > -1 or inAreaDissField.find(";") > -1:
#         AddMsgAndPrint("A maximum of one dissolve field is allowed.", 2)
#         sys.exit()
#
#NEED TO DISSOLVE ALL FEATURES HERE, CAN ADD FUNCTIONALITY WITH ANOTHER GET USER INPUT
#IF USER INPUTS MULTIPLE POLYGONS, i.e. MULTIPLE CITY LIMITS OR RINGS FROM A MULTIRING BUFFER
#ASK USER FOR DISSOLVE FIELD (NAME, FID, ETC). IF NOT, DISSOLVE GENERIC WITH NO DISSOLVE FIELD
#TO HANDLE MULTIPART INPUT FEATURES
#
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



#############################################################
##USER PROVIDES POPULATION DATA

# #popLyr1=arcpy.GetParameterAsText(2) #optional
# #popLyrField=arcpy.GetParameterAsText(3) #optional
#
# ##ERROR CHECKS AND MESSAGES ON USER INPUT POPULATION DATA
# #check for shape=polygon
# if popLyr1 != "":
#     popLyrDesc = arcpy.Describe(popLyr1)
#     if popLyr1Desc.shapeType != "Polygon" :
#     AddMsgAndPrint("User submitted population data must be of type polygon.", 2)
#     sys.exit()
#
# #check for input population field
# if popLyr1 != "" and popLyrField == "":
#     AddMsgAndPrint("If user submits population data, population field must be provided.", 2)
#     sys.exit()
#
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
#
#
# #maybe more checks here, valid geometry etc.



#popLyrFinal=popLyr1



#############################################################
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
#is pretty generic, therefore, will get the layer into a variable by counting the number of features
#for every layer in the map, if count==8174955, its the layer we want-tested in arcPro
for maplayer in m.listLayers():
    if maplayer.isFeatureLayer:
        if str(arcpy.management.GetCount(maplayer))=='8174955':
            popLyrFinal=maplayer



#############################################################
#USING popLyrFinal FROM EITHER USER INPUT OR LIVING ATLAS, SELECT BY LOCATION

#Extract population data intersecting input polygons to cut down on runtime, living atlas layer has 8 million features
popLyrIntersect=arcpy.management.SelectLayerByLocation(popLyrFinal,'',inAreaFinal) #this works inside arcPro
#arcpy.management.CopyFeatures(popLyrIntersect, popInt.shp,) #may not need to do this, just use input with selected features

#its_working.gif


###########################################################
##PASS SELECTED POPULATION FEATURES AND DISSOLVED INPUT POLYGONS INTO TABULATE INTERSECTIONS TOOL
##WITH INPUT POLYGONS AS ZONE LAYER, DISSOLVE FIELD OR OBJECT ID AS ZONE fields, POP LAYER AS CLASS FIELD
##GEO_ID AS CLASS FIELD, AND POP_TOTAL AS SUM FIELD

#tabTable=arcpy.analysis.TabulateIntersections(in_zone_features, zone_fields, in_class_features, out_table, {class_fields}, {sum_fields})


###########################################################
##PASS TABULATE FEATURES TABLE INTO arcpy.management.PivotTable(in_table, zone_fields, class_fields, population_field, out_table)

#arcpy.management.PivotTable(tabTable, dissfield_or_obj, pivot_field, pop_field, out_table)

##OUTPUT PIVOT TABLE AS FINAL OUTPUT



#2020 Census Kyle:45,697
#Our Estimate: 46,204
#Select All intersecting blocks: 54,942

aprx.save()