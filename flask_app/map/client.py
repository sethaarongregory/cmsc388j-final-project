# imports
import requests
import pandas as pd
import numpy as np
import folium
import certifi

from folium import plugins
from SPARQLWrapper import SPARQLWrapper, JSON


# Our MapClient will generate maps and maintain them
class MapClient(object):
    def __init__(self):
        self.pd_table = initialize_pd_table()
        self.basic_map = basic_map(self.pd_table)
        self.heat_map = heat_map(self.pd_table)

    # Unused in current implementation
    def year_map(self, df, year):
        m = folium.Map(location=[35, -100], zoom_start=4)

        for i in range(0, len(df)):
            if df.iloc[i]['birthYear'] == year:
                name = df.iloc[i]['name']
                content = df.iloc[i]['description']
                html = folium.Html('<b>' + name + '</b><p>' + content + '</p>', script=True)
                popup = folium.Popup(html, max_width=250)
                folium.Marker([df.iloc[i]['lat'], df.iloc[i]['long']], popup=popup).add_to(m)

        return m

    # Save our map as an html file
    def save_html(self, map, name):
        route = './flask_app/map/' + name
        map.save(route)

# Helper functions for generation maps and running SPARQL queries

def heat_map(df):
    heatm = folium.Map(location=[35,-100], zoom_start=4)
    heat_data = [[[row['lat'], row['long']] for idx, row in
                  df[(df['birthDate'] <= i) & (df['birthDate'] + 10 > i)].iterrows()] for i in range(1875, 1990)]

    hm = plugins.HeatMapWithTime(heat_data, auto_play=True, max_opacity=0.8)
    hm.add_to(heatm)

    return heatm


def initialize_pd_table():
    df = dfResults(endpoint, prefix, q)

    df['lat'] = df['lat'].astype(float)
    df['long'] = df['long'].astype(float)
    df = df.drop_duplicates(subset=['person'])
    df['name'].replace('', np.nan, inplace=True)
    df.dropna(subset=['name'], inplace=True)

    for idx, row in df.iterrows():
        bd = str(row['birthDate']).split('-')
        df.loc[idx, 'birthDate'] = float(bd[0])

    return df

def basic_map(df):
    m = folium.Map(location=[35, -100], zoom_start=4)

    for i in range(0, len(df)):
        name = df.iloc[i]['name']
        content = df.iloc[i]['description']

        html = '<b>' + name + '</b><p>' + content + '</p>'

        html = folium.Html(html, script=True)
        popup = folium.Popup(html, max_width=250)
        folium.Marker([df.iloc[i]['lat'], df.iloc[i]['long']], popup=popup).add_to(m)

    return m

# Code for compatibility between SPARQL and pandas, source:
# https://gist.github.com/psychemedia/0b5e6d7b51750b63a1041c66264e51c2

# A function that will return the results of running a SPARQL query with
# a defined set of prefixes over a specified endpoint.
# It follows the same five-step process apart from creating the query, which
# is provided as an argument to the function.
def runQuery(endpoint, prefix, q):
    ''' Run a SPARQL query with a declared prefix over a specified endpoint '''
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(prefix + q)  # concatenate the strings representing the prefixes and the query
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

# Function to convert query results into a DataFrame
# The results are assumed to be in JSON format and therefore the Python dictionary will have
# the results indexed by 'results' and then 'bindings'.
def dict2df(results):
    ''' A function to flatten the SPARQL query results and return the column values '''
    data = []
    for result in results["results"]["bindings"]:
        tmp = {}
        for el in result:
            tmp[el] = result[el]['value']
        data.append(tmp)

    df = pd.DataFrame(data)
    return df


# Function to run a query and return results in a DataFrame
def dfResults(endpoint, prefix, q):
    ''' Generate a data frame containing the results of running
        a SPARQL query with a declared prefix over a specified endpoint '''
    return dict2df(runQuery(endpoint, prefix, q))


# Print a limited number of results of a query
def printQuery(results, limit=''):
    ''' Print the results from the SPARQL query '''
    resdata = results["results"]["bindings"]
    if limit != '':
        resdata = results["results"]["bindings"][:limit]
    for result in resdata:
        for ans in result:
            print('{0}: {1}'.format(ans, result[ans]['value']))
        print()


# Run a query and print out a limited number of results
def printRunQuery(endpoint, prefix, q, limit=''):
    ''' Print the results from the SPARQL query '''
    results = runQuery(endpoint, prefix, q)
    printQuery(results, limit)


# Define any prefixes
prefix = '''
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbc: <http://dbpedia.org/resource/Category:>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

    PREFIX ouseful:<http://ouseful.info/>
'''

# Declare the DBPedia endpoint
endpoint="http://dbpedia.org/sparql"
sparql = SPARQLWrapper(endpoint)

q = '''
SELECT DISTINCT ?person ?name ?description ?abstract ?birthPlaceName ?lat ?long ?birthDate
WHERE {
      ?person a dbo:MusicalArtist .
      ?person dbo:genre dbr:Jazz .
      ?person dbo:birthDate ?birth .
      ?person dbp:birthPlace ?birthPlaceName .
      ?person dbo:birthPlace ?birthPlace .
      ?person dbo:birthDate ?birthDate .

      ?birthPlace geo:lat ?lat .
      ?birthPlace geo:long ?long .

      ?person dbp:name ?name .
      ?person rdfs:comment ?description .
      ?person dbo:abstract ?abstract .

      FILTER (LANG(?description) = 'en') .
      FILTER(LANG(?abstract) = 'en') .
      FILTER (LANG(?name) = 'en') . 
} ORDER BY ?name LIMIT 3000
'''

