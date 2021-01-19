Creator: Erin Carroll
Contact: erin_carroll@berkeley.edu
Last Update: January 19, 2021

The files in this repository collectively produce distribution maps (presence/absence) for quaking aspen (Populus tremuloides) over a ~1500 km^2 area near the Rocky Mountain Biological Laboratory in 2019 and 2020. 
S2SRstack2019.py creates a quality mosaic of Sentinel-2 surface reflectance (Level 2a) imagery over 2019 minimizing clouds, shadows, and snow. The final image has 50 bands – 10 of the 13 available bands quality mosaicked for each month June-October. We exclude the three ‘atmospheric’ bands at 60m resolution. S2SRstack2020.py does the same for 2020.

dist_RF_RMBL_2019.ipynb and dist_RF_RMBL_2020.ipynb are python notebooks to be opened in Google Colab. They import the final images produced in S2SRstack2019.py and S2SRstack2020.py, respectively. Each produces an aspen cover map using a random forest classifier. Reference data was hand-delineated using high-resolution Google Earth Engine basemap imagery.
