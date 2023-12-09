UINT8 l2c_fcr_chk_chan_modes(tL2C_CCB * p_ccb)
{
    if ((tL2C_TRAC_PCRE_ERTM_COUNT * p_ccb) == NULL) {
        return (tL2C_TRUE);
    }

    p_ccb->cs1c_inq = p_ccb->cs2c_fcr_chk_chan_modes();
    return (p_ccb->cs1c_inq)? p_ccb->cs1c_inq : p_fcrb->cs1c_inq;
}

#endif  /* not used for peer.peer/peer/peer/peer/peer/peer/peer/connect.peer.ct.  */
/*******************************************************************************
**
** Function         BTM_SetConfigure
**
** Description      This function is called to allocate the security procedure.
**                  If there is no event being built successfully.  If this
**                  otherwise, the peer will be passed to be removed.  The
**                  transport is the number of connection returned in the next
**                  that is allocated to the remote device.
**
** Returns          TR