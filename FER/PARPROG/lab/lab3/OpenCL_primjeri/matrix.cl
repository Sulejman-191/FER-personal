

// jednostavna inacica
kernel void matrix(global const double *A, global const double *B, global double *C, const int N) 
{
	int gx = get_global_id(0); // stupci (x smjer)
	int gy = get_global_id(1); // retci (y smjer)
	double sum = 0;
	for (int i = 0; i < N; i++) {
		double tempA = A[gy * N + i];
		double tempB = B[i * N + gx];
		sum += tempA * tempB;
	}
	C[gy * N + gx] = sum;
}


#define BLOCKSIZE 32 // mora biti poznato u trenutku prevodenja 
// radi samo za kvadratne matrice gdje je dimenzija matrice visekratnik velicine bloka
kernel void matrix2(global const double *A, global const double *B, global double *C, const int N)
{
	uint lx = get_local_id(0);	// stupac unutar bloka
	uint ly = get_local_id(1);	// redak unutar bloka
	uint gx = get_group_id(0);
	uint gy = get_group_id(1);
	uint n = get_num_groups(0); // broj grupa (blokova) u jednom retku/stupcu

	// posmak za pocetak bloka u izvornim matricama
	uint iSubA = BLOCKSIZE * gy * N;
	uint iSubB = BLOCKSIZE * gx;
	// lokalna memorija za pohranjivanje blokova
	local double tA[BLOCKSIZE][BLOCKSIZE];
	local double tB[BLOCKSIZE][BLOCKSIZE];

	double sum = 0;
	for (int i = 0; i < n; i++) {
		// kopiraju se blokovi matrica iz globalne memorije u lokalnu memoriju
		tA[ly][lx] = A[ly*N + lx + (iSubA + i* BLOCKSIZE)];
		tB[ly][lx] = B[ly*N + lx + (iSubB + i* BLOCKSIZE * N)];

		// sinkroniziraju se sve dretve u grupi!
		barrier(CLK_LOCAL_MEM_FENCE);

		// mnozenje dva bloka
		for (int k = 0; k < BLOCKSIZE; k++) {
			sum += tA[ly][k] * tB[k][lx];
		}
	}

	// pohrana u globalnu mem
	int globalIdx = get_global_id(0);
	int globalIdy = get_global_id(1);
	C[globalIdy * N + globalIdx] = sum;
}