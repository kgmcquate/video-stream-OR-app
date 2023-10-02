import cv2
import dataclasses
from typing import Dict, List, Tuple, Any
import numpy as np
import base64
import json


face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


@dataclasses.dataclass #(slots=True)
class ProcessedImage:
    image: np.array
    object_name: str
    object_bounding_boxes: List[tuple]
    detector_name: str
    id: str = None
    metadata: Dict[str, Any] = None
    video_stream_id: str = None

    def to_jpeg_base64(self) -> str:
        jpeg_bytes = self.to_jpeg_bytes()
        return base64.b64encode(jpeg_bytes).decode('ascii')

    def to_jpeg_bytes(self):
        success, encoded_image = cv2.imencode('.jpeg', self.image)
        jpeg_bytes = encoded_image.tobytes()
        return jpeg_bytes

    def to_record(self):
        return {
            "video_stream_id": self.video_stream_id,
            "detector_name": self.detector_name,
            "object_name": self.object_name,
            "object_bounding_boxes_json": json.dumps(self.object_bounding_boxes),
            "metadata_json": json.dumps(self.metadata),
            "jpeg_image": self.to_jpeg_bytes()
        }
    
    def to_json(self):
        return json.dumps(self.to_record())

        

class BaseObjectDetector:
    bounding_box_color: Tuple[int]
    detector_name: str = None
    target_object_name: str = None

    def process(self, image: np.array) -> ProcessedImage:
        """Returns processed image and metadata dict"""
        pass

@dataclasses.dataclass
class HAARClassifier(BaseObjectDetector):
    bounding_box_color: Tuple[int, int, int] = (255, 0, 0)
    detector_name: str = "haar_classifier"
    target_object_name: str = "person"
    haar_cascade_file: str = cv2.data.haarcascades + "haarcascade_fullbody.xml"

    def __post_init__(self):
        self.cv2_classifier = cv2.CascadeClassifier(self.haar_cascade_file)

    def process(self, image: np.array) -> ProcessedImage:
        """Returns processed image and metadata dict"""
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Getting corners around the face
        # 1.3 = scale factor, 5 = minimum neighbor can be detected
        objs = self.cv2_classifier.detectMultiScale(img_gray, 1.05, 3)  

        # drawing bounding box around face
        for (x, y, w, h) in objs:
            image = cv2.rectangle(image, (x, y), (x + w, y + h), self.bounding_box_color, 3)

        # displaying image with bounding box
        # cv2.imshow('face_detect', img)
        return ProcessedImage(
                        image=image,
                        object_name=self.target_object_name,
                        object_bounding_boxes=[(int(x), int(y), int(w), int(h)) for (x, y, w, h) in objs], 
                        detector_name=self.detector_name
                    )
    
DETECTORS = [HAARClassifier()]

@dataclasses.dataclass
class RawImageRecord:
    id: str
    video_stream_id: str
    jpeg_image: bytes
    metadata_json: str
    object_detectors: List[BaseObjectDetector] = dataclasses.field(default_factory=lambda: DETECTORS) 

    def process_image(self) -> List[ProcessedImage]:
        
        
        image = cv2.imdecode(
            np.frombuffer(self.jpeg_image, np.uint8),
            cv2.IMREAD_COLOR
        )

        processed_images = []
        for detector in self.object_detectors:
            processed_image = detector.process(image)
            processed_image.video_stream_id = self.video_stream_id
            processed_image.metadata = {}
            processed_image.id = f"{self.id}_{detector.detector_name}_{detector.target_object_name}"
            processed_images.append(
                processed_image
            )

        return processed_images