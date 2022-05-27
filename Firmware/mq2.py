from machine import Pin,ADC

#Select ADC input 0 (GPIO26)
ADC_ConvertedValue = ADC(0)
DIN = Pin(22,Pin.IN)
conversion_factor = 3.3 / (65535)

def gas_state():
    AD_value = ADC_ConvertedValue.read_u16() * conversion_factor
    if(DIN.value() == 1) :
        return {
            "Status": "Not Leaking",
            "Analog output": AD_value,
            "Digital output": DIN
        }
    else :
        return {
            "Status": "Leaking",
            "Analog output": AD_value,
            "Digital output": DIN
        }
        
        

