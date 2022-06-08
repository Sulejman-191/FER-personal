#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <iostream>
#include <fstream>

#include "arraymalloc.h"
#include "boundary.h"
#include "jacobi.h"
#include "cfdio.h"

#include <CL/cl.hpp>
#include "timing.h"
using namespace cl;

char SOURCE_FILE[] = "jacobi.cl";
char KERNEL_NAME[] = "jacobistep";
int N = 1 << 20;
int L = 32;

int main(int argc, char **argv)
{
	int printfreq = 1000; // output frequency
	double error, bnorm;
	double tolerance = 0.0; // tolerance for convergence. <=0 means do not check

	// main arrays
	double *psi;
	// temporary versions of main arrays
	double *psitmp;

	// command line arguments
	int scalefactor, numiter;

	// simulation sizes
	int bbase = 10;
	int hbase = 15;
	int wbase = 5;
	int mbase = 32;
	int nbase = 32;

	int irrotational = 1, checkerr = 0;

	int m, n, b, h, w;
	int iter;
	int i, j;

	double tstart, tstop, ttot, titer;

	Clock clock;
	std::cout << "start..." << std::endl;
	clock.start();

	Program program; // izdvojeno zbog catch(...)

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
		{CL_CONTEXT_PLATFORM, (cl_context_properties)(platforms[0])(), 0};

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

	// std::cout << "Trajanje: " << clock.stop() << " s" << std::endl;

	// do we stop because of tolerance?
	if (tolerance > 0)
	{
		checkerr = 1;
	}

	// check command line parameters and parse them

	if (argc < 3 || argc > 4)
	{
		printf("Usage: cfd <scale> <numiter>\n");
		return 0;
	}

	scalefactor = atoi(argv[1]);
	numiter = atoi(argv[2]);

	if (!checkerr)
	{
		printf("Scale Factor = %i, iterations = %i\n", scalefactor, numiter);
	}
	else
	{
		printf("Scale Factor = %i, iterations = %i, tolerance= %g\n", scalefactor, numiter, tolerance);
	}

	printf("Irrotational flow\n");

	// Calculate b, h & w and m & n
	b = bbase * scalefactor;
	h = hbase * scalefactor;
	w = wbase * scalefactor;
	m = mbase * scalefactor;
	n = nbase * scalefactor;

	printf("Running CFD on %d x %d grid in serial\n", m, n);

	// allocate arrays
	psi = (double *)malloc((m + 2) * (n + 2) * sizeof(double));
	psitmp = (double *)malloc((m + 2) * (n + 2) * sizeof(double));

	// zero the psi array
	for (i = 0; i < m + 2; i++)
	{
		for (j = 0; j < n + 2; j++)
		{
			psi[i * (m + 2) + j] = 0.0;
		}
	}

	// set the psi boundary conditions
	boundarypsi(psi, m, n, b, h, w);

	// compute normalisation factor for error
	bnorm = 0.0;

	for (i = 0; i < m + 2; i++)
	{
		for (j = 0; j < n + 2; j++)
		{
			bnorm += psi[i * (m + 2) + j] * psi[i * (m + 2) + j];
		}
	}
	bnorm = sqrt(bnorm);

	// begin iterative Jacobi loop
	printf("\nStarting main loop...\n\n");
	tstart = gettime();

	for (iter = 1; iter <= numiter; iter++)
	{

		// Stvori buffer za input
		Buffer A = Buffer(context, CL_MEM_READ_ONLY | CL_MEM_COPY_HOST_PTR, (m + 2) * (n + 2) * sizeof(double), &psi[0]);
		// enqueueWriteBuffer nije potrebno ako smo maloprije stavili | CL_MEM_COPY_HOST_PTR:
		// queue.enqueueWriteBuffer(A, CL_TRUE, 0, N * sizeof(int), &a[0]);

		// Stvori buffer za rezultate
		Buffer B = Buffer(context, CL_MEM_WRITE_ONLY, (m + 2) * (n + 2) * sizeof(double));

		// Postavi argumente jezgrenih funkcija
		kernel.setArg(0, A);
		kernel.setArg(1, B);
		kernel.setArg(2, m);
		kernel.setArg(3, n);

		// Definiraj velicinu radnog prostora i radne grupe
		NDRange global(N, 1); // ukupni broj dretvi
		NDRange local(L, 1);  // velicina radne grupe

		// Pokreni jezgrenu funkciju
		queue.enqueueNDRangeKernel(kernel, NullRange, global, local);

		queue.finish();

		// Procitaj rezultat
		queue.enqueueReadBuffer(B, CL_TRUE, 0, (m + 2) * (n + 2) * sizeof(double), &psitmp[0]);

		// calculate psi for next iteration
		// jacobistep(psitmp, psi, m, n);

		// calculate current error if required
		if (checkerr || iter == numiter)
		{
			error = deltasq(psitmp, psi, m, n);

			error = sqrt(error);
			error = error / bnorm;
		}

		// quit early if we have reached required tolerance
		if (checkerr)
		{
			if (error < tolerance)
			{
				printf("Converged on iteration %d\n", iter);
				break;
			}
		}

		// copy back
		for (i = 1; i <= m; i++)
		{
			for (j = 1; j <= n; j++)
			{
				psi[i * (m + 2) + j] = psitmp[i * (m + 2) + j];
			}
		}

		// print loop information
		if (iter % printfreq == 0)
		{
			if (!checkerr)
			{
				printf("Completed iteration %d\n", iter);
			}
			else
			{
				printf("Completed iteration %d, error = %g\n", iter, error);
			}
		}
	} // iter

	if (iter > numiter)
		iter = numiter;

	tstop = gettime();

	ttot = tstop - tstart;
	titer = ttot / (double)iter;

	// print out some stats
	printf("\n... finished\n");
	printf("After %d iterations, the error is %g\n", iter, error);
	printf("Time for %d iterations was %g seconds\n", iter, ttot);
	printf("Each iteration took %g seconds\n", titer);

	// output results
	// writedatafiles(psi,m,n, scalefactor);
	// writeplotfile(m,n,scalefactor);

	// free un-needed arrays
	free(psi);
	free(psitmp);
	printf("... finished\n");

	return 0;
}

