import dataclasses
from typing import List, Dict, Any
import numpy as np
import base64
import json
import io
import cv2
import fastavro

from .avro_schemas import raw_image_avro_schema, processed_image_avro_schema
from .detectors import  (
    BaseObjectDetector, 
    HAARClassifier, 
    YOLOv3Detector, 
    # FasterRCNNMobileNetDetector
)
DETECTORS = [
    # HAARClassifier(), 
    YOLOv3Detector(),
    # FasterRCNNMobileNetDetector()
]

@dataclasses.dataclass #(slots=True)
class ProcessedImage:
    source_name: str
    video_stream_id: str
    frame_ts: str
    image: np.array
    object_name: str
    object_bounding_boxes: List[tuple]
    detector_name: str
    detector_version: str
    id: str
    metadata: Dict[str, Any]

    def to_jpeg_base64(self) -> str:
        jpeg_bytes = self.to_jpeg_bytes()
        return base64.b64encode(jpeg_bytes).decode('ascii')

    def to_jpeg_bytes(self):
        success, encoded_image = cv2.imencode('.jpeg', self.image)
        jpeg_bytes = encoded_image.tobytes()
        return jpeg_bytes

    def to_record(self):
        return {
            "source_name": self.source_name,
            "video_stream_id": self.video_stream_id,
            "frame_ts": self.frame_ts,
            "detector_name": self.detector_name,
            "detector_version": self.detector_version,
            "object_name": self.object_name,
            "object_bounding_boxes_json": json.dumps(self.object_bounding_boxes),
            "metadata_json": json.dumps(self.metadata),
            "jpeg_image": b'' #self.to_jpeg_bytes() #Remove image data froms tream for performance
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_record())
    
    def to_avro(self) -> bytes:
        bytes_writer = io.BytesIO()
        img_dict = self.to_record()
        fastavro.writer(bytes_writer, 
                        schema=processed_image_avro_schema, 
                        records=[img_dict]
        )
        return bytes_writer.getvalue()
    

    
@dataclasses.dataclass
class RawImageRecord:
    id: str
    source_name: str
    video_stream_id: str
    frame_ts: str
    jpeg_image: bytes
    metadata_json: str
    object_detectors: List[BaseObjectDetector] = dataclasses.field(default_factory=lambda: DETECTORS) 

    @staticmethod
    def from_avro(id, avro_bytes) -> "RawImageRecord":
        with io.BytesIO(avro_bytes) as bytes_io:
            reader = fastavro.reader(bytes_io, raw_image_avro_schema)
            messages = [msg for msg in reader]
        assert len(messages) == 1
        message = messages[0]
    
        return RawImageRecord(
            id=id,
            **message
        )

    def process_image(self) -> List[ProcessedImage]:
        
        image: np.array = cv2.imdecode(
            np.frombuffer(self.jpeg_image, np.uint8),
            cv2.IMREAD_COLOR
        )

        processed_images = []
        for detector in self.object_detectors:
            image_attributes = {
                "source_name": self.source_name,
                "video_stream_id": self.video_stream_id, 
                "frame_ts": self.frame_ts,
                "metadata": {},
                "id": f"{self.id}_{detector.detector_name}_{detector.target_object_name}"
            }
            images = detector.process(image, **image_attributes)

            for img in images:
                processed_images.append(
                    img
                )

        return processed_images