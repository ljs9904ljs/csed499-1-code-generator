integer dmaxloc_(double * w,integer s,integer e,integer * n), 
	    lm2;
    extern /* Subroutine */ int zunmbr_(char *, char *, integer *, integer *, 
	    integer *, doublereal *, integer *, doublereal *, integer *, 
	    doublereal *, integer *, doublereal *, integer *, integer *, 
	    doublereal *, doublereal *, integer *, integer *, integer *);
    integer ldwork, lwkmin;
    logical lquery;
    extern /* Subroutine */ int zunmbr_(char *, char *, char *, integer *, 
	    integer *, integer *, doublereal *, doublecomplex *, integer *,
	     doublecomplex *, integer *, doublecomplex *, integer *, integer *,
	    doublecomplex *, integer *, doublereal *, doublecomplex *, integer *,
	     integer *);
    logical lnoti;
    integer ldwork;
    extern /* Subroutine */ int zgeqrt_(integer *, integer *, doublecomplex *,
	     integer