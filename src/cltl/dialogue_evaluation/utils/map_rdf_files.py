import json
from pathlib import Path
import re


def load_scenario(scenario_folder, rdf_folder):
    # Read rdf files, ordered temporaly
    files = sorted([path for path in rdf_folder.glob('*.trig')])

    # Read from EMISSOR
    with open(scenario_folder / 'text.json', 'r') as j:
        data = json.loads(j.read())

    return data, files


def get_speaker(data):
    speaker = 'SPEAKER'
    for item in data:
        for m in item['mentions']:
            for ann in m['annotations']:
                if ann['type'] == 'VectorIdentity':
                    # Establish speaker identity
                    speaker = ann['value']

    return speaker


def process_mentions(ann, utt_id, rdf_file, speaker=None, files=None):
    # Process utterances
    if ann["type"] == "ConversationalAgent":
        rdf_file, files = search_id_in_log(utt_id, rdf_file, files)
        return rdf_file, speaker
    else:
        return rdf_file, speaker


def search_id_in_log(utt_id, rdf_file, files):
    files_to_remove = []

    for f in files:
        txt = Path(f).read_text()
        if utt_id in txt:
            # Found it!
            rdf_file.append(f.stem + '.trig')
            files.remove(f)
            break

    for f in files_to_remove:
        files.remove(f)

    return rdf_file, files


def map_emissor_scenarios(scenario_folder, rdf_folder):
    data, files = load_scenario(scenario_folder, rdf_folder)
    speaker = get_speaker(data)

    # Loop through utterances, to map ids to those present in the rdf files
    utterances = []
    for index, item in enumerate(data):
        utt_id = item['id']
        rdf_file = []

        # Loop through mentions to find an utterance id
        for m in item['mentions']:
            for ann in m['annotations']:
                rdf_file, utterance_speaker = process_mentions(ann, utt_id, rdf_file, speaker=speaker, files=files)

        # Add utterance, with rdf file pointers if available
        utterance = {"Mention ID": utt_id, "Turn": index, "Speaker": utterance_speaker,
                     "Response": item['text'], "rdf_file": rdf_file}
        utterances.append(utterance)

    # Check if there is a generic rdf file left to map, probably the ontology upload
    if len(files) == 1:
        utterances[0]["rdf_file"].append(files[0].stem + '.trig')
        files.remove(files[0])

    with open(scenario_folder / 'turn_to_trig_file.json', 'w') as f:
        js = json.dumps(utterances)
        f.write(js)
