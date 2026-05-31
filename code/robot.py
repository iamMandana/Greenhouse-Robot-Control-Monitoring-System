import random

class Robot:
    def __init__(self):
        # position
        self.x = 0
        self.y = 0
        self.home = (0, 0)
        # custom path
        self.path = [(0,0), (5,0), (5,5), (0,5)]   # square greenhouse
        self.current_target_index = 0

        # system
        self.battery = 100
        self.state = "IDLE"
        self.autonomous = False

        self.going_home = False
        self.waiting_full_charge = False
        self.resume_after_charge = True  

        self.decision = "Waiting"

        # step system
        self.step_mode = "MOVE"  # MOVE → SENSE → DECIDE

        # greenhouse sensors
        self.temperature = 25
        self.humidity = 60
        self.soil = 50
        self.light = 400

        
        self.temp_history = []
        self.humidity_history = []
        self.soil_history = []
        self.light_history = []

        self.fan_on = False
        self.grow_light_on = False
        self.water_pump_on = False
        self.heater_on = False

    # control functions

    def update_actuators(self):
        # Fan control based on temperature
        if self.temperature > 30 and not self.fan_on:
            self.fan_on = True
            self.decision = "High temperature - Cooling fan activated"
        elif self.temperature <= 30 and self.fan_on:
            self.fan_on = False
        
        # Grow light control based on light level
        if self.light < 200 and not self.grow_light_on:
            self.grow_light_on = True
            self.decision = "Low light - Grow light activated"
        elif self.light >= 200 and self.grow_light_on:
            self.grow_light_on = False
        
        # Water pump control based on soil moisture
        if self.soil < 30 and not self.water_pump_on:
            self.water_pump_on = True
            self.decision = "Soil dry - Water pump activated"
        elif self.soil >= 30 and self.water_pump_on:
            self.water_pump_on = False
        
        # Heater control based on low temperature
        if self.temperature < 18 and not self.heater_on:
            self.heater_on = True
            self.decision = "Low temperature - Heater activated"
        elif self.temperature >= 18 and self.heater_on:
            self.heater_on = False

    def move_to_target(self):
        target_x, target_y = self.path[self.current_target_index]

        if self.x < target_x:
            self.x += 1
        elif self.x > target_x:
            self.x -= 1

        if self.y < target_y:
            self.y += 1
        elif self.y > target_y:
            self.y -= 1

        # Check if reached target
        if (self.x, self.y) == (target_x, target_y):
            self.current_target_index = (self.current_target_index + 1) % len(self.path)

    def start_autonomous(self):
        if self.state == "SHUTDOWN":
            self.decision = "System is OFF"
            return

        self.autonomous = True

        if self.state == "CHARGING":
            self.decision = "Charging interrupted → resuming"
            self.state = "MOVING"
            self.waiting_full_charge = False
        else:
            self.state = "MOVING"
            self.decision = "Autonomous started"

    def stop(self):
        if self.battery <= 20:
            self.decision = "Cannot stop → battery too low"
            return

        self.autonomous = False
        self.going_home = False
        self.state = "IDLE"
        self.decision = "Stopped by user"

    def emergency_stop(self):
        self.autonomous = False
        self.going_home = False
        self.state = "STOPPED"
        self.decision = "EMERGENCY STOP"

    def shutdown(self):
        self.autonomous = False
        self.going_home = False
        self.state = "SHUTDOWN"
        self.decision = "System OFF"

    def power_on(self):
        if self.state == "SHUTDOWN":
            self.state = "IDLE"
            self.decision = "System ON"

    def toggle_resume_after_charge(self):
        self.resume_after_charge = not self.resume_after_charge

    def go_home(self):
        if self.state == "SHUTDOWN":
            return

        self.going_home = True
        self.state = "GOING_HOME"
        self.decision = "Manual return to charger"

    # sensors and decisions
    def read_sensors(self):
        self.temperature = random.randint(18, 35)
        self.humidity = random.randint(40, 90)
        self.soil = random.randint(20, 80)
        self.light = random.randint(100, 800)

        self.temp_history.append(self.temperature)
        self.humidity_history.append(self.humidity)
        self.soil_history.append(self.soil)
        self.light_history.append(self.light)

        # Keep only last 200 readings
        if len(self.temp_history) > 200:
            self.temp_history.pop(0)
            self.humidity_history.pop(0)
            self.soil_history.pop(0)
            self.light_history.pop(0)

    def make_decision(self):
        if self.temperature > 30:
            self.decision = "High temp → Turn ON fan"

        elif self.soil < 30:
            self.decision = "Soil dry → Start irrigation"

        elif self.light < 200:
            self.decision = "Low light → Turn ON LED"

        else:
            self.decision = "Environment OK"

    # update loop
    def update(self):

        # hard shutdown
        if self.state == "SHUTDOWN":
            return

        # battery fail
        if self.battery <= 0:
            self.battery = 0
            self.state = "SHUTDOWN"
            self.autonomous = False
            self.decision = "Battery depleted → system OFF"
            return

        # charging
        if self.state == "CHARGING":
            self.battery += 2

            if self.battery >= 100:
                self.battery = 100
                self.waiting_full_charge = False

                if self.autonomous and self.resume_after_charge:
                    self.state = "MOVING"
                else:
                    self.state = "IDLE"

            return

        # going home
        if self.going_home:
            self.decision = "Returning to charger"

            if self.x > 0:
                self.x -= 1
            elif self.x < 0:
                self.x += 1

            if self.y > 0:
                self.y -= 1
            elif self.y < 0:
                self.y += 1

            self.battery -= 0.5

            if (self.x, self.y) == self.home:
                self.state = "CHARGING"
                self.going_home = False
                self.waiting_full_charge = True
                self.decision = "Charging started"

            return

        # low battery
        if self.battery <= 20:
            self.going_home = True
            self.autonomous = True
            self.state = "GOING_HOME"
            self.decision = "Low battery → going home"
            return

        # autonomous system
        if self.autonomous:

            if self.step_mode == "MOVE":
                self.state = "MOVING"

                self.move_to_target()

                self.battery -= 1
                self.step_mode = "SENSE"

            elif self.step_mode == "SENSE":
                self.state = "SENSING"
                self.read_sensors()
                self.battery -= 0.3

                self.step_mode = "DECIDE"

            elif self.step_mode == "DECIDE":
                self.state = "DECIDING"
                self.make_decision()
                self.battery -= 0.2

                self.step_mode = "MOVE"

        else:
            # idle
            self.state = "IDLE"

            if (self.x, self.y) != self.home:
                self.battery -= 0.1

        # clamp
        self.battery = max(0, min(100, self.battery))
