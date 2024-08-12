"""
Traffic Jam Whopper System

This module implements a simulation of Burger King's Traffic Jam Whopper feature,
which detects traffic jams and allows for creating food orders in those areas.

The system consists of several key components:
- MockGoogleMapsClient: Simulates the Google Maps API
- TrafficJamDetector: Detects traffic jams using the mock client
- Order: Represents a customer order
- OrderRepository: Handles persistence of orders
- OrderManager: Manages order creation and retrieval
- TrafficJamWhopper: Main class that coordinates the system
- TrafficJamWhopperFactory: Creates instances of TrafficJamWhopper
- CLIFormatter: Formats output for the command-line interface

Usage:
    Run the script to start the Traffic Jam Whopper System CLI:
    $ python akl_bk_traffic_whopper.py

Note: This is a simulation and does not interact with real-world systems or data.
"""

import random
import logging
from datetime import datetime
import json
import os
import textwrap

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MockGoogleMapsClient:
    def __init__(self):
        """Initializes the MockGoogleMapsClient with predefined routes."""
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
        """Simulates the Google Maps API places_nearby method.

        Args:
            location (tuple): The latitude and longitude to search around.
            radius (int): The radius to search within.
            type (str): The type of place to search for.

        Returns:
            dict: A dictionary containing the search results.
        """
        return {"results": self.routes}

    def directions(self, start_location, end_location, mode, departure_time):
        """Simulates the Google Maps API directions method.

        Args:
            start_location (tuple): The starting latitude and longitude.
            end_location (tuple): The ending latitude and longitude.
            mode (str): The mode of transportation.
            departure_time (datetime): The departure time.

        Returns:
            list: A list containing the directions results.
        """
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
        """Initializes the TrafficJamDetector.

        Args:
            maps_client (MockGoogleMapsClient): The mock Google Maps client.
            center (tuple): The center location to search around.
            radius (int): The radius to search within.
        """
        self.maps_client = maps_client
        self.center = center
        self.radius = radius

    def find_traffic_jams(self):
        """Finds traffic jams near the center location.

        Returns:
            list: A list of locations with traffic jams.
        """
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
        """Checks for traffic on a given route.

        Args:
            route (dict): The route to check for traffic.

        Returns:
            bool: True if there is a traffic jam, False otherwise.
        """
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

class Order:
    def __init__(self, customer_name, location):
        """Initializes an Order.

        Args:
            customer_name (str): The name of the customer.
            location (str): The location of the order.
        """
        self.id = random.randint(1000, 9999)
        self.customer_name = customer_name
        self.location = location
        self.timestamp = datetime.now()
        self.status = "Pending"

    def to_dict(self):
        """Converts the Order to a dictionary.

        Returns:
            dict: A dictionary representation of the Order.
        """
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "location": self.location,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }

    def cancel(self):
        """Cancels the Order."""
        self.status = "Removed"

class OrderRepository:
    def __init__(self):
        """Initializes the OrderRepository."""
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.orders_file = os.path.join(self.data_dir, 'orders.json')
        self.orders = self.load_orders()

    def save_order(self, order):
        """Saves an Order to the repository.

        Args:
            order (Order): The order to save.
        """
        self.orders.append(order)
        self.save_orders()

    def get_orders(self):
        """Gets all orders from the repository.

        Returns:
            list: A list of all orders.
        """
        return self.orders

    def save_orders(self):
        """Saves all orders to the orders file."""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.orders_file, 'w') as f:
            json.dump([order.to_dict() for order in self.orders], f)

    def load_orders(self):
        """Loads orders from the orders file.

        Returns:
            list: A list of loaded orders.
        """
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
        """Updates an existing order in the repository.

        Args:
            order (Order): The order to update.
        """
        for i, existing_order in enumerate(self.orders):
            if existing_order.id == order.id:
                self.orders[i] = order
                self.save_orders()
                return

