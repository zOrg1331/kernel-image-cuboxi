/*
 * PKUNITY Interrupt Controller (INTC) Registers
 */
/*
 * INTC Level Reg INTC_ICLR.
 */
#define INTC_ICLR	io_p2v(PKUNITY_INTC_BASE + 0x0000)
/*
 * INTC Mask Reg INTC_ICMR.
 */
#define INTC_ICMR	io_p2v(PKUNITY_INTC_BASE + 0x0004)
/*
 * INTC Pending Reg INTC_ICPR.
 */
#define INTC_ICPR	io_p2v(PKUNITY_INTC_BASE + 0x0008)
/*
 * INTC IRQ Pending Reg INTC_ICIP.
 */
#define INTC_ICIP	io_p2v(PKUNITY_INTC_BASE + 0x000C)
/*
 * INTC REAL Pending Reg INTC_ICFP.
 */
#define INTC_ICFP	io_p2v(PKUNITY_INTC_BASE + 0x0010)
/*
 * INTC Control Reg INTC_ICCR.
 */
#define INTC_ICCR	io_p2v(PKUNITY_INTC_BASE + 0x0014)

