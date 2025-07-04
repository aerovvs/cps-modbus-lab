#!/usr/bin/env python3
"""
simple modbus tcp server for cps cybersecurity lab
controls led via gpio pin 17 using modbus coil 0
robust error handling and proper ctrl+c support
"""

import socket # tcp/ip networking - creates server socket
import struct # binary data packing/unpacking for modbus protocol
import threading # handles multiple clients
import time # delays and timeouts
import signal # catches sigint and sigterm (kill)
import sys # system functions
import os # os functions
import logging # structured logging

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
) # creates timestamped logs
logger = logging.getLogger(__name__)

# try to import gpio
try:
    from gpiozero import LED
    GPIO_AVAILABLE = True
    logger.info("gpio support enabled")
except ImportError: # sets flag and continues if not available, allows code to run on non-Pi systems
    GPIO_AVAILABLE = False
    logger.warning("gpiozero not found - running in simulation mode")

# global shutdown flag
running = True # when false, all loops stop
server_instance = None # reference to server for signal handler

class SimpleLED:
    """simple led wrapper with error handling"""
    def __init__(self, pin):
        self.pin = pin # gpio pin number
        self.led = None # holds led object
        self.state = False # tracks on/off
        
        if GPIO_AVAILABLE:
            try:
                self.led = LED(pin) # creates led controller for gpio pin
                logger.info(f"led initialized on gpio pin {pin}")
            except Exception as e:
                logger.error(f"failed to initialize led: {e}")
    
    def on(self):
        """turn led on"""
        try:
            if self.led: # only if gpio is available
                self.led.on() # turns off physical led
            self.state = True # track state
            logger.info(f"led on (pin {self.pin})")
        except Exception as e:
            logger.error(f"failed to turn led on: {e}")
    
    def off(self):
        """turn led off"""
        try:
            if self.led:
                self.led.off() # turns off physical led
            self.state = False # track state
            logger.info(f"led off (pin {self.pin})")
        except Exception as e:
            logger.error(f"failed to turn led off: {e}")
    
    def cleanup(self):
        """cleanup gpio resources"""
        try:
            if self.led:
                self.led.close() 
                logger.info("led cleanup complete")
        except Exception as e:
            logger.error(f"led cleanup error: {e}")

