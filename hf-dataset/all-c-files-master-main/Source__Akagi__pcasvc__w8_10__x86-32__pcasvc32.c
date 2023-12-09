/*

File has been edited after MIDL compiler, changes:
1. XCFG BS removed
2. Warning supression added

*/

 /* File created by MIDL compiler version 8.01.0626 */
/* at Mon Jan 18 19:14:07 2038
 */
/* Compiler settings for pcasvc.idl:
    Oicf, W1, Zp8, env=Win32 (32b run), target_arch=X86 8.01.0626 
    protocol : dce , ms_ext, c_ext, robust
    error checks: allocation ref bounds_check enum stub_data 
    VC __declspec() decoration level: 
         __declspec(uuid()), __declspec(selectany), __declspec(novtable)
         DECLSPEC_UUID(), MIDL_INTERFACE()
*/
/* @@MIDL_FILE_HEADING(  ) */

#if !defined(_M_IA64) && !defined(_M_AMD64) && !defined(_ARM_)


#pragma warning( disable: 4049 )  /* more than 64k source lines */
#if _MSC_VER >= 1200
#pragma warning(push)
#endif

#pragma warning( disable: 4211 )  /* redefine extern to static */
#pragma warning( disable: 4232 )  /* dllimport identity*/
#pragma warning( disable: 4024 )  /* array to pointer mapping*/
#pragma warning( disable: 4100 ) /* unreferenced arguments in x86 call */

#pragma optimize("", off ) 

#include <string.h>

#include "pcasvc32.h"

#define TYPE_FORMAT_STRING_SIZE   7                                 
#define PROC_FORMAT_STRING_SIZE   71                                
#define EXPR_FORMAT_STRING_SIZE   1                                 
#define TRANSMIT_AS_TABLE_SIZE    0            
#define WIRE_MARSHAL_TABLE_SIZE   0            

typedef struct _pcasvc_MIDL_TYPE_FORMAT_STRING
    {
    short          Pad;
    unsigned char  Format[ TYPE_FORMAT_STRING_SIZE ];
    } pcasvc_MIDL_TYPE_FORMAT_STRING;

typedef struct _pcasvc_MIDL_PROC_FORMAT_STRING
    {
    short          Pad;
    unsigned char  Format[ PROC_FORMAT_STRING_SIZE ];
    } pcasvc_MIDL_PROC_FORMAT_STRING;

typedef struct _pcasvc_MIDL_EXPR_FORMAT_STRING
    {
    long          Pad;
    unsigned char  Format[ EXPR_FORMAT_STRING_SIZE ];
    } pcasvc_MIDL_EXPR_FORMAT_STRING;


static const RPC_SYNTAX_IDENTIFIER  _RpcTransferSyntax = 
{{0x8A885D04,0x1CEB,0x11C9,{0x9F,0xE8,0x08,0x00,0x2B,0x10,0x48,0x60}},{2,0}};

extern const pcasvc_MIDL_TYPE_FORMAT_STRING pcasvc__MIDL_TypeFormatString;
extern const pcasvc_MIDL_PROC_FORMAT_STRING pcasvc__MIDL_ProcFormatString;
extern const pcasvc_MIDL_EXPR_FORMAT_STRING pcasvc__MIDL_ExprFormatString;

#define GENERIC_BINDING_TABLE_SIZE   0            


/* Standard interface: PcaService, ver. 1.0,
   GUID={0x0767a036,0x0d22,0x48aa,{0xba,0x69,0xb6,0x19,0x48,0x0f,0x38,0xcb}} */



static const RPC_CLIENT_INTERFACE PcaService___RpcClientInterface =
    {
    sizeof(RPC_CLIENT_INTERFACE),
    {{0x0767a036,0x0d22,0x48aa,{0xba,0x69,0xb6,0x19,0x48,0x0f,0x38,0xcb}},{1,0}},
    {{0x8A885D04,0x1CEB,0x11C9,{0x9F,0xE8,0x08,0x00,0x2B,0x10,0x48,0x60}},{2,0}},
    0,
    0,
    0,
    0,
    0,
    0x00000000
    };
RPC_IF_HANDLE PcaService_v1_0_c_ifspec = (RPC_IF_HANDLE)& PcaService___RpcClientInterface;

extern const MIDL_STUB_DESC PcaService_StubDesc;

static RPC_BINDING_HANDLE PcaService__MIDL_AutoBindHandle;


long RAiMonitorProcess( 
    handle_t bindingHandle,
    /* [in] */ unsigned __int3264 hProcess,
    /* [in] */ long unknown0,
    /* [string][unique][in] */ wchar_t *exeFileName,
    /* [string][unique][in] */ wchar_t *cmdLine,
    /* [string][unique][in] */ wchar_t *workingDir,
    /* [in] */ long flags)
{

    CLIENT_CALL_RETURN _RetVal;

    _RetVal = NdrClientCall2(
                  ( PMIDL_STUB_DESC  )&PcaService_StubDesc,
                  (PFORMAT_STRING) &pcasvc__MIDL_ProcFormatString.Format[0],
                  ( unsigned char * )&bindingHandle);
    return ( long  )_RetVal.Simple;
    
}


#if !defined(__RPC_WIN32__)
#error  Invalid build platform for this stub.
#endif

