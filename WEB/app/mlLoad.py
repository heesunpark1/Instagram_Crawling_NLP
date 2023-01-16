import os
import json
from django.conf import settings
import numpy as np
import fasttext



def init():
    mod_load_path = os.path.join(settings.MODEL_DIR, settings.MODEL_FILENAME)

    model = fasttext.load_model(mod_load_path)
    print("Loaded Model from disk")

    return model