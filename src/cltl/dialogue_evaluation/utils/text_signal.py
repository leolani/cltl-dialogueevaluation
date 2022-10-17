from emissor.representation.scenario import TextSignal



def get_speaker_from_text_signal(textSignal: TextSignal):
    speaker = None
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'ConversationalAgent':
                speaker = annotation.value
                break
        if speaker:
            break
    return speaker


def get_turns_with_context_from_signals(signals: [], max_context=200):
    ids = []
    quadruples = []
    speakers = set()
    context = ""
    target = ""
    cue = ""
    for index, signal in enumerate(signals):
        ids.append(signal.id)
        speaker = get_speaker_from_text_signal(signal)
        if speaker:
            speakers.add(speaker)
        if index == 0:
            target = ''.join(signal.seq)
        else:
            cue = target
            context += " " + target
            target = ''.join(signal.seq)
        if len(context) > max_context:
            context = context[len(context) - max_context:]
        quadruple = (context, target, cue, speaker)
        quadruples.append(quadruple)
    return ids, quadruples, speakers
