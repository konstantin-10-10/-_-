import sympy #нет в прошивке
from 2_helper import HallFilamentWideSensorHelper


class EllipseFilamentWideSensorHelper:
    def __init__(self, config):
        self.sensor1 = HallFilamentWideSensorHelper(config, 's1_')
        self.sensor2 = HallFilamentWideSensorHelper(config, 's2_')
        self.sensor3 = HallFilamentWideSensorHelper(config, 's3_')

        self.nominal_filament_dia = config.getfloat(
            'default_nominal_filament_diameter', above=1)
        self.measurement_max_difference = config.getfloat('max_difference', 0.2)
        self.max_diameter = (self.nominal_filament_dia
                             + self.measurement_max_difference)
        self.min_diameter = (self.nominal_filament_dia
                             - self.measurement_max_difference)
        self.runout_dia_min = config.getfloat('min_diameter', 1.0)
        self.runout_dia_max = config.getfloat('max_diameter', self.max_diameter)

    def __call__(self):
        r1, r2, r3 = sorted([i / 2 for i in (self.sensor1.diameter, self.sensor2.diameter,
                                             self.sensor3.diameter)], reverse=True)
        # тут вычисления !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if r3 < self.runout_dia_min or r2 < self.runout_dia_min or r1 < self.runout_dia_min:
            return (self.a * self.b) ** 0.5 * 2
        if r1 == r2:
            if r2 == r3:
                self.a, self.b = r1, r1
                return r1 * 2
            r1, r3 = r3, r1
        if r2 == r3:
            b = (0.75 * r2 ** 2 / (1 - (0.25 * r2 ** 2 / r1 ** 2))) ** 0.5
            self.b, self.a = sorted([r1, b])
            return (self.a * self.b) ** 0.5 * 2
        # тут вычисления !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        c, d = sympy.symbols("c d")
        f1 = sympy.Eq((16 * (r1 ** 4 + r2 ** 4 + r1 ** 2 * r2 ** 2)) * c ** 2 * d ** 2 -
                      (24 * (r1 ** 4 * r2 ** 2 + r1 ** 2 * r2 ** 4)) * c * d ** 2 -
                      (24 * (r1 ** 4 * r2 ** 2 + r1 ** 2 * r2 ** 4)) * c ** 2 * d +
                      (30 * r1 ** 4 * r2 ** 4) * c * d +
                      (9 * r2 ** 4 * r1 ** 4) * d ** 2 +
                      (9 * r2 ** 4 * r1 ** 4) * c ** 2, 0)
        f2 = sympy.Eq((16 * (r1 ** 4 + r3 ** 4 + r1 ** 2 * r3 ** 2)) * c ** 2 * d ** 2 -
                      (24 * (r1 ** 4 * r3 ** 2 + r1 ** 2 * r3 ** 4)) * c * d ** 2 -
                      (24 * (r1 ** 4 * r3 ** 2 + r1 ** 2 * r3 ** 4)) * c ** 2 * d +
                      (30 * r1 ** 4 * r3 ** 4) * c * d +
                      (9 * r3 ** 4 * r1 ** 4) * d ** 2 +
                      (9 * r3 ** 4 * r1 ** 4) * c ** 2, 0)
        rezult = sympy.solve((f1, f2), (c, d))
        self.a, self.b = [(i[0] ** 0.5, i[1] ** 0.5) for i in rezult if i[0] > i[1] > 0][0]
        # тут вычисления !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return (self.a * self.b) ** 0.5 * 2

    def check_for_virtual_f_swich_sensor(self):
        # self.runout_dia_min <= self.diameter <= self.runout_dia_max
        if self.sensor1.diameter < self.runout_dia_min:
            return False
        if self.sensor1.diameter > self.runout_dia_max:
            return False
        if self.sensor2.diameter < self.runout_dia_min:
            return False
        if self.sensor2.diameter > self.runout_dia_max:
            return False
        if self.sensor3.diameter < self.runout_dia_min:
            return False
        if self.sensor3.diameter > self.runout_dia_max:
            return False
        #self.__call__()
        if self.a * 2 > self.runout_dia_max:
            return False
        if self.b * 2 < self.runout_dia_min:
            return False
        return True  # если все ок

    def __str__(self):
        if (self.sensor1.diameter < self.runout_dia_min or
                self.sensor2.diameter < self.runout_dia_min or self.sensor3.diameter < self.runout_dia_min):
            return ('sensor value is less than the minimum value! ' +
                    f'{self.sensor1.SENSOR_PREFIX}diameter={self.sensor1.diameter}' +
                    f'{self.sensor2.SENSOR_PREFIX}diameter={self.sensor2.diameter}' +
                    f'{self.sensor3.SENSOR_PREFIX}diameter={self.sensor3.diameter}')
        virtual_diameter = self.__call__()
        return f'a={self.a}  b={self.b}  virtual_diameter={virtual_diameter}'

    def get_raw_values(self, gcmd):
        gcmd.respond_info('PREFIX=' + self.sensor1.SENSOR_PREFIX + ' ' + self.sensor1.Get_Raw_Values())
        gcmd.respond_info('PREFIX=' + self.sensor2.SENSOR_PREFIX + ' ' + self.sensor2.Get_Raw_Values())
        gcmd.respond_info('PREFIX=' + self.sensor3.SENSOR_PREFIX + ' ' + self.sensor3.Get_Raw_Values())

    def get_status_dict(self):
        virtual_diameter = self.__call__()
        return {'a': self.a, 'b': self.b, 'Virtual_Diameter': virtual_diameter,
                (self.sensor1.SENSOR_PREFIX + 'Raw'): (self.sensor1.lastFilamentWidthReading +
                                                       self.sensor1.lastFilamentWidthReading2),
                (self.sensor2.SENSOR_PREFIX + 'Raw'): (self.sensor2.lastFilamentWidthReading +
                                                       self.sensor2.lastFilamentWidthReading2),
                (self.sensor3.SENSOR_PREFIX + 'Raw'): (self.sensor3.lastFilamentWidthReading +
                                                       self.sensor3.lastFilamentWidthReading2)}
