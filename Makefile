TOP:=$(CURDIR)
ifneq (1,$(words $(TOP)))
TOP:=.
endif

include $(TOP)/configure/RULES
