import random
import logging
from datetime import datetime
import json
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MockGoogleMapsClient:
    def __init__(self):
        self.routes = [
            {"name": "Queen Street", "geometry": {"location": (-36.8485, 174.7633)}},
            {"name": "Karangahape Road", "geometry": {"location": (-36.8573, 174.7614)}},
            {"name": "Ponsonby Road", "geometry": {"location": (-36.8581, 174.7429)}},
            {"name": "Hobson Street", "geometry": {"location": (-36.8487, 174.7620)}},
            {"name": "Nelson Street", "geometry": {"location": (-36.8544, 174.7680)}},
            {"name": "Brigham Creek Road", "geometry": {"location": (-36.8185, 174.5853)}},
            {"name": "Lincoln Road", "geometry": {"location": (-36.8605, 174.6281)}},
            {"name": "Lake Road", "geometry": {"location": (-36.7912, 174.7657)}},
            {"name": "Glenfield Road", "geometry": {"location": (-36.7749, 174.7163)}},
            {"name": "Tamaki Drive", "geometry": {"location": (-36.8449, 174.8272)}},
            {"name": "Dominion Road", "geometry": {"location": (-36.8806, 174.7467)}},
            {"name": "Howick Road", "geometry": {"location": (-36.9069, 174.9186)}},
            {"name": "Pakuranga Road", "geometry": {"location": (-36.9019, 174.8727)}},
            {"name": "Te Irirangi Drive", "geometry": {"location": (-36.9592, 174.8905)}},
        ]

    def places_nearby(self, location, radius, type):
        return {"results": self.routes}

    def directions(self, start_location, end_location, mode, departure_time):
        distance = random.uniform(1000, 5000)
        duration = random.uniform(300, 1800)
        return [{
            "legs": [{
                "distance": {"value": distance},
                "duration_in_traffic": {"value": duration}
            }]
        }]

class TrafficJamDetector:
    def __init__(self, maps_client, center, radius):
        self.maps_client = maps_client
        self.center = center
        self.radius = radius

    def find_traffic_jams(self):
        places_result = self.maps_client.places_nearby(
            location=self.center,
            radius=self.radius,
            type='route'
        )

        jams = []
        for place in places_result.get('results', []):
            if self.check_traffic_on_route(place):
                jams.append(place['name'])
        return jams

    def check_traffic_on_route(self, route):
        try:
            start_location = route['geometry']['location']
            end_location = route['geometry']['location']

            directions_result = self.maps_client.directions(
                start_location,
                end_location,
                mode="driving",
                departure_time=datetime.now()
            )

            if directions_result:
                leg = directions_result[0]['legs'][0]
                duration = leg['duration_in_traffic']['value']
                distance = leg['distance']['value']
                
                average_speed = (distance / 1000) / (duration / 3600)

                if average_speed < 10:
                    logging.info(f"Traffic jam detected on {route['name']}. Average Speed: {average_speed:.2f} km/h")
                    return True
                else:
                    logging.info(f"No traffic jam on {route['name']}. Average speed: {average_speed:.2f} km/h")
            return False
        except Exception as e:
            logging.error(f"Error checking traffic on {route['name']}: {str(e)}")
            return False

# Update the Order class
class Order:
    def __init__(self, customer_name, location):
        self.id = random.randint(1000, 9999)
        self.customer_name = customer_name
        self.location = location
        self.timestamp = datetime.now()
        self.status = "Pending"

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "location": self.location,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }

    def cancel(self):
        self.status = "Removed"


# Update the OrderRepository class
class OrderRepository:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.orders_file = os.path.join(self.data_dir, 'orders.json')
        self.orders = self.load_orders()

    def save_order(self, order):
        self.orders.append(order)
        self.save_orders()

    def get_orders(self):
        return self.orders

    def save_orders(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.orders_file, 'w') as f:
            json.dump([order.to_dict() for order in self.orders], f)

    def load_orders(self):
        if os.path.exists(self.orders_file):
            with open(self.orders_file, 'r') as f:
                order_dicts = json.load(f)
                orders = []
                for o in order_dicts:
                    order = Order(o['customer_name'], o['location'])
                    order.id = o['id']
                    order.timestamp = datetime.fromisoformat(o['timestamp'])
                    order.status = o['status']
                    orders.append(order)
                return orders
        return []

    def update_order(self, order):
        for i, existing_order in enumerate(self.orders):
            if existing_order.id == order.id:
                self.orders[i] = order
                self.save_orders()
                return

# Update the OrderManager class
class OrderManager:
    def __init__(self, repository):
        self.repository = repository

    def create_order(self, customer_name, location):
        order = Order(customer_name, location)
        self.repository.save_order(order)
        logging.info(f"New order created: {order.id} for {customer_name} at {location}")
        return order

    def get_orders(self):
        return self.repository.get_orders()

    def cancel_order(self, order_id):
        orders = self.get_orders()
        for order in orders:
            if order.id == order_id:
                if order.status == "Removed":
                    logging.warning(f"Order {order_id} has already been cancelled.")
                    return None
                order.cancel()
                self.repository.update_order(order)
                logging.info(f"Order {order_id} has been cancelled.")
                return order
        logging.warning(f"Order {order_id} not found.")
        return None

class TrafficJamWhopper:
    def __init__(self, maps_client, center, radius, order_manager):
        self.detector = TrafficJamDetector(maps_client, center, radius)
        self.order_manager = order_manager
        self.traffic_jam_locations = []

    def check_for_traffic_jams(self):
        jams = self.detector.find_traffic_jams()
        self.traffic_jam_locations = jams
        for jam_location in jams:
            self.trigger_order_availability(jam_location)

    def trigger_order_availability(self, location):
        logging.info(f"Traffic Jam Whopper service is now available near {location}")

    def create_order(self, customer_name, location):
        if location not in self.traffic_jam_locations:
            logging.warning(f"Cannot create order. No traffic jam detected at {location}.")
            print(f"Cannot create order. No traffic jam detected at {location}.")
            return None
        return self.order_manager.create_order(customer_name, location)

class TrafficJamWhopperFactory:
    @staticmethod
    def create():
        gmaps = MockGoogleMapsClient()
        AUCKLAND_CENTER = (-36.8485, 174.7633)
        repository = OrderRepository()
        order_manager = OrderManager(repository)
        return TrafficJamWhopper(gmaps, AUCKLAND_CENTER, radius=5000, order_manager=order_manager)

# Update the main function
def main():
    tj_whopper = TrafficJamWhopperFactory.create()

    while True:
        print("\n1. Check for traffic jams")
        print("2. Create an order")
        print("3. View all orders")
        print("4. Cancel an order")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            tj_whopper.check_for_traffic_jams()
        elif choice == '2':
            customer_name = input("Enter customer name: ")
            location = input("Enter location: ")
            tj_whopper.create_order(customer_name, location)
        elif choice == '3':
            orders = tj_whopper.order_manager.get_orders()
            for order in orders:
                print(f"Order {order.id}: {order.customer_name} at {order.location} - Status: {order.status}")
        elif choice == '4':
            order_id = int(input("Enter order ID to cancel: "))
            tj_whopper.order_manager.cancel_order(order_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()