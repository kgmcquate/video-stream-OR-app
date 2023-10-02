from confluent_kafka import Consumer, Producer, TopicPartition, KafkaException, KafkaError

from fastavro.types import AvroMessage
import fastavro
import io

from classifiers import ProcessedImage, RawImageRecord

from dataclasses import dataclass

from typing import Any, Dict


def log_kafka_message_delivery(err, msg):
    """ Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()}. Partition: [{msg.partition()}]')


@dataclass
class ImageStreamProcessor:
    src_topic: str
    src_partition: int
    src_avro_schema: fastavro.types.Schema
    tgt_topic: str
    # tgt_partition: int
    tgt_avro_schema: fastavro.types.Schema
    kafka_config: Dict[str, str]
    poll_period_seconds: float = 1.0

    def __post_init__(self):
        self.consumer = Consumer(self.kafka_config)
        # self.consumer.subscribe(self.topic)
        
        self.consumer.assign([
            TopicPartition(
                self.src_topic,
                self.src_partition
            )
        ])

        self.producer = Producer(self.kafka_config)


    def _consume(self):
    
        while True:
            msg = self.consumer.poll(timeout=self.poll_period_seconds)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    print(f'{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}')
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                proccessed_images = self.process_message(msg)
                self.write_processed_images(proccessed_images)
                

    def consume(self):
        try:
            self._consume()
        except Exception as e:
            raise Exception(f"Error occurred while running Kafka Consumer. topic: {self.src_topic} partition: {self.src_partition} ", e)
        finally:
            self.consumer.close()
            self.producer.flush()

    
    def process_message(self, msg) -> list[ProcessedImage]:
    
        records = self.deserialize_avro(
            msg.value()
        )
        assert len(records) <= 1
        record = records[0]
        
        image = RawImageRecord(id=msg.key(), **record)
        processed_images = image.process_image()

        return processed_images
       
        # display(Image.fromarray(processed_images[0].image))
        # print(len(processed_images[0].object_bounding_boxes))

    def write_processed_images(self, processed_images: list[ProcessedImage]):
        for img in processed_images:
            avro_bytes = self.serialize_avro([img.to_record()])

            self.producer.produce(
                topic=self.tgt_topic,
                value=avro_bytes,
                key=img.id,
                on_delivery=log_kafka_message_delivery
            )
    
        # producer.flush()
    
        # producer.poll(0)

    
    def serialize_avro(self, objs: list) -> bytes:
        bytes_writer = io.BytesIO()
    
        fastavro.writer(bytes_writer, 
                        schema=self.tgt_avro_schema, 
                        records=objs
        )

        return bytes_writer.getvalue()
        

    def deserialize_avro(self, avro_bytes: bytes) -> list[AvroMessage]:
        with io.BytesIO(avro_bytes) as bytes_io:
            reader = fastavro.reader(bytes_io, self.src_avro_schema)
            return [msg for msg in reader]

