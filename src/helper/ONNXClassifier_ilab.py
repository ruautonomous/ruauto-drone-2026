import onnxruntime as ort
import numpy as np

class ONNXClassifierWrapper:
    """
    A drop-in replacement for the TensorRTModel class, used for testing
    and simulation environments where .engine files cannot be used.
    
    (iLab Optimized Version: Configured to prevent CUDNN_STATUS_NOT_INITIALIZED 
    errors on shared GPU clusters).
    """

    def __init__(self, model_path: str):
        print(f"[ONNX Wrapper] Loading classifier model from {model_path}...")

        # 1. Create a configuration dictionary for the GPU with safe memory limits
        cuda_options = {
            "device_id": 0,
            "arena_extend_strategy": "kNextPowerOfTwo", # Safer memory allocation
            "cudnn_conv_algo_search": "DEFAULT",        # Stops cuDNN from benchmarking algorithms
            "cudnn_conv_use_max_workspace": "0"         # Prevents cuDNN from hogging all VRAM
        }

        # 2. Pass the options into the provider list (GPU first, CPU fallback)
        providers = [
            #('CUDAExecutionProvider', cuda_options),
            'CPUExecutionProvider'
        ]

        try:
            # We also pass a session options object to prevent graph optimization memory spikes
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
            
            self.session = ort.InferenceSession(model_path, sess_options=sess_options, providers=providers)
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