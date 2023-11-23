# Heating control

This project is designed to control a solenoid valve using solid-state relay.
The goal is to eliminate disturbing nightly noises coming from the central heating system.

The control process activates the relay (closes the valve) between 22:00 and 7:00 if
the outside temperature is higher than -3 degrees Celsius.

## Coding

The microcontroller is programmed using MicroPython. It's just one [Python file](main.py). Loading time from the attached
RTC module is a bit tricky, but otherwise the script is dead simple.

## Used components

- Raspberry Pi Pico W RP2040 Microcontroller ([link](https://www.amazon.de/-/en/dp/B0BN5YT8W6?psc=1&ref=ppx_yo2ov_dt_b_product_details))
- MASUNN Ds18B20 - Digital Temperature Sensor ([link](https://www.amazon.de/dp/B07QGRC5KJ?ref=ppx_yo2ov_dt_b_product_details&th=1))
- Solid state relay module  ([link](https://www.amazon.de/-/en/dp/B084SWK4VY?psc=1&ref=ppx_yo2ov_dt_b_product_details))
- Waveshare Precision RTC Module  ([link](https://www.amazon.de/-/en/dp/B08VRL1D95?psc=1&ref=ppx_yo2ov_dt_b_product_details))
- YYRL 12V/24V/36V/48V to 5V, Car Micro USB Power Supply ([link](https://www.amazon.de/dp/B09L68LTZ7?psc=1&ref=ppx_yo2ov_dt_b_product_details))

## Enclosure

You can find the Fusion project for the box enclosure [here](heat_controller_box_v12.f3d)
