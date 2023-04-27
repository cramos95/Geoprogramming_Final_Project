import arcpy
from arcpy import analysis  # if I don't import this separately, arcpy.analysis.TabulateIntersection() won't work
import sys

# INITIAL SETUP


#INPUT PARAMETERS
inArea1=arcpy.GetParameterAsText(0) #required study area
inAreaDissField=arcpy.GetParameterAsText(1) #optional study area dissolve field
popLyr1=arcpy.GetParameterAsText(2) #optional user-submitted population data
popLyrField=arcpy.GetParameterAsText(3) #optional population data field containing population data
finalOutput=arcpy.GetParameterAsText(4) #required output table

#path for living atlas layer
dataPath = r'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_2020_Redistricting_Blocks/FeatureServer'


# Will need to use mapObject.addDataFromPath() to add living atlas layer, therefore, must first create a project object, preferably with "CURRENT"
#Will also use to add final output to current map. aprx.save() added at end of script as well.
aprx = arcpy.mp.ArcGISProject("CURRENT")

# Set map object to variable with activeMap method
m = aprx.activeMap



##---------------------------------------------------------------------------------------------------
# CREATE FUNCTION TO ADD MESSAGES THROUGHOUT SCRIPT, taken from arcpy documentation
def AddMsgAndPrint(msg, severity=0):
    # Adds a Message (in case this is run as a tool)
    # and also prints the message to the screen (standard output)
    print(msg)

    # Split the message on \n first, so that if its multiple lines,
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

#Error checks and messages on user input study area

#check input for type polygon-stolen from arcpy documentation
inArea1Desc=arcpy.Describe(inArea1)
if inArea1Desc.shapeType != "Polygon" :
    AddMsgAndPrint("Input Study Area must be of type polygon.", 2)
    sys.exit()

#check input study area for >1 features, if so, require dissolve field

if int((arcpy.management.GetCount(inArea1))[0]) > 1: #getCount returns a Result object,  Result[0] references the actual output value, have to wrap in int() because returns string
    if inAreaDissField == "":
        AddMsgAndPrint("Input Study Area has more than 1 feature, dissolve field required.", 2)
        sys.exit()

#Only one dissolve field-also stolen from documentation
if inAreaDissField != "":
    if inAreaDissField.find(";") > -1:
        AddMsgAndPrint("A maximum of one dissolve field is allowed.", 2)
        sys.exit()


#---------------------------------------------------------------------------------------------------
#DISSOLVE STUDY AREA

#If user input dissolve field, dissolve with field, else dissolve all, wrap in try/except with messages
#Either way, set output equal to inAreaFinal variable
if inAreaDissField != "":
    try:
        result=arcpy.management.Dissolve(inArea1, '#', inAreaDissField) #dissolve and other geoprocessing tools do not return the filepath to the output, but they can be set to the result object, see https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/result.htm for more info
        inAreaFinal = result
    except:
        AddMsgAndPrint("Dissolve Failed.", 2)
        sys.exit()
elif inAreaDissField == "":
    try:
        result = arcpy.management.Dissolve(inArea1, '#')
        inAreaFinal = result
    except:
        AddMsgAndPrint("Dissolve Failed.", 2)
        sys.exit()

AddMsgAndPrint("Finished dissolve", 0)


##---------------------------------------------------------------------------------------------------
#USER PROVIDES POPULATION DATA

#Error checks and messages on user input population data

#check for shape=polygon
if popLyr1 != "":
    popLyrDesc = arcpy.Describe(popLyr1)
    if popLyrDesc.shapeType != "Polygon" :
        AddMsgAndPrint("User submitted population data must be of type polygon.", 2)
        sys.exit()

#check for input population field
if popLyr1 != "" and popLyrField == "":
    AddMsgAndPrint("If user submits population data, population field must be provided.", 2)
    sys.exit()

#Only one input population field allowed
if popLyr1 != "" and popLyrField != "":
    if popLyrField.find(";") > -1:
        AddMsgAndPrint("A maximum of one population field is allowed.", 2)
        sys.exit()

#check input population field for validity, null values, and non-integer values
if popLyr1 != "" and popLyrField != "":
    try:
        with arcpy.da.SearchCursor(popLyr1,popLyrField) as cur1:
            for row in cur1:
                if isinstance(row[0], int) != True:
                    AddMsgAndPrint("Population field contains null or non-integer values.", 2)
                    sys.exit()
    except:
        AddMsgAndPrint("Population field is not a valid field", 2)
        AddMsgAndPrint(arcpy.Getmessages(),0)
        sys.exit()

#If popLyr1 is not blank, i.e. user submits population data and makes it through the above checks then>
#set input variable to popLyrFinal. Otherwise, proceed to default population layer
if popLyr1 != "":
    popLyrFinal = popLyr1
else:
    ##---------------------------------------------------------------------------------------------------
    # USER DOES NOT PROVIDE POPULATION DATA, DEFAULT TO LIVING ATLAS LAYER

    # add the living atlas layer from path, with method on map object
    m.addDataFromPath(dataPath)

    # get newly added layer as popLyrFinal variable
    # Note, the layer imports as a group layer, and the sublayer needed is called 'Blocks', which is
    # generic and it seems inconsistent, somtimes called 'USA_BLOCK_GROUPS//Blocks, therefore, will get the layer into a variable by counting the number of features
    # for every layer in the map, if is feature layer and if count==8174955, it's the layer we want. tested in arcPro
    for maplayer in m.listLayers():
        if maplayer.isFeatureLayer:
            if str(arcpy.management.GetCount(maplayer)) == '8174955':
                popLyrFinal = maplayer

