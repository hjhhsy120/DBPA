import os
import json
import numpy as np

def loadCausalModels_NotCombiner(model_directory):
    models = []
    for file in os.listdir(model_directory):
        modelFile = file
        # print("modelFile",modelFile)
        with open(model_directory + '/' + modelFile) as f:
            if ".txt" in modelFile:
                model = json.load(f)
        # print("model",model)
            models.append(model)
        # print("models", models)
    return models