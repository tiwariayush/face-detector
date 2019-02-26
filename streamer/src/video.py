import numpy as np
import cv2


def compress(frame: np.array, compression_factor: float) -> np.array:
    """
    Compress the reference image can affect the efficiency of the matching
    :param compression_factor: if < 1 increase size else reduce size of image
    """
    compressed_shape = (
        int(frame.shape[1] / compression_factor),
        int(frame.shape[0] / compression_factor),
    )
    frame = cv2.resize(frame, compressed_shape)

    return frame
