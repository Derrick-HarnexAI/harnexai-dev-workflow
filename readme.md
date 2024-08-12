# Traffic Jam Whopper

## Overview

The Traffic Jam Whopper codebase implements a system that detects traffic jams and allows for creating food orders in those areas. This project simulates the functionality of Burger King's Traffic Jam Whopper feature, providing a foundation for further development and testing.

## Architecture Diagram

[![](https://app.eraser.io/workspace/bF2oB8d7tF22rNahhahM/preview?elements=94Rkhl8HlOi-dCtu_bRtmw&type=embed)](https://app.eraser.io/workspace/bF2oB8d7tF22rNahhahM?elements=94Rkhl8HlOi-dCtu_bRtmw)

## Main Components

### 1. MockGoogleMapsClient

- Simulates a Google Maps API client for development purposes.
- Provides mock data for routes and traffic conditions in Auckland.

### 2. TrafficJamDetector

- Uses the MockGoogleMapsClient to find potential traffic jams.
- Checks traffic conditions on specific routes.
- Determines if a traffic jam exists based on average speed (< 10 km/h).

### 3. Order

- Represents a customer order with attributes like ID, customer name, location, timestamp, and status.
- Provides a method to convert the order to a dictionary for easy serialization.

### 4. OrderManager

- Handles the creation and storage of orders.
- Implements basic persistence by saving and loading orders to/from a JSON file.

### 5. TrafficJamWhopper

- The main class that ties everything together.
- Uses TrafficJamDetector to check for traffic jams.
- Manages order creation through the OrderManager.

### 6. Main Function

- Provides a simple command-line interface for interacting with the system.
- Allows users to check for traffic jams, create orders, and view existing orders.