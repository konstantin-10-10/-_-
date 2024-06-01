ADC_REPORT_TIME = 0.500
ADC_SAMPLE_TIME = 0.03
ADC_SAMPLE_COUNT = 15


class HallFilamentWideSensorHelper:
    def __init__(self, config, SENSOR_PREFIX):
        self.printer = config.get_printer()
        self.pin1 = config.get(SENSOR_PREFIX + 'adc1_pin')
        self.pin2 = config.get(SENSOR_PREFIX + 'adc2_pin')
        self.dia1 = config.getfloat(SENSOR_PREFIX + 'Cal_dia1', 1.5)
        self.dia2 = config.getfloat(SENSOR_PREFIX + 'Cal_dia2', 2.0)
        self.rawdia1 = config.getint(SENSOR_PREFIX + 'Raw_dia1', 9500)
        self.rawdia2 = config.getint(SENSOR_PREFIX + 'Raw_dia2', 10500)
        self.nominal_filament_dia = config.getfloat(
            'default_nominal_filament_diameter', above=1)
        self.diameter = self.nominal_filament_dia
        self.ppins = self.printer.lookup_object('pins')
        self.mcu_adc = self.ppins.setup_pin('adc', self.pin1)
        self.mcu_adc.setup_minmax(ADC_SAMPLE_TIME, ADC_SAMPLE_COUNT)
        self.mcu_adc.setup_adc_callback(ADC_REPORT_TIME, self.adc_callback)
        self.mcu_adc2 = self.ppins.setup_pin('adc', self.pin2)
        self.mcu_adc2.setup_minmax(ADC_SAMPLE_TIME, ADC_SAMPLE_COUNT)
        self.mcu_adc2.setup_adc_callback(ADC_REPORT_TIME, self.adc2_callback)
        self.lastFilamentWidthReading = 0
        self.lastFilamentWidthReading2 = 0
        self.SENSOR_PREFIX = SENSOR_PREFIX

    def adc_callback(self, read_time, read_value):
        # read sensor value
        self.lastFilamentWidthReading = round(read_value * 10000)

    def adc2_callback(self, read_time, read_value):
        # read sensor value
        self.lastFilamentWidthReading2 = round(read_value * 10000)
        # calculate diameter
        diameter_new = round((self.dia2 - self.dia1) /
                             (self.rawdia2 - self.rawdia1) *
                             ((self.lastFilamentWidthReading + self.lastFilamentWidthReading2)
                              - self.rawdia1) + self.dia1, 4)
        self.diameter = (5.0 * self.diameter + diameter_new) / 6

    def Get_Raw_Values(self):
        response = "ADC1="
        response += str(self.lastFilamentWidthReading)
        response += (" ADC2=" + str(self.lastFilamentWidthReading2))
        response += (" RAW=" +
                     str(self.lastFilamentWidthReading
                         + self.lastFilamentWidthReading2))
        return response
