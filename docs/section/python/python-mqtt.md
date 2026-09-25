# Message Queuing Telemetry Transport (MQTT) with Python

!!! info "Learning Objectives"
    - Understand the Publish/Subscribe (Pub/Sub) architecture and its advantages over request-response models.
    - Implement MQTT publishers and subscribers using the `paho-mqtt` library.
    - Design and manage MQTT topic hierarchies using wildcards.
    - Configure Quality of Service (QoS) levels to ensure message delivery reliability.
    - Implement advanced MQTT features, including Retained messages and Last Will and Testament (LWT).
    - Apply security best practices for MQTT connections using TLS and authentication.

In traditional web communication, the HTTP protocol uses a request-response model where a client asks for data and the server responds. This model is inefficient for Internet of Things (IoT) and cloud telemetry, where devices may be battery-powered, have unstable network connections, or need to push data to multiple observers in real-time.

Message Queuing Telemetry Transport (MQTT) is a lightweight, binary messaging protocol designed specifically for these constraints. Instead of direct client-server communication, MQTT uses a Broker to mediate messages. Devices (clients) "publish" messages to a specific "topic," and other devices "subscribe" to those topics. The broker ensures that any message published to a topic is delivered to all current subscribers of that topic.

## The MQTT Architecture

The MQTT ecosystem consists of three primary components: the Broker, the Publisher, and the Subscriber.

### The Broker

The broker is the central server that manages all communication. It does not store messages permanently (unless they are "retained") but handles the routing of messages from publishers to subscribers. Popular brokers include Mosquitto, HiveMQ, and EMQX.

### The Publisher

A publisher is a client that sends data to the broker. The publisher specifies a "topic" (a string) and a "payload" (the actual data). The publisher does not know who, if anyone, is receiving the message.

### The Subscriber

A subscriber is a client that tells the broker it is interested in a particular topic. When the broker receives a message on that topic, it pushes the message to the subscriber. A single client can act as both a publisher and a subscriber.

## MQTT Topic Hierarchies and Wildcards

Topics are the routing mechanism in MQTT. They are structured as strings separated by forward slashes, creating a hierarchy similar to a file system.

### Designing Topics

A well-designed topic hierarchy allows for granular control over data flow. For example, in a cloud data center, a topic structure might look like:
`datacenter/building_1/rack_4/server_12/temperature`

### Using Wildcards

Subscribers can use wildcards to subscribe to multiple topics at once:

- **Single-level wildcard (`+`)**: Matches one level in the hierarchy.
    - `datacenter/+/rack_4/server_12/temperature` matches any building in rack 4 on server 12.
- **Multi-level wildcard (`#`)**: Matches all remaining levels in the hierarchy.
    - `datacenter/building_1/#` matches every single metric coming from building 1.

## Implementation with Paho-MQTT

The `paho-mqtt` library is the industry standard for implementing MQTT in Python.

### Installation

```bash
pip install paho-mqtt
```

### Implementing an MQTT Subscriber

Subscribers in `paho-mqtt` are typically implemented using a callback-based approach. The `on_message` function is triggered whenever the broker pushes a message to the client.

Example: A basic MQTT subscriber.

```python
import paho.mqtt.client as mqtt

# Callback triggered when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to a specific topic upon connection
    client.subscribe("cloudmesh/sensors/temperature")

# Callback triggered when a message is received
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} | Payload: {msg.payload.decode()}")

# Initialize the client
client = mqtt.Client()

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to a public broker (for testing purposes)
client.connect("mqtt.eclipseprojects.io", 1883, 60)

# Start the network loop to process incoming messages
client.loop_forever()
```

### Implementing an MQTT Publisher

Publishers are simpler as they do not need to maintain a persistent listener loop for incoming messages.

Example: A basic MQTT publisher.

```python
import paho.mqtt.client as mqtt
import time
import random

# Initialize the client
client = mqtt.Client()

# Connect to the broker
client.connect("mqtt.eclipseprojects.io", 1883, 60)

# Simulate sensor data
try:
    while True:
        temp = round(random.uniform(20.0, 25.0), 2)
        payload = f"Temperature: {temp}C"
        
        # Publish message to topic
        result = client.publish("cloudmesh/sensors/temperature", payload)
        
        # Check if publish was successful
        status = result[0]
        if status == 0:
            print(f"Published: {payload}")
        else:
            print(f"Failed to send message to topic")
            
        time.sleep(5)
except KeyboardInterrupt:
    client.disconnect()
```

## Quality of Service (QoS)

MQTT provides three levels of Quality of Service to ensure that messages are delivered according to the reliability needs of the application.

### QoS 0: At most once (Fire and Forget)

