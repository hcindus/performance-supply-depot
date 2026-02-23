#!/usr/bin/env python3
"""
Socket Arsenal — Core Socket Manager
Classification: OMEGA-LEVEL
Date: 2026-02-20 23:01 UTC
Purpose: Non-blocking multi-connection socket management using selectors

Based on: RealPython Socket Programming Guide (Nathan Jennings)
Features:
- Concurrent multi-target handling
- Non-blocking I/O with selectors
- State management per connection
- Graceful error handling
- Automatic cleanup
"""

import socket
import selectors
import types
import logging
import time
from typing import Dict, Callable, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SocketArsenal')


class ConnectionState(Enum):
    """Connection lifecycle states."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    READING = "reading"
    WRITING = "writing"
    CLOSING = "closing"
    CLOSED = "closed"
    ERROR = "error"


@dataclass
class ConnectionData:
    """Per-connection state container."""
    addr: tuple
    state: ConnectionState = ConnectionState.CONNECTING
    inb: bytes = field(default_factory=bytes)  # Incoming buffer
    outb: bytes = field(default_factory=bytes)  # Outgoing buffer
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def touch(self):
        """Update last activity timestamp."""
        self.last_activity = time.time()


class SocketManager:
    """
    High-performance multi-connection socket manager.
    
    Uses selectors for efficient I/O multiplexing.
    Supports both client (outbound) and server (inbound) connections.
    """
    
    def __init__(self, timeout: Optional[float] = None):
        """
        Initialize socket manager.
        
        Args:
            timeout: Default timeout for select() operations (None = blocking)
        """
        self.selector = selectors.DefaultSelector()
        self.timeout = timeout
        self.connections: Dict[socket.socket, ConnectionData] = {}
        self.running = False
        self._handlers: Dict[str, Callable] = {}
        
        logger.info("SocketManager initialized")
    
    def register_handler(self, event: str, handler: Callable):
        """
        Register event handler.
        
        Events: 'connect', 'read', 'write', 'close', 'error'
        """
        self._handlers[event] = handler
        logger.debug(f"Handler registered for event: {event}")
    
    def connect(self, host: str, port: int, metadata: Optional[Dict] = None) -> socket.socket:
        """
        Initiate non-blocking connection to target.
        
        Args:
            host: Target hostname or IP
            port: Target port
            metadata: Optional metadata to attach to connection
            
        Returns:
            Socket object (non-blocking, not yet connected)
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        
        # Use connect_ex to avoid blocking exception
        err = sock.connect_ex((host, port))
        
        if err != 0 and err != 115:  # 115 = EINPROGRESS (normal for non-blocking)
            logger.error(f"Connection failed immediately to {host}:{port}: errno {err}")
            sock.close()
            raise OSError(f"Connection failed: {err}")
        
        # Create connection data
        data = ConnectionData(
            addr=(host, port),
            state=ConnectionState.CONNECTING,
            metadata=metadata or {}
        )
        
        # Register for both read and write (to detect connection completion)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(sock, events, data=data)
        self.connections[sock] = data
        
        logger.info(f"Connection initiated to {host}:{port}")
        return sock
    
    def listen(self, host: str, port: int, backlog: int = 100) -> socket.socket:
        """
        Create listening socket for inbound connections.
        
        Args:
            host: Bind address (use '' for all interfaces)
            port: Listen port
            backlog: Connection queue size
            
        Returns:
            Listening socket
        """
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((host, port))
        lsock.listen(backlog)
        lsock.setblocking(False)
        
        # Register for read events only
        self.selector.register(lsock, selectors.EVENT_READ, data=None)
        
        logger.info(f"Listening on {host}:{port}")
        return lsock
    
    def _accept_connection(self, lsock: socket.socket):
        """Accept new inbound connection."""
        conn, addr = lsock.accept()
        conn.setblocking(False)
        
        data = ConnectionData(addr=addr, state=ConnectionState.CONNECTED)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(conn, events, data=data)
        self.connections[conn] = data
        
        logger.info(f"Accepted connection from {addr}")
        
        if 'connect' in self._handlers:
            self._handlers['connect'](conn, data)
    
    def _handle_read(self, sock: socket.socket, data: ConnectionData):
        """Handle readable socket."""
        try:
            recv_data = sock.recv(4096)
            
            if recv_data:
                data.inb += recv_data
                data.touch()
                data.state = ConnectionState.READING
                
                logger.debug(f"Received {len(recv_data)} bytes from {data.addr}")
                
                if 'read' in self._handlers:
                    self._handlers['read'](sock, data, recv_data)
            else:
                # Client closed connection
                logger.info(f"Connection closed by peer: {data.addr}")
                self._close_connection(sock, data)
                
        except BlockingIOError:
            # Resource temporarily unavailable - normal for non-blocking
            pass
        except OSError as e:
            logger.error(f"Read error from {data.addr}: {e}")
            self._close_connection(sock, data, error=e)
    
    def _handle_write(self, sock: socket.socket, data: ConnectionData):
        """Handle writable socket."""
        # Check if this is a pending connection completion
        if data.state == ConnectionState.CONNECTING:
            # Connection completed (or failed)
            err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if err != 0:
                logger.error(f"Connection failed to {data.addr}: errno {err}")
                self._close_connection(sock, data, error=OSError(f"Connect failed: {err}"))
                return
            
            data.state = ConnectionState.CONNECTED
            logger.info(f"Connection established to {data.addr}")
            
            if 'connect' in self._handlers:
                self._handlers['connect'](sock, data)
        
        # Send any pending data
        if data.outb:
            try:
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]
                data.touch()
                data.state = ConnectionState.WRITING
                
                logger.debug(f"Sent {sent} bytes to {data.addr}")
                
                if 'write' in self._handlers:
                    self._handlers['write'](sock, data, sent)
                    
            except BlockingIOError:
                pass
            except OSError as e:
                logger.error(f"Write error to {data.addr}: {e}")
                self._close_connection(sock, data, error=e)
    
    def _close_connection(self, sock: socket.socket, data: ConnectionData, error: Optional[Exception] = None):
        """Gracefully close connection."""
        data.state = ConnectionState.CLOSING
        
        if error and 'error' in self._handlers:
            self._handlers['error'](sock, data, error)
        
        if 'close' in self._handlers:
            self._handlers['close'](sock, data)
        
        try:
            self.selector.unregister(sock)
        except Exception:
            pass
        
        try:
            sock.close()
        except Exception:
            pass
        
        if sock in self.connections:
            del self.connections[sock]
        
        data.state = ConnectionState.CLOSED
        
        if error:
            logger.warning(f"Connection to {data.addr} closed with error: {error}")
        else:
            logger.info(f"Connection to {data.addr} closed")
    
    def send(self, sock: socket.socket, data: bytes):
        """
        Queue data for sending on socket.
        
        Args:
            sock: Target socket
            data: Bytes to send
        """
        if sock in self.connections:
            self.connections[sock].outb += data
            self.connections[sock].touch()
    
    def disconnect(self, sock: socket.socket):
        """Initiate disconnection."""
        if sock in self.connections:
            self._close_connection(sock, self.connections[sock])
    
    def run(self, duration: Optional[float] = None):
        """
        Run event loop.
        
        Args:
            duration: Run for specified seconds (None = until stop())
        """
        self.running = True
        start_time = time.time()
        
        logger.info("SocketManager event loop starting")
        
        try:
            while self.running:
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    logger.info("Duration expired, stopping")
                    break
                
                # Wait for events
                events = self.selector.select(timeout=self.timeout)
                
                for key, mask in events:
                    sock = key.fileobj
                    data = key.data
                    
                    if data is None:
                        # Listening socket - accept new connection
                        self._accept_connection(sock)
                    else:
                        # Client socket - handle I/O
                        if mask & selectors.EVENT_READ:
                            self._handle_read(sock, data)
                        
                        if mask & selectors.EVENT_WRITE:
                            self._handle_write(sock, data)
                
                # Cleanup stale connections (optional, configurable)
                self._cleanup_stale()
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.shutdown()
    
    def _cleanup_stale(self, max_idle: float = 300):
        """Close connections idle for too long (default 5 minutes)."""
        now = time.time()
        stale = []
        
        for sock, data in self.connections.items():
            if now - data.last_activity > max_idle:
                stale.append((sock, data))
        
        for sock, data in stale:
            logger.warning(f"Closing stale connection to {data.addr} (idle {now - data.last_activity:.0f}s)")
            self._close_connection(sock, data)
    
    def stop(self):
        """Signal event loop to stop."""
        self.running = False
        logger.info("Stop signal received")
    
    def shutdown(self):
        """Graceful shutdown - close all connections."""
        logger.info("Shutting down SocketManager")
        
        # Close all connections
        for sock, data in list(self.connections.items()):
            self._close_connection(sock, data)
        
        # Close selector
        self.selector.close()
        
        logger.info("SocketManager shutdown complete")
    
    def get_stats(self) -> Dict:
        """Get current connection statistics."""
        states = {}
        for data in self.connections.values():
            state = data.state.value
            states[state] = states.get(state, 0) + 1
        
        return {
            'total_connections': len(self.connections),
            'states': states,
            'selector_map_size': len(self.selector.get_map()) if hasattr(self.selector, 'get_map') else 'unknown'
        }


