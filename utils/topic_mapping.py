def map_topic_number_to_name(topic_number: int, topic_map: dict[int, str]) -> str:
    """
    Maps a BERTopic cluster number to a human-readable topic name.
    
    Args:
        topic_number (int): The topic number from the data (e.g. from 'bertopic').
        topic_map (dict[int, str]): Mapping from topicno2 to topic_name from CSV.
    
    Returns:
        str: Human-readable topic name if found, otherwise a fallback string.
    """
    return topic_map.get(topic_number, f"Unknown topic {topic_number}")