The message is sent once. There is no acknowledgment from the receiver. If the network drops, the message is lost. This is used for high-frequency, non-critical data (e.g., a temperature reading every second).

### QoS 1: At least once (Acknowledged Delivery)

The broker ensures the message reaches the subscriber at least once. This is achieved through an acknowledgment (PUBACK). If the publisher doesn't receive the ACK, it sends the message again. This may result in duplicate messages.

### QoS 2: Exactly once (Assured Delivery)

The highest and slowest level. It uses a four-step handshake to ensure that the message is delivered exactly once, without duplicates. This is critical for financial transactions or control commands (e.g., "Open Valve").

## Advanced MQTT Features

### Retained Messages

By default, a subscriber only receives messages published *after* it connects. A **Retained Message** is a message that the broker stores. When a new subscriber connects to that topic, the broker immediately sends the last retained message. This is useful for "Last Known Good" state (e.g., "System Status: ONLINE").

Example: Publishing a retained message.

```python
# The 'retain=True' flag tells the broker to store this as the last known state
client.publish("cloudmesh/status", "ONLINE", retain=True)
```

### Last Will and Testament (LWT)

LWT allows a client to tell the broker: "If I disconnect unexpectedly, publish this message on my behalf." This is the primary way to detect device failures in a cloud environment.

Example: Setting a Last Will.

```python
# Define the Will before connecting
client.will_set("cloudmesh/status/device_01", payload="OFFLINE", qos=1, retain=True)

# Now connect
client.connect("mqtt.eclipseprojects.io", 1883, 60)
```

## Security in MQTT

Because MQTT is often used over public networks, security is mandatory.

- **Authentication**: Use `client.username_pw_set("username", "password")` to authenticate with the broker.
- **Encryption (TLS/SSL)**: Use `client.tls_set()` to wrap the connection in TLS. This prevents eavesdropping and Man-in-the-Middle (MITM) attacks.

Example: Configuring TLS and authentication.

```python
client = mqtt.Client()
client.username_pw_set("my_user", "my_password")

# Load system default CA certificates for TLS
client.tls_set() 

client.connect("secure-broker.example.com", 8883)
```

!!! tip "Summary Checklist"
    - Selected the correct architecture: Pub/Sub via a Broker.
    - Designed a hierarchical topic structure using `/` and wildcards (`+`, `#`).
    - Implemented `on_connect` and `on_message` callbacks for subscribers.
    - Chose the appropriate QoS level (0, 1, or 2) based on reliability requirements.
    - Configured Retained messages for state management.
    - Set a Last Will and Testament (LWT) to monitor device availability.
    - Secured the connection using TLS/SSL and username/password authentication.


## Self Assessment

Test your knowledge by expanding the questions below.

??? question "Contrast the Request-Response model with the Pub/Sub model used by MQTT."
    In Request-Response (e.g., HTTP), a client explicitly asks for data and waits for a server's response. In Pub/Sub (MQTT), publishers send messages to topics on a broker, and any subscriber interested in that topic receives the message asynchronously, without the publisher knowing who the subscribers are.

??? question "What is the purpose of MQTT wildcards, and how do `+` and `#` differ?"
    Wildcards allow subscribers to monitor multiple topics. The single-level wildcard (`+`) matches exactly one level in the hierarchy, while the multi-level wildcard (`#`) matches all remaining levels from that point forward.

??? question "Explain the difference between QoS 0, QoS 1, and QoS 2."
    QoS 0 (At most once) delivers the message once with no acknowledgment. QoS 1 (At least once) ensures delivery via acknowledgment but may result in duplicates. QoS 2 (Exactly once) uses a four-step handshake to ensure the message is delivered exactly once without duplicates.

## Assignments


!!! note "Assignment 1: Basic Telemetry System"
    Create a publisher that sends a random "CPU Load" percentage every 2 seconds to the topic `cloudmesh/metrics/cpu`. Create a subscriber that prints these values in real-time.

!!! note "Assignment 2: Multi-Sensor Monitor"
    Implement a subscriber that uses a wildcard to monitor all sensors in a building. Use the topic `cloudmesh/building_1/+/value`. The subscriber should print the sensor name (extracted from the topic) and the value.

!!! note "Assignment 3: Robust IoT Gateway"
    Develop a system that implements the following:
    1. A publisher that sets an LWT message to "DISCONNECTED" on the topic `gateway/status`.
    2. The publisher sends heartbeats every 10 seconds using QoS 1.
    3. The publisher uses a Retained message to signal its current "Config Version".
    4. A subscriber that monitors `gateway/status` and alerts the user if a device goes OFFLINE.
