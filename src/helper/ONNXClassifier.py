import onnxruntime as ort
import numpy as np


class ONNXClassifierWrapper:
    """
    A drop-in replacement for the TensorRTModel class, used for testing
    and simulation environments where .engine files cannot be used.
    """

    def __init__(self, model_path: str):
        print(f"[ONNX Wrapper] Loading classifier model from {model_path}...")

        # Define execution providers. It will try CUDA (GPU) first,
        # and seamlessly fall back to CPU if no GPU is available on your dev machine.
        providers = ['CPUExecutionProvider']

        try:
            self.session = ort.InferenceSession(model_path, providers=providers)
        except Exception as e:
            raise RuntimeError(f"Failed to load ONNX model: {e}")

        # Dynamically grab the input and output node names from the model
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        # Log the expected input shape so you can debug preprocessing issues if they arise
        expected_shape = self.session.get_inputs()[0].shape
        print(f"[ONNX Wrapper] Model loaded. Expected input shape: {expected_shape}")

    def predict(self, input_tensor: np.ndarray) -> np.ndarray:
        """
        Runs inference on the preprocessed image tensor.
        Expects the exact same input_tensor format that your TensorRT model uses
        (usually a numpy array of shape [1, Channels, Height, Width] in float32).
        """
        # ONNX typically expects float32
        if input_tensor.dtype != np.float32:
            input_tensor = input_tensor.astype(np.float32)

        # Ensure the tensor is contiguous in memory (prevents subtle C++ backend crashes)
        if not input_tensor.flags['C_CONTIGUOUS']:
            input_tensor = np.ascontiguousarray(input_tensor)

        # Run the model
        outputs = self.session.run([self.output_name], {self.input_name: input_tensor})

        # outputs[0] contains the batch predictions, e.g., shape (1, num_classes)
        # We return it exactly as the TensorRT model would.
        return outputs[0]