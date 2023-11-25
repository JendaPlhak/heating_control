from machine import Pin, I2C
import machine
import time
import utime
import ds18x20
import onewire

# RTC module pins
I2C_PORT = 0
I2C_SDA = 20
I2C_SCL = 21

DS18B20_PIN = 28
RELAY_PIN = 26


def bcd2dec(bcd):
    return ((bcd & 0xF0) >> 4) * 10 + (bcd & 0x0F)


def dec2bcd(dec):
    tens, units = divmod(dec, 10)
    return (tens << 4) + units


def tobytes(num):
    return num.to_bytes(1, "little")


class ds3231(object):
    address = int(0x68)
    start_reg = int(0x00)

    def __init__(self, i2c_port, i2c_scl, i2c_sda):
        self.bus = I2C(i2c_port, scl=Pin(i2c_scl), sda=Pin(i2c_sda))

    def read_time(self):
        t = self.bus.readfrom_mem(self.address, self.start_reg, 7)

        ss = bcd2dec(t[0])
        mm = bcd2dec(t[1])
        if t[2] & 0x40:
            hh = bcd2dec(t[2] & 0x1F)
            if t[2] & 0x20:
                hh += 12
        else:
            hh = bcd2dec(t[2])
        wday = t[3]
        mday = bcd2dec(t[4])
        MM = bcd2dec(t[5] & 0x1F)
        YY = bcd2dec(t[6])
        if t[5] & 0x80:
            YY += 2000
        else:
            YY += 1900
        return (
            YY,
            MM,
            mday,
            hh,
            mm,
            ss,
            wday - 1,
        )

    def save_time(self, time_tuple):
        (YY, MM, mday, hh, mm, ss, wday) = time_tuple
        self.bus.writeto_mem(self.address, 0, tobytes(dec2bcd(ss)))
        self.bus.writeto_mem(self.address, 1, tobytes(dec2bcd(mm)))
        self.bus.writeto_mem(self.address, 2, tobytes(dec2bcd(hh)))
        self.bus.writeto_mem(self.address, 3, tobytes(dec2bcd(wday + 1)))
        self.bus.writeto_mem(self.address, 4, tobytes(dec2bcd(mday)))
        if YY >= 2000:
            self.bus.writeto_mem(self.address, 5, tobytes(dec2bcd(MM) | 0b10000000))
            self.bus.writeto_mem(self.address, 6, tobytes(dec2bcd(YY - 2000)))
        else:
            self.bus.writeto_mem(self.address, 5, tobytes(dec2bcd(MM)))
            self.bus.writeto_mem(self.address, 6, tobytes(dec2bcd(YY - 1900)))

    def sync_time(self):
        year, month, day, hour, minute, second, weekday = self.read_time()
        machine.RTC().datetime((year, month, day, weekday, hour, minute, second, 0))


def CETtime():
    year = utime.localtime()[0]
    HHMarch = utime.mktime(
        (year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0, 0)
    )  # Time of March change to CEST
    HHOctober = time.mktime(
        (year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 1, 0, 0, 0, 0, 0)
    )  # Time of October change to CET
    now = time.time()
    if now < HHMarch:  # we are before last sunday of march
        cet = time.localtime(now + 3600)  # CET:  UTC+1H
    elif now < HHOctober:  # we are before last sunday of october
        cet = time.localtime(now + 7200)  # CEST: UTC+2H
    else:  # we are after last sunday of october
        cet = time.localtime(now + 3600)  # CET:  UTC+1H
    return cet


def save_current_UTC_time(rtc: ds3231):
    # Set current time in UTC
    # year, month, day, hour, minute, second, weekday (0 for Monday)
    t = list(time.localtime()[:7])
    t[3] -= 1
    print(t)
    rtc.save_time(t)


def read_ds18b20_temp(one_wire):
    ds_sensor = ds18x20.DS18X20(one_wire)
    roms = ds_sensor.scan()
    if roms:
        ds_sensor.convert_temp()
        time.sleep_ms(750)
        for rom in roms:
            temp = ds_sensor.read_temp(rom)
            return temp
    else:
        print("No DS18B20 devices found")
        return None


relay = Pin(RELAY_PIN, Pin.OUT)
temp_one_wire = onewire.OneWire(Pin(DS18B20_PIN))


class TempMonitor:
    def __init__(self):
        self.high = -1.5
        self.low = -3.0
        self.is_low = False

    def low_temperature(self):
        temp = read_ds18b20_temp(temp_one_wire)
        if temp is None:
            return False
        if self.is_low:
            if temp > self.high:
                self.is_low = False
        else:
            if temp < self.low:
                self.is_low = True
        self.is_low


class TimeMonitor:
    def in_range(self):
        current_time = CETtime()
        month = current_time[1]
        hour = current_time[3]
        is_night = hour < 7 or hour >= 22
        is_heating_season = month <= 5 or month >= 9
        return is_night and is_heating_season


def run_relay_control():
    temp_mon = TempMonitor()
    time_mon = TimeMonitor()
    while True:
        rtc.sync_time()
        if time_mon.in_range() and not temp_mon.low_temperature():
            relay.value(1)
        else:
            relay.value(0)
        utime.sleep(60)


if __name__ == "__main__":
    rtc = ds3231(I2C_PORT, I2C_SCL, I2C_SDA)
    # save_current_UTC_time(rtc)
    rtc.sync_time()

    run_relay_control()
