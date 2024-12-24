from app.file_by_chunks_consumer.video_consumer import video_consumer

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
     style="{",
     datefmt="%Y-%m-%d %H:%M",
 )

video_consumer()
