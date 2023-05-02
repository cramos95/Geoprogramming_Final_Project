# Municipal Area Population Estimation Through Areal Interpolation of Census Data

The tool presented here is an ESRI ArcGIS python script tool written for use in ArcGIS Pro.
The tool provides an alternative to the popular, yet tedious Housing Unit Method of small area population estimation.  The tool requires nothing more from the user than a feature class or feature layer of the study area
and does not use the tedious calculations associated with the Housing Unit Method.

By default, the tool uses 2020 Census Blocks as the population data, taken from the ESRI Living Atlas 

[ESRI Living Atlas 2020 Census Blocks](https://www.arcgis.com/home/item.html?id=b3642e91b49548f5af772394b0537681#overview)

## Installation

Download and add the ArcGIS Toolbox to an ArcGIS Pro Project to use the tool.



## Usage


### There are two options for the use of this tool

1) The user provides only a polygon study area

In this case, the tool will add the ESRI Living Atlas 2020 Census Blocks layer as the population layer for the estimation.  

2) The user provides both a study area polygon and a polygon layer containing population data.

In this case, the user must also select which of the fields contains the population data

### Other Requirements and Recommendations

If the user-submitted study area feature layer or feature class contains more than 1 feature (i.e. more than 1 city or area polygon), the user must select a field to dissolve on. This will usually be the field containing the city names, but can also be a UID field. Whichever field is used will be displayed in the output table to identify the separate population estimates. For example in the table below, the City_Name field is the field selected as the dissolve field:

FID City_Name PopEstimate

0 Austin  950,000

1 San Marcos  55,000

| FID       | City_Name           | PopEstimate  |
| ------------- |:-------------:| -----:|
| 0     | Austin       | 950000 |
|1      | San Marcos      |   55,000 |

Due to the limitations in the system tools used in the script, the user input study area(s) cannot contain more than 5 features (i.e. 5 study areas or 5 cities). However it is recommended that no more than 2 features be used as the runtime becomes significantly higher with more input features. It is more efficient to pass multiple study areas into the tool 1 or 2 at a time.


### Limitations
At present, the tool requires further research to improve the reliability of the populaiton estimates.  In testing, the population estimates for the majority of cities was less than 2% different
than the known populations.  However, for certain cities the error is higher than 10% and in some rare cases, higher than 50%.  Please check that the estimate provided is reasonable for the study area. 


### Data in Folder

The file, "GEO5419_PopEstimate.atbx" is the ESRI Toolbox containing the script tool described here
The file, "PopEst_ArcProSetup.py" is the python code associated (and embedded in) the script tool described here
The file, "README.html" is a help file describing the use of the script tool described here
The file, "TestData1.zip" Contains a shapefile named "Cities".  This Cities shapefile contains the Municipal City limits boundaries for the appx. 1200 cities in Texas.  To test the tool, select one or two of these cities as described above, and then pass the shapefile with the selection into the script tool as the input study area. 


## Read the Research
[Research Paper](https://git.txstate.edu/cgr50/GIS_Final_Project/blob/master/Ramos_Jackson_Research.pdf)






## License

[License](https://choosealicense.com/licenses/mit/)
