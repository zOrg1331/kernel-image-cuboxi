#!/bin/bash

sed -i .config \
    -e "s/.*\(CONFIG_DEBUG_SLAB\>\).*/\1=y/" \
    -e "s/.*\(CONFIG_DEBUG_RT_MUTEXES\>\).*/\1=y/" \
    -e "s/.*\(CONFIG_DEBUG_SPINLOCK\>\).*/\1=y/" \
    -e "s/.*\(CONFIG_DEBUG_MUTEXES\>\).*/\1=y/" \
    -e "s/.*\(CONFIG_DEBUG_RWSEMS\>\).*/\1=y/" \
    -e "s/.*\(CONFIG_DEBUG_LOCK_ALLOC\>\).*/\1=y/" \
    -e "s/.*\(CONFIG_PROVE_LOCKING\>\).*/\1=y/" \
    -e "s/.*\(CONFIG_DEBUG_SPINLOCK_SLEEP\>\).*/\1=y/"

echo "CONFIG_DEBUG_SLAB_LEAK=y" >> .config
echo "CONFIG_DEBUG_PI_LIST=y" >> .config
echo "CONFIG_DEBUG_LOCKDEP=n" >> .config
echo "CONFIG_TRACE_IRQFLAGS=y" >> .config
echo "CONFIG_STACKTRACE=y" >> .config
echo "CONFIG_KALLSYMS_ALL=y" >> .config
echo "CONFIG_STACKTRACE=y" >> .config