class SimpleModbusServer:
    """simple modbus tcp server"""
    
    def __init__(self, host='0.0.0.0', port=502):
        self.host = host # 0.0.0.0 = listen on all interfaces
        self.port = port # 502 = standard modbus port
        self.socket = None # holds tcp server socket
        self.led = SimpleLED(17)  # gpio pin 17
        
        # simple data storage
        self.coils = [False] * 100  # 100 boolean values (on/off)
        self.holding_registers = [0] * 100  # 100 16-bit integers for sensor values, settings, etc
        
    def start(self):
        """start the modbus server"""
        global running
        
        try:
            # create socket with reuse option
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPv4, SOCK_STREAM = TCP
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # SO_REUSEADDR = lets us restart server immediately
            
            # set timeout so we can check for shutdown
            self.socket.settimeout(1.0)
            
            # bind and listen
            try:
                self.socket.bind((self.host, self.port))
                self.socket.listen(5) # queue up to 5 connections
                logger.info(f"modbus server listening on {self.host}:{self.port}")
                logger.info("press ctrl+c to stop")
                logger.info("test with: mbpoll -t 0 -r 1 <ip_address> 1")
            except Exception as e:
                logger.error(f"failed to bind socket: {e}")
                return
            
            # accept connections
            while running:
                try:
                    # accept with timeout
                    client_socket, address = self.socket.accept()
                    logger.info(f"connection from {address}")
                    
                    # handle in new thread
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True # daemon threads die when main program exits
                    )
                    thread.start()
                    
                except socket.timeout:
                    # timeout is normal - check if we should shutdown
                    continue
                except OSError as e:
                    # socket was closed by signal handler
                    if not running:
                        logger.info("socket closed by shutdown signal")
                        break
                    else:
                        logger.error(f"socket error: {e}")
                except Exception as e:
                    if running:
                        logger.error(f"accept error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"server error: {e}")
        finally:
            self.cleanup()
    
    def handle_client(self, client_socket, address):
        """handle modbus client connection"""
        try:
            client_socket.settimeout(5.0)
            
            while running:
                try:
                    # read modbus tcp header (7 bytes)
                    header = client_socket.recv(7)
                    if not header or len(header) < 7:
                        break
                    
                    # parse header
                    transaction_id, protocol_id, length = struct.unpack('>HHH', header[:6])
                    unit_id = header[6]
                    
                    # read pdu
                    pdu = client_socket.recv(length - 1)
                    if not pdu:
                        break
                    
                    function_code = pdu[0] # first byte of pdu is function code
                    
                    # handle function codes
                    try:
                        if function_code == 1:  # read coils
                            response = self.read_coils(pdu)
                        elif function_code == 3:  # read holding registers
                            response = self.read_holding_registers(pdu)
                        elif function_code == 5:  # write single coil
                            response = self.write_single_coil(pdu)
                        elif function_code == 6:  # write single register
                            response = self.write_single_register(pdu)
                        else:
                            # unsupported function
                            response = bytes([function_code + 0x80, 1])  # illegal function
                    except Exception as e:
                        logger.error(f"function handler error: {e}")
                        response = bytes([function_code + 0x80, 4])  # device failure
                    
                    # send response
                    response_length = len(response) + 1  # +1 for unit id
                    response_header = struct.pack('>HHHB',
                        transaction_id, # echo back same transaction id
			protocol_id, # should be 0 for modbus
			response_length, # bytes following this field
			unit_id) # echo back unit id
                    
                    client_socket.send(response_header + response)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"request handling error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"client handler error: {e}")
        finally:
            try:
                client_socket.close()
                logger.info(f"connection closed from {address}")
            except:
                pass
    
    def read_coils(self, pdu):
        """handle read coils request (function code 1)"""
        try:
            start_address, quantity = struct.unpack('>HH', pdu[1:5])
            logger.info(f"read coils: address={start_address}, quantity={quantity}")
            
            # validate
            if start_address + quantity > len(self.coils):
                return bytes([0x81, 2])  # illegal address
            
            # prepare response
            byte_count = (quantity + 7) // 8
            response = bytes([1, byte_count])
            
            # pack coil values into bytes (8 coils per byte)
            coil_bytes = []
            for byte_num in range(byte_count):
                byte_value = 0
                for bit in range(8):
                    coil_index = start_address + byte_num * 8 + bit
                    if coil_index < start_address + quantity and self.coils[coil_index]:
                        byte_value |= (1 << bit) # set bit if coil is true
                coil_bytes.append(byte_value)
            
            return response + bytes(coil_bytes)
            
        except Exception as e:
            logger.error(f"read coils error: {e}")
            return bytes([0x81, 4])  # device failure
    
    def write_single_coil(self, pdu):
        """handle write single coil request (function code 5)"""
        try:
            address, value = struct.unpack('>HH', pdu[1:5])
	    # pdu[1:5] = 4 bytes (2 for address, 2 for value)
            logger.info(f"write single coil: address={address}, value={value:04X}")
            
            # validate
            if address >= len(self.coils):
                return bytes([0x85, 2])  # illegal address
            
            # set coil value
            coil_value = (value == 0xFF00) # 0xFF00 for ON, 0x0000 for OFF
            self.coils[address] = coil_value
            
            # control led if address 0
            if address == 0:
                if coil_value:
                    self.led.on()
                else:
                    self.led.off()
            
            # echo request as response
            return pdu
            
        except Exception as e:
            logger.error(f"write single coil error: {e}")
            return bytes([0x85, 4])  # device failure
    
    def read_holding_registers(self, pdu):
        """handle read holding registers request (function code 3)"""
        try:
            start_address, quantity = struct.unpack('>HH', pdu[1:5])
            logger.info(f"read registers: address={start_address}, quantity={quantity}")
            
            # validate
            if start_address + quantity > len(self.holding_registers):
                return bytes([0x83, 2])  # illegal address
            
            # prepare response
            byte_count = quantity * 2
            response = bytes([3, byte_count])
            
            # pack register values
            for i in range(quantity):
                reg_value = self.holding_registers[start_address + i]
                response += struct.pack('>H', reg_value)
            
            return response
            
        except Exception as e:
            logger.error(f"read registers error: {e}")
            return bytes([0x83, 4])  # device failure
    
    def write_single_register(self, pdu):
        """handle write single register request (function code 6)"""
        try:
            address, value = struct.unpack('>HH', pdu[1:5])
            logger.info(f"write single register: address={address}, value={value}")
            
            # validate
            if address >= len(self.holding_registers):
                return bytes([0x86, 2])  # illegal address
            
            # set register value
            self.holding_registers[address] = value
            
            # echo request as response
            return pdu
            
        except Exception as e:
            logger.error(f"write single register error: {e}")
            return bytes([0x86, 4])  # device failure
    
    def cleanup(self):
        """cleanup resources"""
        try:
            if self.socket:
                try:
                    self.socket.close()
                    logger.info("socket closed")
                except OSError:
                    # socket already closed
                    pass
        except Exception as e:
            logger.error(f"socket cleanup error: {e}")
        
        try:
            self.led.cleanup()
        except Exception as e:
            logger.error(f"led cleanup error: {e}")

def signal_handler(signum, frame):
    """handle ctrl+c gracefully"""
    global running, server_instance
    print("\n")  # newline for cleaner output after ^C
    logger.info(f"received signal {signum}, shutting down...")
    running = False # tell all loops to stop
    
    # force close the server socket to unblock accept()
    try:
        if server_instance and server_instance.socket:
            server_instance.socket.close()
    except:
        pass
    
    # force exit after a short delay
    def force_exit():
        time.sleep(0.5)
        print("forced shutdown complete")
        os._exit(0)
    
    threading.Thread(target=force_exit, daemon=True).start()

def main():
    """main entry point"""
    global running, server_instance
    
    # setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=== cps modbus security lab server ===")
    logger.info("simple modbus tcp server with gpio control")
    
    # test led
    try:
        logger.info("testing led...")
        test_led = SimpleLED(17)
        test_led.on()
        time.sleep(0.5)
        test_led.off()
        test_led.cleanup()
        logger.info("led test complete")
    except Exception as e:
        logger.error(f"led test failed: {e}")
    
    # create and start server
    try:
        server_instance = SimpleModbusServer(host='0.0.0.0', port=502)
        logger.info("starting modbus server...")
        server_instance.start()
    except KeyboardInterrupt:
        logger.info("keyboard interrupt")
    except Exception as e:
        logger.error(f"server error: {e}")
    finally:
        running = False
        logger.info("shutdown complete")

if __name__ == "__main__":
    main()
