import pandas as pd
import joblib
import os

RULES_FILE = 'location_rules.joblib'

def prepare_training_data(raw_events):
    df = pd.DataFrame(raw_events)

    unique_data = sorted(df['location'].unique().tolist())

    mapping = {town: i for i, town in enumerate(unique_data)}
    reverse_mapping = {i: town for town, i in mapping.items()}

    joblib.dump({'forward': mapping, 'backward': reverse_mapping}, RULES_FILE)

    df['location_id'] = df['location'].map(mapping)

    return df[['location_id', 'fatalities']]


def get_prediction_town(predicted_data):
    if not os.path.exists(RULES_FILE):
        return "Rules file missing"
    
    rules = joblib.load(RULES_FILE)

    return rules['backward'].get(predicted_data, "Unknown Location")