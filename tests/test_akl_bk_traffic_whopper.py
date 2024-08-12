"""
Unit tests for the Auckland Burger King Traffic Jam Whopper system.

This test suite covers the main components of the akl_bk_traffic_whopper.py module:
- MockGoogleMapsClient
- TrafficJamDetector
- Order
- OrderManager
- TrafficJamWhopper

It also includes an abstract base class for OrderRepository and its in-memory implementation.
"""

import unittest
import sys
import os
from unittest.mock import patch
from datetime import datetime
from abc import ABC, abstractmethod

from akl_bk_traffic_whopper import MockGoogleMapsClient, TrafficJamDetector, Order, OrderManager, TrafficJamWhopper

class TestMockGoogleMapsClient(unittest.TestCase):
    """Test suite for the MockGoogleMapsClient class."""

    def setUp(self):
        """Initialize a MockGoogleMapsClient instance for each test."""
        self.client = MockGoogleMapsClient()

    def test_places_nearby(self):
        """
        Test the places_nearby method of MockGoogleMapsClient.
        
        Verifies that the method returns a dictionary with a 'results' key
        containing a list of routes.
        """
        result = self.client.places_nearby((-36.8485, 174.7633), 5000, 'route')
        self.assertIsInstance(result, dict)
        self.assertIn('results', result)
        self.assertIsInstance(result['results'], list)

    def test_directions(self):
        """
        Test the directions method of MockGoogleMapsClient.
        
        Verifies that the method returns a list containing route information
        with 'legs' data.
        """
        result = self.client.directions((-36.8485, 174.7633), (-36.8581, 174.7429), 'driving', datetime.now())
        self.assertIsInstance(result, list)
        self.assertIn('legs', result[0])

class TestTrafficJamDetector(unittest.TestCase):
    """Test suite for the TrafficJamDetector class."""

    def setUp(self):
        """Initialize a TrafficJamDetector instance with a MockGoogleMapsClient for each test."""
        self.maps_client = MockGoogleMapsClient()
        self.detector = TrafficJamDetector(self.maps_client, (-36.8485, 174.7633), 5000)

    def test_find_traffic_jams(self):
        """
        Test the find_traffic_jams method of TrafficJamDetector.
        
        Verifies that the method returns a list of traffic jams.
        """
        jams = self.detector.find_traffic_jams()
        self.assertIsInstance(jams, list)

class TestOrder(unittest.TestCase):
    """Test suite for the Order class."""

    def test_order_creation(self):
        """
        Test the creation of an Order instance.
        
        Verifies that an Order is created with the correct attributes.
        """
        order = Order("John Doe", "123 Test St")
        self.assertEqual(order.customer_name, "John Doe")
        self.assertEqual(order.location, "123 Test St")
        self.assertEqual(order.status, "Pending")

class OrderRepository(ABC):
    """Abstract base class for OrderRepository."""

    @abstractmethod
    def save_order(self, order):
        """Save an order."""
        pass

    @abstractmethod
    def get_order(self, order_id):
        """Retrieve an order by its ID."""
        pass

    @abstractmethod
    def get_all_orders(self):
        """Retrieve all orders."""
        pass

class InMemoryOrderRepository(OrderRepository):
    """In-memory implementation of OrderRepository for testing purposes."""

    def __init__(self):
        """Initialize an empty dictionary to store orders."""
        self.orders = {}

    def save_order(self, order):
        """Save an order to the in-memory storage."""
        self.orders[order.id] = order

    def get_order(self, order_id):
        """Retrieve an order by its ID from the in-memory storage."""
        return self.orders.get(order_id)

    def get_all_orders(self):
        """Retrieve all orders from the in-memory storage."""
        return list(self.orders.values())

class TestOrderManager(unittest.TestCase):
    """Test suite for the OrderManager class."""

    def setUp(self):
        """Initialize an OrderManager instance with an InMemoryOrderRepository for each test."""
        self.repository = InMemoryOrderRepository()
        self.order_manager = OrderManager(self.repository)

    @patch('akl_bk_traffic_whopper.open')
    def test_create_order(self, mock_open):
        """
        Test the create_order method of OrderManager.
        
        Verifies that an order is created with the correct attributes and saved to the repository.
        """
        order = self.order_manager.create_order("Jane Smith", "456 Sample Ave")
        self.assertIsInstance(order, Order)
        self.assertEqual(order.customer_name, "Jane Smith")
        self.assertEqual(order.location, "456 Sample Ave")
        self.assertIn(order.id, self.repository.orders)

class TestTrafficJamWhopper(unittest.TestCase):
    """Test suite for the TrafficJamWhopper class."""

    def setUp(self):
        """Initialize a TrafficJamWhopper instance with necessary dependencies for each test."""
        self.maps_client = MockGoogleMapsClient()
        self.repository = InMemoryOrderRepository()
        self.order_manager = OrderManager(self.repository)
        self.tj_whopper = TrafficJamWhopper(self.maps_client, (-36.8485, 174.7633), 5000, self.order_manager)

    def test_check_for_traffic_jams(self):
        """
        Test the check_for_traffic_jams method of TrafficJamWhopper.
        
        Verifies that the method calls trigger_order_availability when traffic jams are found.
        """
        with patch.object(self.tj_whopper, 'trigger_order_availability') as mock_trigger:
            self.tj_whopper.check_for_traffic_jams()
            mock_trigger.assert_called()

if __name__ == '__main__':
    unittest.main()