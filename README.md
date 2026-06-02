# Datalogger_DATAQ_DI2108_Template

Python module for DATAQ datalogger

Features:

current setup reads 4-20mA channels and converts them to adc voltage using 150ohm resistors.

250ohm resistors can be used by changing the conversion factor in the code:

150ohm conversion factor:

(adcVoltage - 0.5) * conversionFactor / (2.9 - 0.5)(adcVoltage - 0.5) * conversionFactor / (2.9 - 0.5)

250ohm conversion factor:

(adcVoltage - 1.0) * conversionFactor / (5.0 - 1.0)(adcVoltage - 1.0) * conversionFactor / (5.0 - 1.0)
