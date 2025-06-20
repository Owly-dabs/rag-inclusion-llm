from pathlib import Path
from utils.topic_mapping import map_topic_number_to_name
from flows.explanation_flow import load_topic_map

MAPTOPIC_PATH = Path("data/maptopics.csv")

def test_mapping_with_real_csv():
    # Load topic map using actual task
    topic_map = load_topic_map()  # Call task and unwrap result

    # Pick a few known topic numbers from your CSV for validation
    print("Sample topic mapping:")
    for key in list(topic_map.keys())[:5]:  # show first 5
        print(f"{key}: {map_topic_number_to_name(key, topic_map)}")

    # Spot-check one known entry if you know it
    assert isinstance(topic_map, dict)
    assert len(topic_map) > 0

    known_topic = next(iter(topic_map.keys()))
    assert map_topic_number_to_name(known_topic, topic_map) == topic_map[known_topic]

    print("✅ Real CSV topic mapping works correctly.")

if __name__ == "__main__":
    test_mapping_with_real_csv()