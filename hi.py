import tensorflow as tf
import time

# Check if GPU is being used
print("Available GPUs:", tf.config.list_physical_devices('GPU'))

# Define a simple computation
matrix_size = 1000
a = tf.random.normal([matrix_size, matrix_size])
b = tf.random.normal([matrix_size, matrix_size])

# Perform the computation on GPU and measure time
start = time.time()
result = tf.matmul(a, b)
end = time.time()

print(f"Matrix multiplication on GPU took {end - start:.4f} seconds")

# Ensure the computation was performed on the GPU
if result.device.endswith('GPU:0'):
    print("Computation was performed on the GPU")
else:
    print("Computation was not performed on the GPU")
