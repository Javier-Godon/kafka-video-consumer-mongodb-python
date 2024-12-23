from kafka import KafkaConsumer

from app.configuration.configuration import get_data


def get_video_stream():
    consumer = KafkaConsumer(
        bootstrap_servers=get_data()['kafka']['consumer']['bootstrap-servers']
        # group_id='videoProcessor',
        # auto_offset_reset=get_data()['kafka']['file_by_chunks_consumer']['auto-offset-reset']
    )
    consumer.subscribe(topics=[get_data()['kafka']['topics']['streaming']])
    for msg in consumer:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpg\r\n\r\n' + msg.value + b'\r\n\r\n')
