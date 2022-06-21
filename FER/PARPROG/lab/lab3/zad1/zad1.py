import numpy
import pyopencl as cl
import time
import sys

G = 2 ** 16
L = 2 ** 9
N = 2 ** 26


def find_prime_numbers():
    print('load program from cl source file')
    f = open('kernel.cl', 'r', encoding='utf-8')
    kernels = ''.join(f.readlines())
    f.close()

    print('prepare data ... ')
    start_time = time.time()
    # matrix = numpy.random.randint(low=1, high=101, dtype=numpy.int32, size=G)
    # matrix = numpy.array([i+1 for i in range(N)])  # matrica koju treba provjeriti
    matrix = numpy.arange(2, N + 1).astype(numpy.int32)
    print(matrix)
    final = numpy.zeros(1, dtype=numpy.int32)
    time_hostdata_loaded = time.time()

    print('create context')
    ctx = cl.create_some_context()
    print('create command queue')
    queue = cl.CommandQueue(ctx, properties=cl.command_queue_properties.PROFILING_ENABLE)
    time_ctx_queue_creation = time.time()

    # prepare device memory for OpenCL
    print('prepare device memory for input / output')
    dev_matrix = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=matrix)
    dev_final = cl.Buffer(ctx, cl.mem_flags.READ_WRITE, final.nbytes)
    time_devicedata_loaded = time.time()
    # dev_final = numpy.int32(0)

    print('compile kernel code')
    prg = cl.Program(ctx, kernels).build()
    time_kernel_compilation = time.time()

    print('execute kernel programs')
    evt = prg.primes_atomic(queue, (G,), (L,), dev_matrix, numpy.int32(len(matrix)), dev_final)
    print('wait for kernel executions')
    evt.wait()

    cl.enqueue_copy(queue, final, dev_final).wait()

    elapsed = 1e-9 * (evt.profile.end - evt.profile.start)
    print("***** Number of Primes Numbers: ", final)
    print('done')

    print('Prepare host data took       : {}'.format(time_hostdata_loaded - start_time))
    print('Create CTX/QUEUE took        : {}'.format(time_ctx_queue_creation - time_hostdata_loaded))
    print('Upload data to device took   : {}'.format(time_devicedata_loaded - time_ctx_queue_creation))
    print('Compile kernel took          : {}'.format(time_kernel_compilation - time_devicedata_loaded))
    print('OpenCL elapsed time          : {}'.format(elapsed))


if __name__ == '__main__':
    print("running main...")
    find_prime_numbers()
