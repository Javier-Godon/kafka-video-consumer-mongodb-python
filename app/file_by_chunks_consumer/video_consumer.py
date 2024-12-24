import json
from collections import namedtuple

from kafka import KafkaConsumer

from app.configuration.configuration import get_data
from app.configuration.database_connection import MongoConnection
from app.file_by_chunks_consumer.domain.video_data import VideoData


def video_consumer():
    config = get_data()
    print("Loaded configuration:", config)
    consumer = KafkaConsumer(
        bootstrap_servers=get_data()['kafka']['consumer']['bootstrap-servers'],
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        # group_id='videoProcessor',
        # auto_offset_reset=get_data()['kafka']['file_by_chunks_consumer']['auto-offset-reset']
    )

    mongodb_instance = MongoConnection().get_instance()
    collection = mongodb_instance['video']

    consumer.subscribe(topics=[get_data()['kafka']['topics']['processed']])
    for message in consumer:
        received_json_str = json.dumps(message.value)
        received_json = json.loads(received_json_str)
        video_data: VideoData = namedtuple("VideoData", received_json.keys())(*received_json.values())
        # video_data = VideoData.from_json(received_json)
        # json_str = json.dumps(video_data.__dict__)
        collection.insert_one(received_json)

        print(f'receiving video chunk: {video_data.chunk_index} from: {video_data.element_alias}')
