import dataclasses
import io
import fastavro

from .avro_schemas import processed_image_avro_schema

@dataclasses.dataclass #(slots=True)
class ProcessedImageRecord:
    source_name: str
    video_stream_id: str
    frame_ts: str
    detector_name: str
    detector_version: str
    object_name: str
    object_bounding_boxes_json: str
    metadata_json: str
    jpeg_image: bytes


    @staticmethod
    def from_avro(avro_bytes):
        with io.BytesIO(avro_bytes) as bytes_io:
            reader = fastavro.reader(bytes_io, processed_image_avro_schema)
            messages = [msg for msg in reader]
        assert len(messages) == 1
        message = messages[0]
    
        return ProcessedImageRecord(**message)