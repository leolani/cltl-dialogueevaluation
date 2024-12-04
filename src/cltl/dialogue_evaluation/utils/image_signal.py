from emissor.representation.scenario import ImageSignal




def make_annotation_label (signal):
    label = ""
    face = get_face_for_image_signal(signal)
    object = get_object_for_image_signal(signal)
    id = get_identity_for_image_signal(signal)
    if face:
        label += face+";"
    if object:
        label += object+";"
    return object, face, id


def get_face_for_image_signal(imageSignal: ImageSignal):
    label = ""
    mentions = imageSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'Face':
                age = annotation.value.age
                gender = annotation.value.gender
                if not gender in label:
                    label += gender+"-"
                if not str(age) in label:
                    label+= str(age)
                return label
    return label

def get_object_for_image_signal(imageSignal: ImageSignal):
    label = ""
    mentions = imageSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'python-type:cltl.object_recognition.api.Object':
                object = annotation.value.label
                conf = annotation.value.confidence
                if not object in label:
                    label += object+"-"+str(round(conf, 2))
            elif annotation.type == 'ObjectType':
                object = annotation.value
                if not object in label:
                    label += object
    return label

def get_identity_for_image_signal(imageSignal: ImageSignal):
    label = ""
    mentions = imageSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'VectorIdentity':
                id = annotation.value
                if not id in label:
                    label = id
            elif annotation.type == 'ObjectIdentity':
                id = annotation.value
                if not id in label:
                    label = id
    return label
