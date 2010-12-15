obj-y	:= clock.o sched-clock.o
obj-$(CONFIG_ARM_TIMER_SP804) += timer-sp.o
ifeq ($(CONFIG_LEDS_CLASS),y)
obj-$(CONFIG_ARCH_REALVIEW) += leds.o
obj-$(CONFIG_ARCH_VERSATILE) += leds.o
endif
