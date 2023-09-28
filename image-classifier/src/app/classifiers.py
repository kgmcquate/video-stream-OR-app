import cv2
import dataclasses
from typing import Any
import numpy as np

face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")



@dataclasses.dataclass(slots=True)
class ProcessedImage:
    image: np.array
    object_name: str
    object_bounding_boxes: list[tuple]
    detector_name: str
    metadata: dict[str, Any]

    def to_jpeg(self) -> bytes:
        success, encoded_image = cv2.imencode('.jpeg', self.image)
        jpeg_bytes = encoded_image.tobytes()
        return jpeg_bytes


class BaseObjectDetector:
    bounding_box_color: tuple[int]
    detector_name: str = None
    target_object_name: str = None

    def process(self, image: np.array) -> ProcessedImage:
        """Returns processed image and metadata dict"""
        pass

@dataclasses.dataclass
class HAARClassifier(BaseObjectDetector):
    bounding_box_color: tuple[int, int, int] = (255, 0, 0)
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
                        object_bounding_boxes=[(x, y, w, h) for (x, y, w, h) in objs], 
                        detector_name=self.detector_name,
                        metadata={}
                    )
    


@dataclasses.dataclass
class RawImageRecord:
    video_stream_id: str
    jpeg_image: bytes
    metadata_json: str
    object_detectors: list[BaseObjectDetector] = [HAARClassifier()]

    def process_image(self) -> list[ProcessedImage]:
        
        
        image = cv2.imdecode(
            np.frombuffer(self.jpeg_image, np.uint8),
            cv2.IMREAD_COLOR
        )

        processed_images = []
        for detector in self.object_detectors:
            processed_images.append(
                detector.process(image)
            )

        return processed_images