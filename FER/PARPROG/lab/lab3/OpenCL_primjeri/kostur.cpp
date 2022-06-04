#include<iostream>
#include<fstream>
#include<string>
#include<sstream>
#include <CL/cl.hpp>
//#include <boost/compute/cl.hpp>

char SOURCE_FILE[] = "../primjeri.cl";
char KERNEL_NAME[] = "get_arg";
const int N = 1024;


int main()
{
	std::ifstream sourceFile(SOURCE_FILE);
	std::stringstream sourceString;
	sourceString << sourceFile.rdbuf();
	std::string ss1 = sourceString.str();
	const char* ss2 = ss1.c_str();
	const char** source = &ss2;

	cl_platform_id platform;
	clGetPlatformIDs(1, &platform, NULL); 

	cl_device_id device;
	clGetDeviceIDs(platform, CL_DEVICE_TYPE_GPU, 1, &device, NULL);

	cl_context context = clCreateContext(NULL, 1, &device, NULL, NULL, NULL);

	cl_program program = clCreateProgramWithSource(context, 1, source, NULL, NULL);

	clBuildProgram(program, 1, &device, NULL, NULL, NULL);

	cl_kernel kernel = clCreateKernel(program, KERNEL_NAME, NULL);

	cl_command_queue queue = clCreateCommandQueue(context, device, 0, NULL);

	int arg1[N];
	cl_mem cl_arg1 = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, sizeof(int) * N, arg1, NULL);

	clSetKernelArg(kernel, 0, sizeof(cl_mem), (void *)&cl_arg1);

	cl_uint dim = 2;
	size_t global_offset[] = { 0 };
	size_t global_size[] = { 32, 1 };
	size_t local_size[] = { 1, 1 };
	clEnqueueNDRangeKernel(queue, kernel, dim, global_offset, global_size, local_size, NULL, NULL, NULL);

	clFinish(queue);

	clEnqueueReadBuffer(queue, cl_arg1, CL_TRUE, 0, N * sizeof(int), arg1, NULL, NULL, NULL);

	// pocisti
	clReleaseKernel(kernel);
	clReleaseProgram(program);
	clReleaseContext(context);
	clReleaseCommandQueue(queue);

	return 0;
}