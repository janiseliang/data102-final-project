# Code in this script is used for downloading and processing data
# (from the CDC and other sources) to prepare for analysis.
# The data from this step is placed in the `data/` folder.

PATH_TO_DATA = "../data"

import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from sodapy import Socrata

from scripts.aqi_state_agg import get_cdc_data, agg_county_weighted_mean

months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
dates = sum([["01"+m+str(yr) for m in months] for yr in np.arange(2011, 2015)], [])

def show_state_data(state_data, title=""):
  plt.figure(figsize=(10, 5))
  plt.plot(cali)

  labels = [x.capitalize() for x in months]*4
  for i in range(4): labels[i*12] = str(i+2011) + " " + labels[i*12]

  plt.xticks(ticks=np.arange(len(labels)), labels=labels, rotation=90)
  plt.title(title)

  plt.axhline(y=cali.mean(), c="g", linestyle='--', label="average")
  plt.axhline(y=cali.median(), c="gray", linestyle=':', label="median")
  plt.legend()

  plt.show()

def agg_ozone_data():
  ozone = get_cdc_data(dates, ozone=True)
  ozone_by_state = agg_county_weighted_mean(ozone)
  ozone_by_state = ozone_by_state.set_index('abbrev')

  show_state_data(ozone_by_state.loc['CA'].drop('state'), title="California ozone concentration cycles")

  

if __name__ == "__main__":
    