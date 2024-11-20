import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse
import sys
from emissor.representation.scenario import Signal
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality
import cltl.dialogue_evaluation.utils.text_signal as text_signal_util
import cltl.dialogue_evaluation.utils.scenario_check as check

class PlotSettings():
    _LLH_THRESHOLD = 0
    _SENTIMENT_THRESHOLD = 0
    _ANNOTATIONS =[]

def get_signal_rows(signals:[Signal], human, agent, settings: PlotSettings):
    data = []
    for i, signal in enumerate(signals):
        speaker = text_signal_util.get_speaker_from_text_signal(signal)
        if speaker=='SPEAKER':
            speaker = human
        elif speaker=='AGENT':
            speaker = agent
        text = ''.join(signal.seq)
        score = 0
        score += text_signal_util.get_dact_feedback_score_from_text_signal(signal)
        if "sentiment" in settings._ANNOTATIONS:
            score += text_signal_util.get_sentiment_score_from_text_signal(signal)
        if "ekman" in settings._ANNOTATIONS:
            score += text_signal_util.get_ekman_feedback_score_from_text_signal(signal)
        if "go" in settings._ANNOTATIONS:
            score += text_signal_util.get_go_feedback_score_from_text_signal(signal)
        if "llh" in settings._ANNOTATIONS:
            score += text_signal_util.get_likelihood_from_text_signal(signal, settings._LLH_THRESHOLD)

        label = text_signal_util.make_annotation_label(signal, settings._SENTIMENT_THRESHOLD, settings._ANNOTATIONS)
        row = {'turn':i+1, 'utterance': text, 'score': score, "speaker": speaker, "type":signal.modality, "annotation": label}
        data.append(row)
    return data


def create_timeline_image(scenario_path, scenario, speaker:str, agent:str, signals:[Signal], settings: PlotSettings):
    rows = get_signal_rows(signals, speaker, agent, settings)
    plt.rcParams['figure.figsize'] = [len(rows), 5]
    df = pd.DataFrame(rows)
    #print(df.head())
    sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
 #   ax = sns.lineplot(x='turn', y='score', data=df, hue='speaker', style='annotation', markers=True, palette="bright", legend="brief")
    ax = sns.lineplot(x='turn', y='score', data=df, hue='speaker', style='speaker', markers=True, palette="bright", legend="brief")
    #palette = "flare/bright/deep/muted/colorblind/dark"
    for index, row in df.iterrows():
        x = row['turn']
        y = row['score']
        category = row['speaker']+":"+str(row['utterance'])
        category += '\n'+str(row['annotation'])
        ax.text(x, y,
                s=" " + str(category),
                rotation=70,
                horizontalalignment='left', size='small', color='black', verticalalignment='bottom',
                linespacing=1.5)

    ax.tick_params(axis='x', rotation=70)
    # Save the plot
    plt.legend(loc='lower right')
    plt.ylim(-5,5)

    evaluation_folder = os.path.join(scenario_path, "evaluation")
    if not os.path.exists(evaluation_folder):
        os.mkdir(evaluation_folder)
    path =  os.path.join(evaluation_folder, scenario+"_plot.png")
    plt.savefig(path, dpi=600)
    plt.show()


def main(emissor_path:str, scenario:str, annotations:[], sentiment_threshold=0, llh_threshold=0):
    scenario_path = os.path.join(emissor_path, scenario)
    has_scenario, has_text, has_image, has_rdf = check.check_scenario_data(scenario_path, scenario)
    check_message = "Scenario folder:" + emissor_path + "\n"
    check_message += "\tScenario JSON:" + str(has_scenario) + "\n"
    check_message += "\tText JSON:" + str(has_text) + "\n"
    check_message += "\tImage JSON:" + str(has_image) + "\n"
    check_message += "\tRDF :" + str(has_rdf) + "\n"
    print(check_message)
    if not has_scenario:
        print("No scenario JSON found. Skipping:", scenario_path)
    elif not has_text:
        print("No text JSON found. Skipping:", scenario_path)
    else:
        settings = PlotSettings()
        if annotations:
            settings._ANNOTATIONS = annotations
        if sentiment_threshold>0:
            settings._SENTIMENT_THRESHOLD=sentiment_threshold
        if llh_threshold>0:
            settings._LLH_THRESHOLD=llh_threshold
        scenario_path = os.path.join(emissor_path, scenario)
        print(scenario_path)
        print("_ANNOTATIONS", settings._ANNOTATIONS)
        print("_SENTIMENT_THRESHOLD", settings._SENTIMENT_THRESHOLD)
        print("_LLH_THRESHOLD", settings._LLH_THRESHOLD)
        scenario_storage = ScenarioStorage(emissor_path)
        scenario_ctrl = scenario_storage.load_scenario(scenario)
        speaker = scenario_ctrl.scenario.context.speaker["name"]
        agent = scenario_ctrl.scenario.context.agent["name"]
        text_signals = scenario_ctrl.get_signals(Modality.TEXT)
        create_timeline_image(scenario_path=scenario_path, scenario=scenario, speaker=speaker, agent=agent,
                              signals=text_signals, settings=settings)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Statistical evaluation emissor scenario')
    parser.add_argument('--emissor-path', type=str, required=False, help="Path to the emissor folder", default='')
    parser.add_argument('--scenario', type=str, required=False, help="Identifier of the scenario", default='')
    parser.add_argument('--sentiment_threshold', type=float, required=False, help="Threshold for dialogue_act, sentiment and emotion scores", default=0.6)
    parser.add_argument('--llh_threshold', type=float, required=False, help="Threshold below which likelihood becomes negative", default=0.3)
    parser.add_argument('--annotations', type=str, required=False, help="Annotations to be considered for scoring: 'go, sentiment, ekman, llh'" , default='go,sentiment,llh')
    args, _ = parser.parse_known_args()
    print('Input arguments', sys.argv)

    main(emissor_path=args.emissor_path,
         scenario=args.scenario,
         annotations=args.annotations,
         llh_threshold=args.llh_threshold,
         sentiment_threshold=args.sentiment_threshold)