AddMsgAndPrint("Finished adding population data", 0)


##---------------------------------------------------------------------------------------------------
##PASS POPULATION FEATURES AND DISSOLVED INPUT POLYGONS INTO TABULATE INTERSECTIONS TOOL

# at this point, the following variables will be set
# inAreaFinal #the user submitted study area
# popLyrFinal #either the user submitted or default population layer
# inAreaDissField #may be blank if not user-submitted

##Use Input polygons as zone layer, dissolve field or object id as zone fields, pop layer as class layer
##pop layer oid as class field, and pop total or population field as sum field

# input variable setup
in_zone_features = inAreaFinal

# for zone fields, either dissolve field or OID, need to get OID with oid_fieldname = arcpy.Describe(fc).OIDFieldName
if inAreaDissField == "":  # i.e., no dissolve field, get oid field name
    oidField = arcpy.Describe(in_zone_features).OIDFieldName  #THIS STEP IS NOT WORKING, NOT PASSING OID FIELD AS GROUP BY FIELD IN SUM STATISTICS, might be because its returning 'OBJECTID' which creates a duplicate object id.
    arcpy.management.AddField(in_zone_features, 'ObjID', 'TEXT') #add new field to hold OG OID field values
    if oidField == 'OBJECTID': #check oid field name and pass into calculate field, cant figure out how ot pass variable in with !variable! notation
        arcpy.management.CalculateField(in_zone_features, 'ObjID', '!OBJECTID!')
    elif oidField == 'FID':
        arcpy.management.CalculateField(in_zone_features, 'ObjID', '!FID!')

    #set zone_fields, the case field for the sum/group by, to the newly created objID
    zone_fields='objID'
    AddMsgAndPrint(zone_fields, 0)
    #add field objid and set equal to OIDFieldName to avoid duplicate 'OBJECTID' when passing into statistics

else:
    zone_fields = inAreaDissField

# class features are the population polygons
in_class_features = popLyrFinal

# class fields are the objectIDs of the population polygons
class_fields = arcpy.Describe(in_class_features).OIDFieldName

# sum fields are the field containing the population data,
if popLyr1 == "":  # if no user submitted population data
    sum_fields = 'P0010001'
else:  # user submitted population data
    sum_fields = popLyrField

#run tabulate intersections
result = arcpy.analysis.TabulateIntersection(in_zone_features, zone_fields, in_class_features, '#', class_fields, sum_fields)
tabTable = result


##---------------------------------------------------------------------------------------------------
#PASS TABULATE FEATURES TABLE INTO Statistics

#to do a sum and group by input area.

arcpy.analysis.Statistics(tabTable, finalOutput, [[sum_fields, "SUM"]], zone_fields)

##---------------------------------------------------------------------------------------------------
##OUTPUT STATS TABLE AS FINAL OUTPUT

#clean up fields, change POO10001 to popTotal, remove extras etc.

# drop 'FREQUENCY' FIELD
arcpy.management.DeleteField(finalOutput, ['FREQUENCY'])

# change fields starting with 'SUM_' to popTotal, change only other non-OID field to studyAreaID, which will be either the study area OID or the dissolve field.
# get SUM_field and study area field to variables, they will be named different depending on user submitted or default population data
# works bc only 3 fields total, the OID, the SUM_, and the 3rd field.
fields = arcpy.ListFields(finalOutput)
finalOutputOIDName = arcpy.Describe(finalOutput).OIDFieldName

#user submits dissolve field
if inAreaDissField != "":
    for field in fields:
        if field.name != finalOutputOIDName:
            if field.name.startswith('SUM_'):
                alterField = field.name
                arcpy.management.AlterField(finalOutput, alterField, '', 'popTotal')
            else:
                alterField1 = field.name
                arcpy.management.AlterField(finalOutput, alterField1, '', 'studyAreaID')

#no dissolve field
if inAreaDissField == "":
    for field in fields:
        if field.name.startswith('SUM_'):
            alterField = field.name
            arcpy.management.AlterField(finalOutput, alterField, '', 'popTotal')


outDesc=arcpy.Describe(finalOutput)
outPath=outDesc.catalogPath
m.addDataFromPath(outPath)

##---------------------------------------------------------------------------------------------------
#SAVE CURRENT PROJECT
aprx.save()

##---------------------------------------------------------------------------------------------------
#END




#Possible Future Functionality
#keep dissolve and tab intersections from writing to file to keep clutter down?
#Maybe add functionality for multiple study areas. Merge incoming polygon layers, keep OID only # to account for different schemas?
#Split incoming study areas to pass into tabulate intersections one at a time to improve runtime

#INITIAL ANALYSIS
# Texas Demographic Center 2020 Census Kyle:45,697
# Our Estimate: 46,204
# %diff=1.109% overestimation
# Select All intersecting blocks: 54,942
# %diff=20.23%
# Select All blocks completely within: 36,604
# %diff=24.84%


# Texas Demographic Center 2020 Census San Marcos: 67,553
# Our Estimate: 67,801
#% diff = 0.36% overestimation
