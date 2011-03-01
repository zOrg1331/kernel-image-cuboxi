/*
 * PKUnity PS2 Controller Registers
 */
/*
 * the same as I8042_DATA_REG PS2_DATA
 */
#define PS2_DATA	io_p2v(PKUNITY_PS2_BASE + 0x0060)
/*
 * the same as I8042_COMMAND_REG PS2_COMMAND
 */
#define PS2_COMMAND	io_p2v(PKUNITY_PS2_BASE + 0x0064)
/*
 * the same as I8042_STATUS_REG PS2_STATUS
 */
#define PS2_STATUS	io_p2v(PKUNITY_PS2_BASE + 0x0064)
/*
 * counter reg PS2_CNT
 */
#define PS2_CNT		io_p2v(PKUNITY_PS2_BASE + 0x0068)

