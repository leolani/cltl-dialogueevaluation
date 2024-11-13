from emissor.representation.scenario import TextSignal


def make_annotation_label (signal, threshold):
    label = ""
    dacts = get_dact_from_text_signal(signal)
    gos = get_go_from_text_signal(signal)
    ekmans = get_ekman_from_text_signal(signal)
    sentiments = get_sentiment_from_text_signal(signal)
    print('dacts',dacts)
    print('gos', gos)
    print('ekmans', ekmans)
    print('sentiments', sentiments)
    # JSON(value='love', type='GO', confidence=0.890785276889801)
    # JSON(value='joy', type='EKMAN', confidence=0.9762245354068)
    # JSON(value='positive', type='SENTIMENT', confidence=0.9762245354068)
    # JSON(value='complaint', type='MIDAS', confidence=0.2305116355419159)
    if dacts:
        for dac in dacts:
            conf = dac[2]
            dac_label = dac[0]
            if conf > threshold:
                label += dac_label
                print(label)
    if sentiments:
        for sentiment in sentiments:
            conf = sentiment[2]
            sentiment_label = sentiment[0]
            if conf > threshold:
                label += ";"+sentiment_label
    if gos:
        for go in gos:
            conf = go[2]
            go_label = go[0]
            if conf > threshold:
                label += ";"+go_label
    if ekmans:
        for ekman in ekmans:
            conf = ekman[2]
            ekman_label = ekman[0]
            if conf > threshold:
                label += ";"+ekman_label
    return label


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

def get_sentiment_score_from_text_signal(textSignal: TextSignal):
    score = 0
    sentiments = get_sentiment_from_text_signal(textSignal)
    if sentiments:
        for sentiment in sentiments:
            if sentiment[0] == 'negative':
                score += -1
            elif sentiment[0] == "positive":
                score += 1
    return score


def get_dact_feedback_score_from_text_signal(textSignal: TextSignal):
    score = 0;
    negative = ['neg_answer', 'complaint', 'abandon', 'apology', 'respond_to_apology', 'non-sense', 'hold']
    positive = ['pos_answer', 'back-channeling', 'appreciation', 'thanking', 'respond_to_apology']
    dacts = get_dact_from_text_signal(textSignal)
    if dacts:
        for dac in dacts:
            if dac[0] in negative:
                score +=-1
            elif dac[0] in positive:
                score += 1
    return score

def get_dact_from_text_signal(textSignal: TextSignal):
    values = []
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type.endswith('DialogueAct'):
                values.append(annotation.value) #['value'])
    return values

def get_go_from_text_signal(textSignal: TextSignal):
    values = []
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            print(annotation)
            if annotation.type and annotation.type.endswith('Emotion') and annotation.value[1]=='GO':
                values.append(annotation.value) #['value'])
    return values


def get_ekman_from_text_signal(textSignal: TextSignal):
    values = []
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type.endswith('Emotion') and annotation.value[1]=='EKMAN':
                values.append(annotation.value)
    return values

def get_sentiment_from_text_signal(textSignal: TextSignal):
    values = []
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type.endswith('Emotion') and annotation.value[1]=='SENTIMENT':
                values.append(annotation.value)
    return values

def get_utterances_with_context_from_signals(signals: [], max_context=200):
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

def get_texts_from_utterances(utterances=[]):
    texts = []
    for utt in utterances:
        texts.append(utt[1])
    return texts