from typing import Dict, List, Tuple, Any
import numpy as np
import os

model_files_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__))
    , "model_files")

class BaseObjectDetector:
    bounding_box_color: Tuple[int]
    detector_name: str = None
    detector_version: str = None
    target_object_name: str = None

    def process(self, image: np.array, **kwargs) -> List["ProcessedImage"]:
        """Returns processed image and metadata dict"""
        pass


# @dataclass
# class TorchVisionModel(BaseObjectDetector):
#     bounding_box_color: Tuple[int, int, int] = (0, 255)
#     detector_name: str = None
#     detector_version: str = None

#     model_init_function: Callable[[], torchvision.models.detection.faster_rcnn.FasterRCNN]
#     model_weights: torchvision.models.detection.WeightsEnum