#if !(TARGET_IS_NT50_OR_LATER)
#error You need Windows 2000 or later to run this stub because it uses these features:
#error   /robust command line switch.
#error However, your C/C++ compilation flags indicate you intend to run this app on earlier systems.
#error This app will fail with the RPC_X_WRONG_STUB_VERSION error.
#endif


static const pcasvc_MIDL_PROC_FORMAT_STRING pcasvc__MIDL_ProcFormatString =
    {
        0,
        {

	/* Procedure RAiMonitorProcess */

			0x0,		/* 0 */
			0x48,		/* Old Flags:  */
/*  2 */	NdrFcLong( 0x0 ),	/* 0 */
/*  6 */	NdrFcShort( 0x0 ),	/* 0 */
/*  8 */	NdrFcShort( 0x20 ),	/* x86 Stack size/offset = 32 */
/* 10 */	0x32,		/* FC_BIND_PRIMITIVE */
			0x0,		/* 0 */
/* 12 */	NdrFcShort( 0x0 ),	/* x86 Stack size/offset = 0 */
/* 14 */	NdrFcShort( 0x18 ),	/* 24 */
/* 16 */	NdrFcShort( 0x8 ),	/* 8 */
/* 18 */	0x46,		/* Oi2 Flags:  clt must size, has return, has ext, */
			0x7,		/* 7 */
/* 20 */	0x8,		/* 8 */
			0x1,		/* Ext Flags:  new corr desc, */
/* 22 */	NdrFcShort( 0x0 ),	/* 0 */
/* 24 */	NdrFcShort( 0x0 ),	/* 0 */
/* 26 */	NdrFcShort( 0x0 ),	/* 0 */

	/* Parameter hProcess */

/* 28 */	NdrFcShort( 0x48 ),	/* Flags:  in, base type, */
/* 30 */	NdrFcShort( 0x4 ),	/* x86 Stack size/offset = 4 */
/* 32 */	0x8,		/* FC_LONG */
			0x0,		/* 0 */

	/* Parameter unknown0 */

/* 34 */	NdrFcShort( 0x48 ),	/* Flags:  in, base type, */
/* 36 */	NdrFcShort( 0x8 ),	/* x86 Stack size/offset = 8 */
/* 38 */	0x8,		/* FC_LONG */
			0x0,		/* 0 */

	/* Parameter exeFileName */

/* 40 */	NdrFcShort( 0xb ),	/* Flags:  must size, must free, in, */
/* 42 */	NdrFcShort( 0xc ),	/* x86 Stack size/offset = 12 */
/* 44 */	NdrFcShort( 0x2 ),	/* Type Offset=2 */

	/* Parameter cmdLine */

/* 46 */	NdrFcShort( 0xb ),	/* Flags:  must size, must free, in, */
/* 48 */	NdrFcShort( 0x10 ),	/* x86 Stack size/offset = 16 */
/* 50 */	NdrFcShort( 0x2 ),	/* Type Offset=2 */

	/* Parameter workingDir */

/* 52 */	NdrFcShort( 0xb ),	/* Flags:  must size, must free, in, */
/* 54 */	NdrFcShort( 0x14 ),	/* x86 Stack size/offset = 20 */
/* 56 */	NdrFcShort( 0x2 ),	/* Type Offset=2 */

	/* Parameter flags */

/* 58 */	NdrFcShort( 0x48 ),	/* Flags:  in, base type, */
/* 60 */	NdrFcShort( 0x18 ),	/* x86 Stack size/offset = 24 */
/* 62 */	0x8,		/* FC_LONG */
			0x0,		/* 0 */

	/* Return value */

/* 64 */	NdrFcShort( 0x70 ),	/* Flags:  out, return, base type, */
/* 66 */	NdrFcShort( 0x1c ),	/* x86 Stack size/offset = 28 */
/* 68 */	0x8,		/* FC_LONG */
			0x0,		/* 0 */

			0x0
        }
    };

static const pcasvc_MIDL_TYPE_FORMAT_STRING pcasvc__MIDL_TypeFormatString =
    {
        0,
        {
			NdrFcShort( 0x0 ),	/* 0 */
/*  2 */	
			0x12, 0x8,	/* FC_UP [simple_pointer] */
/*  4 */	
			0x25,		/* FC_C_WSTRING */
			0x5c,		/* FC_PAD */

			0x0
        }
    };

static const unsigned short PcaService_FormatStringOffsetTable[] =
    {
    0
    };


static const MIDL_STUB_DESC PcaService_StubDesc = 
    {
    (void *)& PcaService___RpcClientInterface,
    MIDL_user_allocate,
    MIDL_user_free,
    &PcaService__MIDL_AutoBindHandle,
    0,
    0,
    0,
    0,
    pcasvc__MIDL_TypeFormatString.Format,
    1, /* -error bounds_check flag */
    0x50002, /* Ndr library version */
    0,
    0x8010272, /* MIDL Version 8.1.626 */
    0,
    0,
    0,  /* notify & notify_flag routine table */
    0x1, /* MIDL flag */
    0, /* cs routines */
    0,   /* proxy/server info */
    0
    };
#if _MSC_VER >= 1200
#pragma warning(pop)
#endif

#else
#pragma warning(disable:4206)
#endif /* !defined(_M_IA64) && !defined(_M_AMD64) && !defined(_ARM_) */

