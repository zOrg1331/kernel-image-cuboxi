/*
 * Definitions for Coldfire I2C interface
*/
#ifndef mcfi2c_h
#define mcfi2c_h

#if defined(CONFIG_M5206) || defined(CONFIG_M5206e)
#define MCFI2C_IOBASE	(MCF_MBAR + 0x1e0)
#elif defined(CONFIG_M523x) || defined(CONFIG_M527x) || defined(CONFIG_M528x)
#define MCFI2C_IOBASE	(MCF_IPSBAR + 0x300)
#elif defined(CONFIG_M5249) || defined(CONFIG_M5307) || defined(CONFIG_M5407)
#define MCFI2C_IOBASE	(MCF_MBAR + 0x280)
#ifdef CONFIG_M5249
#define MCFI2C_IOBASE2	(MCF_MBAR2 + 0x440)
#endif
#elif defined(CONFIG_M520x) || defined(CONFIG_M532x) || defined(CONFIG_M5445x)
#define MCFI2C_IOBASE	0xFC058000
#endif
#define	MCFI2C_IOSIZE	0x40

/**
 * struct mcfi2c_platform_data - platform data for the coldfire i2c driver
 * @bitrate: bitrate to use for this i2c controller.
*/
struct mcfi2c_platform_data {
	u32	bitrate;
};

#endif /* mcfi2c_h */
