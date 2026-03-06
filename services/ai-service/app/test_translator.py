from translator_utils import prepare_training_data, get_prediction_town

mock_data = [
    {"location": "Bor", "fatalities": 25},
    {"location": "Yambio", "fatalities": 1},
    {"location": "Udier", "fatalities": 21}
]

print("Serialization")

numeric_df = prepare_training_data(mock_data)

print("Numeric Table for AI:")
print(numeric_df)

print("\nRunning Deserialization")

test_id = 0 
town_name = get_prediction_town(test_id)

print(f"The AI predicted ID {test_id}. Translator says this is: {town_name}")

if town_name == "Bor":
    print("\nSUCCESS: The mapping is correct!")