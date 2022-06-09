import json
from pathlib import Path


def map_emissor_scenarios(scenario_folder, rdf_folder):
    # TODO fix the first upload with ontology
    # Read rdf files, ordered temporaly
    datapath = Path(rdf_folder)
    files = sorted([path for path in datapath.glob('*.trig')])

    # Read from EMISSOR
    with open(scenario_folder + 'text.json', 'r') as j:
        data = json.loads(j.read())

    utterances = []
    utt_id = None

    # Loop through utterances, to map ids to those present in the rdf files
    for index, item in enumerate(data):
        speakers = set()
        rdf_file = []

        # Loop through mentions to find an utterance id
        for m in item['mentions']:
            for ann in m['annotations']:
                if type(ann) == list:
                    ann = ann[0]
                if ann['type'] == 'utterance':
                    speakers.add(ann['source'])
                    utt_id = ann['value']

        # find in files
        if utt_id:
            for f in files:
                txt = Path(f).read_text()
                if utt_id in txt:
                    rdf_file = [f.stem + '.trig']
                    files.remove(f)
                    break

        # Add utterance, with rdf file pointers if available
        utterance = {"Turn": index, "Speaker": speakers.pop(),
                     "Response": ''.join(item['seq']), "rdf_file": rdf_file}
        utterances.append(utterance)

    # Check if there is a generic rdf file left to map, probably the ontology upload
    if len(files) == 1:
        utterances[0]["rdf_file"].append(files[0].stem + '.trig')
        files.remove(files[0])

    with open(scenario_folder + '/turn_to_trig_file.json', 'w') as f:
        js = json.dumps(utterances)
        f.write(js)
