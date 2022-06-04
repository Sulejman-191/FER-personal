#define __CL_ENABLE_EXCEPTIONS
#include <CL/cl.hpp>
#include <utility>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include "timing.h"
using namespace cl;


char SOURCE_FILE[] = "primjeri.cl";
char KERNEL_NAME[] = "vektor";
int N = 1 << 20;
int L = 32;


int main(int argc, char** argv) 
{
	// argumenti
	std::vector<int> a(N, 1), b(N, 0);
	for (int i = 0; i < N; i++)
		//a[i] = rand();
		a[i] = i;

	Clock clock;
	std::cout << "start..." << std::endl;
	clock.start();

	Program program;	// izdvojeno zbog catch(...)
 
	try {
		// Ucitaj tekst programa
		std::ifstream sourceFile(SOURCE_FILE);
		std::string sourceCode(
			std::istreambuf_iterator<char>(sourceFile),
			(std::istreambuf_iterator<char>()));
		Program::Sources source(1, std::make_pair(sourceCode.c_str(), sourceCode.length() + 1));

		// Dostupne platforme
		std::vector<Platform> platforms;
		Platform::get(&platforms);

		// Odabir platforme i stvaranje konteksta
		cl_context_properties cps[3] = 
			{ CL_CONTEXT_PLATFORM, (cl_context_properties)(platforms[0])(), 0 };
		Context context(CL_DEVICE_TYPE_GPU, cps);

		// Popis OpenCL uredjaja
		std::vector<Device> devices = context.getInfo<CL_CONTEXT_DEVICES>();

		// Stvori naredbeni red za prvi uredjaj
		CommandQueue queue = CommandQueue(context, devices[0]);

		// Stvori programski objekt
		program = Program(context, source);

		// Prevedi programski objekt za zadani uredjaj
		program.build(devices);

		// Stvori jezgrene funkcije
		Kernel kernel(program, KERNEL_NAME);

		// Stvori buffer za input
		Buffer A = Buffer(context, CL_MEM_READ_ONLY | CL_MEM_COPY_HOST_PTR, N * sizeof(int), &a[0]);
		// enqueueWriteBuffer nije potrebno ako smo maloprije stavili | CL_MEM_COPY_HOST_PTR:
		//queue.enqueueWriteBuffer(A, CL_TRUE, 0, N * sizeof(int), &a[0]);

		// Stvori buffer za rezultate
		Buffer B = Buffer(context, CL_MEM_WRITE_ONLY, N * sizeof(int));

		// Postavi argumente jezgrenih funkcija
		kernel.setArg(0, A);
		kernel.setArg(1, B);
		kernel.setArg(2, N);
		
		// Definiraj velicinu radnog prostora i radne grupe
		NDRange global(N, 1);	// ukupni broj dretvi
		NDRange local(L, 1);	// velicina radne grupe

		// Pokreni jezgrenu funkciju
		queue.enqueueNDRangeKernel(kernel, NullRange, global, local);

		queue.finish();

		// Procitaj rezultat
		queue.enqueueReadBuffer(B, CL_TRUE, 0, N * sizeof(int), &b[0]);

		std::cout << "Trajanje: " << clock.stop() << " s" << std::endl;

	} catch(Error error) {
		std::cout << error.what() << "(" << error.err() << ")" << std::endl;
		std::cout << "Build Status: " << program.getBuildInfo<CL_PROGRAM_BUILD_STATUS>(cl::Device::getDefault()) << std::endl;
		std::cout << "Build Options:\t" << program.getBuildInfo<CL_PROGRAM_BUILD_OPTIONS>(cl::Device::getDefault()) << std::endl;
		std::cout << "Build Log:\t " << program.getBuildInfo<CL_PROGRAM_BUILD_LOG>(cl::Device::getDefault()) << std::endl;
	}

	return 0;
}