# Example usage / test
if __name__ == '__main__':
    """Demonstrate SocketManager with echo client connections."""
    
    def on_connect(sock, data):
        print(f"[CONNECT] {data.addr}")
        # Send test message
        manager.send(sock, b"Hello from SocketArsenal!")
    
    def on_read(sock, data, received_bytes):
        print(f"[READ] {data.addr}: {received_bytes!r}")
        # Echo back
        manager.send(sock, received_bytes)
    
    def on_write(sock, data, sent_bytes):
        print(f"[WRITE] {data.addr}: {sent_bytes} bytes sent")
    
    def on_close(sock, data):
        print(f"[CLOSE] {data.addr}")
    
    def on_error(sock, data, error):
        print(f"[ERROR] {data.addr}: {error}")
    
    # Create manager
    manager = SocketManager(timeout=1.0)
    
    # Register handlers
    manager.register_handler('connect', on_connect)
    manager.register_handler('read', on_read)
    manager.register_handler('write', on_write)
    manager.register_handler('close', on_close)
    manager.register_handler('error', on_error)
    
    # Connect to example target (will fail without server, but demonstrates API)
    try:
        # This would connect to actual target
        # sock = manager.connect('127.0.0.1', 65432)
        print("SocketManager initialized successfully")
        print(f"Stats: {manager.get_stats()}")
    except Exception as e:
        print(f"Test connection failed (expected without server): {e}")
    
    print("\nSocket Arsenal Core ready for integration.")
