from sodapy import Socrata
import pandas as pd
import numpy as np
from tqdm import tqdm

def update_cdc_fips(fips):
    """ Updates (in-place) FIPS codes for CDC dataset to match wikipedia FIPS data """
    
    # County code changes in the 2010s - wikipedia is up-to-date but CDC slightly out of date
    fips_updates = {
    '46113': '46102', # shannon county, SD (46113) renamed to oglala lakota county (46102)
    '51515': '51019' # bedford city (51515) merged into bedford county (51019)
    }
    
    for oldfips, newfips in fips_updates.items():
        fips = fips.str.replace(oldfips, newfips, regex=False)
    return fips

def get_cdc_data(date, ozone=True, limit=100000):
    """
    Fetches data from CDC website using Socrata API.
    API code example from https://dev.socrata.com/foundry/data.cdc.gov/fcqm-xrf4

    DATE: array of strings in DDMMMYYYY form (e.g. "01JAN2014")
    OZONE: boolean (True for ozone data, False for PM 2.5 data)
    LIMIT: integer limit for maximum number of rows downloaded

    returns pandas dataframe containing up to LIMIT rows of the result
    """
    assert type(date) in [str, list]
    if type(date) == str:
        date = [date]
    
    dataset_id = "372p-dx3h" if ozone else "fcqm-xrf4"
    colname = "ds_o3_pred" if ozone else "ds_pm_pred"
    client = Socrata("data.cdc.gov", None)

    res = None
    for d in tqdm(date):
        # arguments are SQL-style: see https://dev.socrata.com/docs/queries/
        results = client.get(dataset_id, query=f"SELECT countyfips, {colname} WHERE date = '{d}' LIMIT {limit}")
        df = pd.DataFrame.from_records(results)
        df = df.rename(columns={colname: d}) # rename column to corresponding date
        df[d] = df[d].astype(np.float64) # cast to float (from string)
        
        # since we only have population data at the county level and not city,
        # we aggregate to use the median of all cities in the same county
        df = df.groupby("countyfips").agg({d: 'median'})

        if res is None:
            res = df
        else:
            res = res.join(df, how='inner')

    # convert FIPS to 5-digit strings (so 1001 becomes '01001')
    res.index = res.index.astype(str).str.zfill(5)
    res.index = update_cdc_fips(res.index)
    return res

def get_county_fips(fips_path):
    """
    Parses wikipedia data downloaded from https://en.wikipedia.org/wiki/List_of_United_States_FIPS_codes_by_county
    CSV_PATH should be the path to the downloaded file
    """
    
    county_fips = pd.read_csv(fips_path, names=['fips', 'county', 'state'], header=0)
    
    # convert FIPS to 5-digit strings, and append state name to county
    county_fips['fips'] = county_fips['fips'].astype(str).str.zfill(5)
    county_fips['county'] = county_fips['county'] + ', ' + county_fips['state']
    county_fips['county'] = county_fips['county'].str.lower()

    # remove/replace special characters
    county_fips['county'] = county_fips['county'].str.replace("\s*–\s*", "-", regex=True)
    county_fips['state'] = county_fips['state'].str.replace("Hawaiʻi", "Hawaii", regex=False)

    # Replace phrases in wikipedia FIPS data to match with population dataset
    wiki_fips_replacements = {
        ", municipality of": " municipality",
        ", city and borough of": " city and borough",
        ", city of": " city",
        ", city and county of": " county",
        ", town and county of": " county",
        "city, consolidated municipality of": "city",
        "hawaiʻi": "hawaii"
    }

    for old, new in wiki_fips_replacements.items(): 
        county_fips['county'] = county_fips['county'].str.replace(old, new, regex=False)

    # valdez-cordova was split into chugach census area and copper river census area in 2019,
    # according to https://en.wikipedia.org/wiki/Valdez-Cordova_Census_Area
    # but the census data still uses the combined area
    county_fips.loc[len(county_fips)] = ['02063,02066', 'valdez-cordova census area, alaska', 'Alaska']
    
    return county_fips

def get_county_pops(pop_path):
    """
    Parses csv data downloaded from https://www2.census.gov/programs-surveys/popest/tables/2010-2019/counties/totals/co-est2019-annres.xlsx
    CSV_PATH should be the path to the downloaded file
    """

    county_pops = pd.read_csv(pop_path, header=3)
    county_pops = county_pops[["Unnamed: 0", "2014"]].iloc[1:-6].rename(columns={"Unnamed: 0": "county", "2014": "2014 population"})

    # delete the dot in front of county names
    county_pops['county'] = county_pops['county'].str.lower().str.replace("^\.", "", regex=True)

    # convert string population numbers to int
    county_pops['2014 population'] = county_pops['2014 population'].str.replace(",", "").astype(int)

    return county_pops

def add_state_abbreviations(df, path):
    """
    Adds 2-letter state abbreviations to data frame based on table from
    https://www.scouting.org/resources/los/states/
    """
    
    abbrevs = pd.read_csv(path, header=0, names=['state', 'abbrev'])
    df = df.merge(abbrevs, left_index=True, right_on="state", how="left")
    return df

def agg_county_weighted_mean(df, columns=None, data_dir="data"):
    """
    COLUMNS: 
    """
    if columns is None:
        columns = df.columns

    fip_to_county = get_county_fips(data_dir + "/county_to_state_aggregation/county_fips_wikipedia.csv")
    county_pops = get_county_pops(data_dir + "/county_to_state_aggregation/county_populations.csv")

    df = df.merge(fip_to_county, left_index=True, right_on="fips", how="left")
    df = df.merge(county_pops, on="county", how="left")

    # take weighted mean by county population
    wm = lambda x: np.average(x, weights=df.loc[x.index, "2014 population"])
    fn_mapper = {}
    for col in columns:
        fn_mapper[col] = (col, wm)
    df_by_state = df.groupby("state").agg(**fn_mapper)
    
    return add_state_abbreviations(df_by_state, data_dir + "/county_to_state_aggregation/state_abbreviations.csv")