from typing import Callable, Any

# from pytube import YouTube
from urllib.parse import urlunsplit, urlencode
from pydantic.dataclasses import dataclass
import dataclasses

# import libraries
from vidgear.gears import CamGear
import cv2
import numpy as np

class Config:
    arbitrary_types_allowed = True

face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
person_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")

@dataclasses.dataclass(slots=True)
class ProcessedImage:
    image: np.array
    object_name: str
    object_bounding_boxes: list[tuple]
    detector_name: str
    metadata: dict[str, Any]

class BaseObjectDetector:
    detector_name: str = None
    target_object_name: str = None

    def process(self, image: np.array) -> ProcessedImage:
        """Returns processed image and metadata dict"""
        pass

@dataclass
class PersonHAARClassifier(BaseObjectDetector):
    detector_name = "haar_classifier"
    target_object_name = "person"

    def process(self, image: np.array) -> ProcessedImage:
        """Returns processed image and metadata dict"""
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Getting corners around the face
        # 1.3 = scale factor, 5 = minimum neighbor can be detected
        objs = person_classifier.detectMultiScale(img_gray, 1.05, 3)  

        # drawing bounding box around face
        for (x, y, w, h) in objs:
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255,   0), 3)

        # displaying image with bounding box
        # cv2.imshow('face_detect', img)
        return ProcessedImage(
                        image=image,
                        object_name=self.target_object_name,
                        object_bounding_boxes=[(x, y, w, h) for (x, y, w, h) in objs], 
                        detector_name=self.detector_name,
                        metadata={}
                    )

@dataclass(config=Config)
class VideoStream:
    streaming_service: str
    video_id: str
    capture_fps: float
    url: str = None
    stream: CamGear = None
    object_detectors: list[BaseObjectDetector] = None

    def __post_init__(self):
        base_url = "http://youtube.com"

        params = {'v': self.video_id,}
        self.url = f'{base_url}/watch?{urlencode(params)}'
        self._init_stream()

        

    def _init_stream(self):
        self.stream = CamGear(
                source=self.url,  
                stream_mode = True,
                # backend=cv2.CAP_GSTREAMER 
                # logging=True
            )
        
    #TODO make async
    # @staticmethod
    def process_frame(self, frame) -> list[ProcessedImage]:
        processed_frames = [
            detector.process(frame) 
            for detector in self.object_detectors
        ]

        return processed_frames

        

    def start_stream(self):
        self.stream.start()

        while True:
            # read frame
            frame = self.stream.read()

            # check if frame is None
            if frame is None:
                break
            
            # do something with frame here
            processed_frames = self.process_frame(frame)
            
            # cv2.imshow("Output Frame", processed_frame)
            cv2.imshow(processed_frames[0].detector_name, processed_frames[0].image)

            cv2.waitKey(int(1e3/self.capture_fps)) #

    def stop_stream(self):
        self.stream.stop()

    def __enter__(self):
        self.start_stream()
    
    def __exit__(self):
        self.stop_stream()



video_ids = [
    # "DHUnz4dyb54",
    "w_DfTc7F5oQ"
]

for video_id in video_ids:
    stream = VideoStream(
        streaming_service="youtube",
        video_id=video_id,
        capture_fps=24.0,
        object_detectors=[PersonHAARClassifier]
    )

    try:
        stream.start_stream()
    except Exception as e:
        raise e
    finally:
        stream.stop_stream()

cv2.destroyAllWindows()