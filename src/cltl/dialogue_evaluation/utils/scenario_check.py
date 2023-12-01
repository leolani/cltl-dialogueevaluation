import glob
import os

def check_scenario_data(scenario_folder, scenario):
    HAS_SCENARIO = False
    HAS_TEXT = False
    HAS_IMAGE = False
    HAS_RDF = False
    for f in os.listdir(scenario_folder):
    #for f in glob.glob(scenario_folder):
        print(f)
        if f==scenario+'.json':
            HAS_SCENARIO=True
        if (scenario+'.json').endswith(f):
            HAS_SCENARIO=True
        elif f=='text.json':
            HAS_TEXT=True
        elif f=='image.json':
            HAS_IMAGE=True
        elif f=='rdf':
            HAS_RDF=True
    return HAS_SCENARIO, HAS_TEXT, HAS_IMAGE, HAS_RDF
