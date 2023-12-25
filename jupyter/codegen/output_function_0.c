integer pow_ii(integer x,integer n){;
	integer pow;
		*(n!= 0) {
		integer pow;n!= 0) {
			if (n == 0 || x == 1) pow = 1;
			else if (x!= -1) pow = x == 0? 1/x : 0;
			else n = -n;
		}
		if ((n > 0) ||!(n == 0 || x == 1 || x!= -1)) {
			u = n;
			for(pow = 1; ; ) {
				if(u & 01) pow *= x;
				if(u >>= 1) x *= x;
				else break;
			}
		}
		return pow;
	}
}

static int dmaxloc_(double *w, integer s, integer e, integer *n)
{
	double m; integer i, mi;
	for(m=w[s-1], mi=s, i=s+1; i<=e; i++)
		if (w[i-1]>m) mi=i,m=w[i-1];
	return mi-s+
}

void print_hello(char* name) {
	printf("%s", name);
}