/*
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "arraymalloc.h"
#include "boundary.h"
#include "jacobi.h"
#include "cfdio.h"


int main(int argc, char **argv)
{
	int printfreq=1000; //output frequency
	double error, bnorm;
	double tolerance=0.0; //tolerance for convergence. <=0 means do not check

	//main arrays
	double *psi;
	//temporary versions of main arrays
	double *psitmp;

	//command line arguments
	int scalefactor, numiter;

	//simulation sizes
	int bbase=10;
	int hbase=15;
	int wbase=5;
	int mbase=32;
	int nbase=32;

	int irrotational = 1, checkerr = 0;

	int m,n,b,h,w;
	int iter;
	int i,j;

	double tstart, tstop, ttot, titer;

	//do we stop because of tolerance?
	if (tolerance > 0) {checkerr=1;}

	//check command line parameters and parse them

	if (argc <3|| argc >4) {
		printf("Usage: cfd <scale> <numiter>\n");
		return 0;
	}

	scalefactor=atoi(argv[1]);
	numiter=atoi(argv[2]);

	if(!checkerr) {
		printf("Scale Factor = %i, iterations = %i\n",scalefactor, numiter);
	}
	else {
		printf("Scale Factor = %i, iterations = %i, tolerance= %g\n",scalefactor,numiter,tolerance);
	}

	printf("Irrotational flow\n");

	//Calculate b, h & w and m & n
	b = bbase*scalefactor;
	h = hbase*scalefactor;
	w = wbase*scalefactor;
	m = mbase*scalefactor;
	n = nbase*scalefactor;

	printf("Running CFD on %d x %d grid in serial\n",m,n);

	//allocate arrays
	psi    = (double *) malloc((m+2)*(n+2)*sizeof(double));
	psitmp = (double *) malloc((m+2)*(n+2)*sizeof(double));

	//zero the psi array
	for (i=0;i<m+2;i++) {
		for(j=0;j<n+2;j++) {
			psi[i*(m+2)+j]=0.0;
		}
	}

	//set the psi boundary conditions
	boundarypsi(psi,m,n,b,h,w);

	//compute normalisation factor for error
	bnorm=0.0;

	for (i=0;i<m+2;i++) {
			for (j=0;j<n+2;j++) {
			bnorm += psi[i*(m+2)+j]*psi[i*(m+2)+j];
		}
	}
	bnorm=sqrt(bnorm);

	//begin iterative Jacobi loop
	printf("\nStarting main loop...\n\n");
	tstart=gettime();

	for(iter=1;iter<=numiter;iter++) {

		//calculate psi for next iteration
		jacobistep(psitmp,psi,m,n);

		//calculate current error if required
		if (checkerr || iter == numiter) {
			error = deltasq(psitmp,psi,m,n);

			error=sqrt(error);
			error=error/bnorm;
		}

		//quit early if we have reached required tolerance
		if (checkerr) {
			if (error < tolerance) {
				printf("Converged on iteration %d\n",iter);
				break;
			}
		}

		//copy back
		for(i=1;i<=m;i++) {
			for(j=1;j<=n;j++) {
				psi[i*(m+2)+j]=psitmp[i*(m+2)+j];
			}
		}

		//print loop information
		if(iter%printfreq == 0) {
			if (!checkerr) {
				printf("Completed iteration %d\n",iter);
			}
			else {
				printf("Completed iteration %d, error = %g\n",iter,error);
			}
		}
	}	// iter

	if (iter > numiter) iter=numiter;

	tstop=gettime();

	ttot=tstop-tstart;
	titer=ttot/(double)iter;

	//print out some stats
	printf("\n... finished\n");
	printf("After %d iterations, the error is %g\n",iter,error);
	printf("Time for %d iterations was %g seconds\n",iter,ttot);
	printf("Each iteration took %g seconds\n",titer);

	//output results
	//writedatafiles(psi,m,n, scalefactor);
	//writeplotfile(m,n,scalefactor);

	//free un-needed arrays
	free(psi);
	free(psitmp);
	printf("... finished\n");

	return 0;
}
*/