class OrderManager:
    def __init__(self, repository):
        """Initializes the OrderManager.

        Args:
            repository (OrderRepository): The order repository.
        """
        self.repository = repository

    def create_order(self, customer_name, location):
        """Creates a new order.

        Args:
            customer_name (str): The name of the customer.
            location (str): The location of the order.

        Returns:
            Order: The created order.
        """
        order = Order(customer_name, location)
        self.repository.save_order(order)
        logging.info(f"New order created: {order.id} for {customer_name} at {location}")
        return order

    def get_orders(self):
        """Gets all orders.

        Returns:
            list: A list of all orders.
        """
        return self.repository.get_orders()

    def cancel_order(self, order_id):
        """Cancels an order by ID.

        Args:
            order_id (int): The ID of the order to cancel.

        Returns:
            Order: The cancelled order, or None if not found.
        """
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
        """Initializes the TrafficJamWhopper.

        Args:
            maps_client (MockGoogleMapsClient): The mock Google Maps client.
            center (tuple): The center location to search around.
            radius (int): The radius to search within.
            order_manager (OrderManager): The order manager.
        """
        self.detector = TrafficJamDetector(maps_client, center, radius)
        self.order_manager = order_manager
        self.traffic_jam_locations = []

    def check_for_traffic_jams(self):
        """Checks for traffic jams and updates the traffic jam locations."""
        jams = self.detector.find_traffic_jams()
        self.traffic_jam_locations = jams
        for jam_location in jams:
            self.trigger_order_availability(jam_location)

    def trigger_order_availability(self, location):
        """Triggers order availability for a given location.

        Args:
            location (str): The location to trigger order availability for.
        """
        logging.info(f"Traffic Jam Whopper service is now available near {location}")

    def create_order(self, customer_name, location):
        """Creates an order if there is a traffic jam at the location.

        Args:
            customer_name (str): The name of the customer.
            location (str): The location of the order.

        Returns:
            Order: The created order, or None if no traffic jam is detected.
        """
        if location not in self.traffic_jam_locations:
            logging.warning(f"Cannot create order. No traffic jam detected at {location}.")
            print(f"Cannot create order. No traffic jam detected at {location}.")
            return None
        return self.order_manager.create_order(customer_name, location)

class TrafficJamWhopperFactory:
    @staticmethod
    def create():
        """Creates a TrafficJamWhopper instance.

        Returns:
            TrafficJamWhopper: The created TrafficJamWhopper instance.
        """
        gmaps = MockGoogleMapsClient()
        AUCKLAND_CENTER = (-36.8485, 174.7633)
        repository = OrderRepository()
        order_manager = OrderManager(repository)
        return TrafficJamWhopper(gmaps, AUCKLAND_CENTER, radius=5000, order_manager=order_manager)
    

class CLIFormatter:
    @staticmethod
    def header(text):
        return f"\n{'=' * 50}\n{text.center(50)}\n{'=' * 50}"

    @staticmethod
    def subheader(text):
        return f"\n{'-' * 50}\n{text}\n{'-' * 50}"

    @staticmethod
    def table(headers, rows, column_widths):
        result = []
        header_row = " | ".join(h.ljust(w) for h, w in zip(headers, column_widths))
        result.append(header_row)
        result.append("-" * len(header_row))
        for row in rows:
            result.append(" | ".join(str(item).ljust(w) for item, w in zip(row, column_widths)))
        return "\n".join(result)

    @staticmethod
    def wrapped_text(text, width=50):
        return "\n".join(textwrap.wrap(text, width=width))
    

def main():
    """Main function to run the Traffic Jam Whopper service."""
    tj_whopper = TrafficJamWhopperFactory.create()

    while True:
        print(CLIFormatter.header("Traffic Jam Whopper System"))
        print(CLIFormatter.subheader("Menu"))
        print("1. Check for traffic jams")
        print("2. Create an order")
        print("3. View all orders")
        print("4. Cancel an order")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            tj_whopper.check_for_traffic_jams()
            print(CLIFormatter.subheader("Traffic Jam Detection Results"))
            if tj_whopper.traffic_jam_locations:
                headers = ["Location"]
                rows = [[loc] for loc in tj_whopper.traffic_jam_locations]
                print(CLIFormatter.table(headers, rows, [50]))
            else:
                print("No traffic jams detected at this time.")

        elif choice == '2':
            customer_name = input("Enter customer name: ")
            location = input("Enter location: ")
            order = tj_whopper.create_order(customer_name, location)
            if order:
                print(CLIFormatter.subheader("Order Created Successfully"))
                print(CLIFormatter.wrapped_text(f"Order ID: {order.id}"))
                print(CLIFormatter.wrapped_text(f"Customer: {order.customer_name}"))
                print(CLIFormatter.wrapped_text(f"Location: {order.location}"))
                print(CLIFormatter.wrapped_text(f"Status: {order.status}"))

        elif choice == '3':
            orders = tj_whopper.order_manager.get_orders()
            print(CLIFormatter.subheader("All Orders"))
            if orders:
                headers = ["ID", "Customer", "Location", "Status"]
                rows = [[order.id, order.customer_name, order.location, order.status] for order in orders]
                print(CLIFormatter.table(headers, rows, [6, 20, 30, 10]))
            else:
                print("No orders found.")

        elif choice == '4':
            order_id = int(input("Enter order ID to cancel: "))
            cancelled_order = tj_whopper.order_manager.cancel_order(order_id)
            if cancelled_order:
                print(CLIFormatter.subheader("Order Cancelled"))
                print(CLIFormatter.wrapped_text(f"Order ID {cancelled_order.id} has been cancelled."))
            else:
                print(CLIFormatter.wrapped_text("Failed to cancel order. Please check the order ID and try again."))

        elif choice == '5':
            print(CLIFormatter.wrapped_text("Thank you for using the Traffic Jam Whopper System. Goodbye!"))
            break
        else:
            print(CLIFormatter.wrapped_text("Invalid choice. Please try again."))

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()