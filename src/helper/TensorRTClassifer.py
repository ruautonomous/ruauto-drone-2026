
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import numpy as np
import cv2

class TensorRTModel:
    def __init__(self, engine_path):
        # 1. Setup the TensorRT logger
        self.logger = trt.Logger(trt.Logger.WARNING)

        # 2. Deserialize the engine
        with open(engine_path, "rb") as f, trt.Runtime(self.logger) as runtime:
            self.engine = runtime.deserialize_cuda_engine(f.read())

        self.context = self.engine.create_execution_context()

        # 3. Memory Allocation Setup
        self.inputs = []
        self.outputs = []
        self.bindings = []
        self.stream = cuda.Stream()

        # Loop through all input and output tensors
        for i in range(self.engine.num_io_tensors):
            tensor_name = self.engine.get_tensor_name(i)
            shape = self.engine.get_tensor_shape(tensor_name)
            dtype = trt.nptype(self.engine.get_tensor_dtype(tensor_name))

            # Calculate total size of the tensor
            volume = abs(trt.volume(shape))  # abs() handles dynamic batch sizes (-1)

            # Allocate page-locked host memory and device memory
            host_mem = cuda.pagelocked_empty(volume, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)

            self.bindings.append(int(device_mem))

            # Determine if tensor is input or output
            if self.engine.get_tensor_mode(tensor_name) == trt.TensorIOMode.INPUT:
                self.inputs.append({'host': host_mem, 'device': device_mem, 'name': tensor_name})
            else:
                self.outputs.append({'host': host_mem, 'device': device_mem, 'name': tensor_name})

    def predict(self, input_image):
        """
        Executes inference on a single input image/array.
        Make sure input_image is a flattened numpy array that matches your model's expected shape and dtype.
        """
        # 1. Copy the input data into the host memory buffer
        np.copyto(self.inputs[0]['host'], input_image.ravel())

        # 2. Transfer input data to the GPU (Host to Device)
        cuda.memcpy_htod_async(self.inputs[0]['device'], self.inputs[0]['host'], self.stream)

        # 3. Set tensor addresses and run inference
        for i in range(self.engine.num_io_tensors):
            self.context.set_tensor_address(self.engine.get_tensor_name(i), self.bindings[i])

        self.context.execute_async_v3(stream_handle=self.stream.handle)

        # 4. Transfer predictions back to the CPU (Device to Host)
        for out in self.outputs:
            cuda.memcpy_dtoh_async(out['host'], out['device'], self.stream)

        # 5. Synchronize the stream to ensure completion
        self.stream.synchronize()

        # Return the output data (reshape it according to your classification classes)
        return [out['host'] for out in self.outputs]


def preprocess_image(img):
    img = cv2.resize(img, (224, 224))
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1)) # HWC to CHW
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

