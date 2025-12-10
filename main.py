from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import requests
import math
import time
from plyer import notification
import threading

lat1 = 22.635232
lon1 = 75.849823
distance = 10
is_running = False

#--------------------------------------------------------

def get_current_location():
    """Get location using unlimited free API"""
    try:
        response = requests.get('http://ip-api.com/json/', timeout=5)
        data = response.json()
        
        if data.get('status') == 'fail':
            print(f"Error: {data.get('message')}")
            return None
        
        return {
            'latitude': data['lat'],
            'longitude': data['lon']
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def distance_between(lat1, lon1):
    """Calculate distance between coordinates"""
    global distance
    coordinates = get_current_location()
    lat2 = coordinates['latitude']
    lon2 = coordinates['longitude']

    d_lat = radian(lat2 - lat1)
    d_lon = radian(lon2 - lon1)

    hav_theta = hav(d_lat) + math.cos(radian(lat1)) * math.cos(radian(lat2)) * hav(d_lon)
    theta = theta_from_hav(hav_theta)
    distance = 6378.1 * theta

    return distance 

def radian(q):
    return q * math.pi/180

def hav(q):
    return math.sin(q/2) * math.sin(q/2)

def theta_from_hav(h):
    return 2 * math.asin(math.sqrt(h))

def location_monitor():
    """Run in background thread"""
    global is_running, distance
    notification.notify(
        title="App Started",
        message="Monitoring location...",
        timeout=2
    )
    
    while is_running:
        try:
            distance_between(lat1, lon1)
            print(f"Distance: {distance:.2f} km")
            
            if distance < 1:
                notification.notify(
                    title="Proximity Alert",
                    message="You are within 1 km of the target location!",
                    timeout=10
                )
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(900)

#---------------------------------------------------------
class MyGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.cols = 1
        self.add_widget(Label(text="Welcome to App"))

        self.latt = TextInput(text=str(lat1), hint_text="Enter Latitude", multiline=False)
        self.long = TextInput(text=str(lon1), hint_text="Enter Longitude", multiline=False)
        
        self.add_widget(self.latt)
        self.add_widget(self.long)

        home = Button(text="Home coordinates set")
        home.bind(on_press=self.on_home)
        self.add_widget(home)

        clg = Button(text="Clg coordinates set")
        clg.bind(on_press=self.on_clg)
        self.add_widget(clg)

        start_button = Button(text="Start")
        start_button.bind(on_press=self.on_start_pressed)
        self.add_widget(start_button)
        
        stop_button = Button(text="Stop")
        stop_button.bind(on_press=self.on_stop_pressed)
        self.add_widget(stop_button)
    
    def on_start_pressed(self, instance):
        global is_running
        is_running = True
        # Run in background thread so UI doesn't freeze
        thread = threading.Thread(target=location_monitor, daemon=True)
        thread.start()
    
    def on_stop_pressed(self, instance):
        global is_running
        is_running = False
        notification.notify(
            title="App Stopped",
            message="Location monitoring stopped.",
            timeout=2
        )
    
    def on_home(self, instance):
        global lat1, lon1
        lat1 = 22.717
        lon1 = 75.8337
        notification.notify(
            title="coordinates Set",
            message="cordinates set to Home",
            timeout=2
        )
    
    def on_clg(self, instance):
        global lat1, lon1
        lat1 = 22.635232
        lon1 = 75.849823
        notification.notify(
            title="coordinates Set",
            message="cordinates set to clg",
            timeout=2
        )

class Rubix(App):
    def build(self):
        return MyGrid()

if __name__ == "__main__":
    app = Rubix()
    app.run()
