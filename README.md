# lora_graph_gw

This repository includes all scripts used to generate the placements evaluated in "Graph-Based Gateway Placement for Better Performance in LoRaWAN Deployments". The folder structure is as follows: the "General" folder includes the scripts necessary to generate the collision probability results for the individual scenarios. These scripts are universal, except for specifically adapted versions used in S4. This folder also includes the sensor's dataset for the city of Wuerzburg used in evaluation.

To reproduce the placements in the work, this dataset should be copied to the individual scenarios folders and renamed to "sensors.csv" to be identified by the script.

Executing the script produces three output files for each result: 

- "gateways_Placement_XXX.csv"
- "reachable_Sensors_XXX.csv"
- "reachable_Sensors_XXX.json"

These files contain the locations and other properties required by the collision probability simulation, for the gateways and sensors respectively.

To conduct a simulation on these results, a new subfolder named "files" has to be created and all result files need to be moved to this folder. The folder structure is as follows:

Scenario Folder
- files
- - gateways_Placement_XXX.csv
- - reachable_Sensors_XXX.csv
- - reachable_Sensors_XXX.json
- Placement_XX.py
- gatewayplacement_collisioncalc.py
- network_collisionanalysis.py
- sensors.csv

After this folder structure is created, the collision probability scripts can be executed. First run the "gatewayplacement_collisioncalc.py" script. This produces additional "_transmissionrange.json" files in the "files" subdirectory. Last, the "network_collisionanalysis.py" script can be executed. This produces the final "2000mitFixedGateways" result file.

## S3
S3 is a special case, as it processes different datasets. To acquire new data for other locations, the "Get_OpenStreetMapData.ipynb" can be used to search for a specific location and download the building locations. To produce correct results, the projected coordinate system has to be correct for each location in all files. The following lines need to be adjusted in each file:

- Get_OpenStreetMapData.ipynb: line 204
- Graph_Metric_Placement.py: lines 59 and 82
- Voronoi_to_Simulation.py: lines 40 and 67

To produce the voronoi cover results, the "sensors.csv" file from the "Get_OpenStreetMapData.ipynb" script can be converted to the input format used by the voronoi cover script using the "Sensors_to_Voronoi.py" script and processed with the voronoi cover script (https://github.com/DomiBau/VoronoiCover). The results can be converted to the simulation input using the "Voronoi_to_Simulation.py" script.

## S5
This scenario is separated into sub scenarios. The general script for performing the clustering is found in the main directory of the scenario. Further subdirectories automate the process for the other scenarios evaluated in the Paper, but use the same internal implementation. The analysis from then on is the same as the other scenarios.
### S5.3
The naming scheme for the sensor files is different from previous scenarios. To process different cities, the sensor files should follow the template "sensors_XX.csv" for this scenario. The script has an option in the main loop to define which values of "XX" are processed. This could also be removed, if it is not required.