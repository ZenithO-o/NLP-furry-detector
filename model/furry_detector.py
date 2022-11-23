from pathlib import Path
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from tensorflow.keras import Model
from typing import Any

class FurryDetector:
    """Keras model wrapper class for the Furry Detector model"""
    
    def __init__(self) -> None:
        """Create new model instance of Furry Detector model
        
        The Furry Detector model works by first recieving an input of the 
        frequency of "furry words" used in text. While this class does not 
        innately have this function. The file `parser.py` contains helper
        functions that you can use to make input easier.
        
        Once given this vector space of words used, the Keras model is then ran
        on it to give a final "confidence" score that the text the model was 
        ran on was written by a furry.
        """
        main_dir = Path(__file__).parent
        self._model_dir = main_dir / 'model_data'
        self.model = self._load_model()
        
    def _load_model(self) -> Model:
        """Helper function for loading json and h5 savefiles of the furry model
        into an uncompiled Keras model.

        Returns:
            model: Keras model of 'Furry Detector' model
        """
        with open(self._model_dir / 'model.json') as json_file:
            data = json_file.read()

        loaded_model = model_from_json(data)
        
        loaded_model: Model # type hinting for IDE
        loaded_model.load_weights(self._model_dir / 'model.h5')
        
        return loaded_model
    
    def run(self, input_arr: Any) -> float:
        """Executes the Furry Detector model on the given input.
        
        If needed, converts `input_arr` into a `Tensor` before running. For
        simplities sake, the output value is converted back into a python
        float.

        Args:
            input_arr (Any): An array of floating point values consisting of
            the frequency of "furry words" used.

        Returns:
            float: The confidence score of the model based on the input word
            frequency vector.
        """
        if not isinstance(input_arr, tf.Tensor):
            input_arr = tf.convert_to_tensor(input_arr)
        
        # model expects batch input, reshape to fit
        input_arr = input_arr[tf.newaxis, ...]
        
        # prediction = value of batch 0, output 0
        prediction = self.model.predict(input_arr)[0][0]
        
        return float(prediction)