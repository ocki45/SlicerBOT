G21 ; Set units to millimeters
G90 ; Use absolute coordinates
M109 S240 ; Set extruder temperature and wait
M190 S70 ; Set bed temperature and wait
G28 ; Home all axes
M106 S254 ; Set fan speed (0-255)
; Layer Z = 0.000
G0 Z0.000 F3000 ; Move to layer Z

; Layer Z = 0.200
G0 Z0.200 F3000 ; Move to layer Z

; Layer Z = 0.400
G0 Z0.400 F3000 ; Move to layer Z

; Layer Z = 0.600
G0 Z0.600 F3000 ; Move to layer Z

; Layer Z = 0.800
G0 Z0.800 F3000 ; Move to layer Z

; Layer Z = 1.000
G0 Z1.000 F3000 ; Move to layer Z

; Layer Z = 1.200
G0 Z1.200 F3000 ; Move to layer Z

; Layer Z = 1.400
G0 Z1.400 F3000 ; Move to layer Z

; Layer Z = 1.600
G0 Z1.600 F3000 ; Move to layer Z

; Layer Z = 1.800
G0 Z1.800 F3000 ; Move to layer Z

; Layer Z = 2.000
G0 Z2.000 F3000 ; Move to layer Z

; Layer Z = 2.200
G0 Z2.200 F3000 ; Move to layer Z

; Layer Z = 2.400
G0 Z2.400 F3000 ; Move to layer Z

; Layer Z = 2.600
G0 Z2.600 F3000 ; Move to layer Z

; Layer Z = 2.800
G0 Z2.800 F3000 ; Move to layer Z

; Layer Z = 3.000
G0 Z3.000 F3000 ; Move to layer Z

; Layer Z = 3.200
G0 Z3.200 F3000 ; Move to layer Z

; Layer Z = 3.400
G0 Z3.400 F3000 ; Move to layer Z

; Layer Z = 3.600
G0 Z3.600 F3000 ; Move to layer Z

; Layer Z = 3.800
G0 Z3.800 F3000 ; Move to layer Z

; Layer Z = 4.000
G0 Z4.000 F3000 ; Move to layer Z

; Layer Z = 4.200
G0 Z4.200 F3000 ; Move to layer Z

; Layer Z = 4.400
G0 Z4.400 F3000 ; Move to layer Z

; Layer Z = 4.600
G0 Z4.600 F3000 ; Move to layer Z

; Layer Z = 4.800
G0 Z4.800 F3000 ; Move to layer Z

; Layer Z = 5.000
G0 Z5.000 F3000 ; Move to layer Z

; Layer Z = 5.200
G0 Z5.200 F3000 ; Move to layer Z

; Layer Z = 5.400
G0 Z5.400 F3000 ; Move to layer Z

; Layer Z = 5.600
G0 Z5.600 F3000 ; Move to layer Z

; Layer Z = 5.800
G0 Z5.800 F3000 ; Move to layer Z

; Layer Z = 6.000
G0 Z6.000 F3000 ; Move to layer Z

; Layer Z = 6.200
G0 Z6.200 F3000 ; Move to layer Z

; Layer Z = 6.400
G0 Z6.400 F3000 ; Move to layer Z

; Layer Z = 6.600
G0 Z6.600 F3000 ; Move to layer Z

; Layer Z = 6.800
G0 Z6.800 F3000 ; Move to layer Z

; Layer Z = 7.000
G0 Z7.000 F3000 ; Move to layer Z

; Layer Z = 7.200
G0 Z7.200 F3000 ; Move to layer Z

; Layer Z = 7.400
G0 Z7.400 F3000 ; Move to layer Z

; Layer Z = 7.600
G0 Z7.600 F3000 ; Move to layer Z

; Layer Z = 7.800
G0 Z7.800 F3000 ; Move to layer Z

; Layer Z = 8.000
G0 Z8.000 F3000 ; Move to layer Z

; Layer Z = 8.200
G0 Z8.200 F3000 ; Move to layer Z

; Layer Z = 8.400
G0 Z8.400 F3000 ; Move to layer Z

; Layer Z = 8.600
G0 Z8.600 F3000 ; Move to layer Z

; Layer Z = 8.800
G0 Z8.800 F3000 ; Move to layer Z

; Layer Z = 9.000
G0 Z9.000 F3000 ; Move to layer Z

; Layer Z = 9.200
G0 Z9.200 F3000 ; Move to layer Z

; Layer Z = 9.400
G0 Z9.400 F3000 ; Move to layer Z

; Layer Z = 9.600
G0 Z9.600 F3000 ; Move to layer Z

; Layer Z = 9.800
G0 Z9.800 F3000 ; Move to layer Z

M104 S0 ; Turn off extruder
M140 S0 ; Turn off bed
G28 X0 Y0 ; Home X and Y axes
M84 ; Disable steppers
