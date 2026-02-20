#!/usr/bin/env python3
"""
Socket Arsenal — Protocol Handler
Classification: OMEGA-LEVEL
Date: 2026-02-20 23:01 UTC
Purpose: Custom application-layer protocol for encrypted socket communication

Protocol Design (based on RealPython guide):
- 2-byte fixed header (JSON header length, network byte order)
- Variable-length JSON header (metadata)
- Binary payload (encrypted content)

Features:
- Structured message framing
- Binary and JSON content support
- Endianness handling
- Streaming message construction
"""

import struct
import json
import sys
from typing import Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """Content type identifiers."""
    JSON = "text/json"
    BINARY = "application/octet-stream"
    ENCRYPTED = "binary/xchacha20"
    TEXT = "text/plain"


@dataclass
class Message:
    """Structured message container."""
    content: Union[bytes, Dict, str]
    content_type: ContentType = ContentType.BINARY
    content_encoding: str = "binary"
    metadata: Dict[str, Any] = None
    byteorder: str = sys.byteorder
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ProtocolHandler:
    """
    Handles encoding/decoding of custom application protocol.
    
    Message Format:
    [2 bytes: header length] [JSON header] [payload]
    """
    
    PROTOCOL_VERSION = "1.0"
    HEADER_SIZE = 2  # Fixed header size in bytes
    
    def __init__(self):
        """Initialize protocol handler."""
        self._buffer = b""
        self._jsonheader_len = None
        self._jsonheader = None
        self._content_len = None
    
    def encode(self, message: Message) -> bytes:
        """
        Encode message to wire format.
        
        Args:
            message: Message to encode
            
        Returns:
            Complete wire-format message
        """
        # Encode content based on type
        if message.content_type == ContentType.JSON:
            content_bytes = json.dumps(message.content).encode(message.content_encoding)
        elif message.content_type == ContentType.TEXT:
            content_bytes = message.content.encode(message.content_encoding)
        else:
            # Binary content
            content_bytes = message.content if isinstance(message.content, bytes) else bytes(message.content)
        
        # Build JSON header
        jsonheader = {
            "byteorder": message.byteorder,
            "content-type": message.content_type.value,
            "content-encoding": message.content_encoding,
            "content-length": len(content_bytes),
            "protocol-version": self.PROTOCOL_VERSION,
            **message.metadata
        }
        
        jsonheader_bytes = json.dumps(jsonheader).encode("utf-8")
        
        # Build fixed header (2-byte length of JSON header)
        fixed_header = struct.pack(">H", len(jsonheader_bytes))
        
        # Assemble complete message
        message_bytes = fixed_header + jsonheader_bytes + content_bytes
        
        return message_bytes
    
    def decode(self, data: bytes) -> Optional[Message]:
        """
        Decode message from wire format.
        
        Args:
            data: Raw bytes received
            
        Returns:
            Decoded Message if complete, None if more data needed
        """
        self._buffer += data
        
        # Step 1: Get fixed header (2 bytes)
        if self._jsonheader_len is None:
            if len(self._buffer) >= self.HEADER_SIZE:
                self._jsonheader_len = struct.unpack(">H", self._buffer[:self.HEADER_SIZE])[0]
                self._buffer = self._buffer[self.HEADER_SIZE:]
            else:
                return None  # Need more data
        
        # Step 2: Get JSON header
        if self._jsonheader is None:
            if len(self._buffer) >= self._jsonheader_len:
                jsonheader_bytes = self._buffer[:self._jsonheader_len]
                self._jsonheader = json.loads(jsonheader_bytes.decode("utf-8"))
                self._content_len = self._jsonheader["content-length"]
                self._buffer = self._buffer[self._jsonheader_len:]
            else:
                return None  # Need more data
        
        # Step 3: Get content
        if len(self._buffer) >= self._content_len:
            content_bytes = self._buffer[:self._content_len]
            self._buffer = self._buffer[self._content_len:]
            
            # Decode content based on type
            content_type_str = self._jsonheader["content-type"]
            content_encoding = self._jsonheader["content-encoding"]
            byteorder = self._jsonheader.get("byteorder", sys.byteorder)
            
            # Parse content type
            if content_type_str == ContentType.JSON.value:
                content = json.loads(content_bytes.decode(content_encoding))
                content_type = ContentType.JSON
            elif content_type_str == ContentType.TEXT.value:
                content = content_bytes.decode(content_encoding)
                content_type = ContentType.TEXT
            else:
                content = content_bytes
                content_type = ContentType.BINARY
            
            # Build metadata (excluding protocol fields)
            metadata = {k: v for k, v in self._jsonheader.items() 
                       if k not in ["byteorder", "content-type", "content-encoding", "content-length", "protocol-version"]}
            
            # Reset state for next message
            self._reset()
            
            return Message(
                content=content,
                content_type=content_type,
                content_encoding=content_encoding,
                metadata=metadata,
                byteorder=byteorder
            )
        else:
            return None  # Need more data
    
    def _reset(self):
        """Reset decoder state for next message."""
        self._jsonheader_len = None
        self._jsonheader = None
        self._content_len = None
    
    def has_partial(self) -> bool:
        """Check if decoder has partial message buffered."""
        return len(self._buffer) > 0 or self._jsonheader_len is not None
    
    @staticmethod
    def create_encrypted_message(encrypted_payload: bytes, probe_id: str, 
                                  encryption_type: str = "xchacha20-poly1305",
                                  metadata: Optional[Dict] = None) -> Message:
        """
        Create pre-encrypted message for secure transmission.
        
        Args:
            encrypted_payload: Already-encrypted content
            probe_id: Probe identifier
            encryption_type: Encryption algorithm used
            metadata: Additional metadata
            
        Returns:
            Message ready for encoding
        """
        meta = {
            "probe-id": probe_id,
            "encryption": encryption_type,
            "timestamp": None,  # Should be set by caller
            **(metadata or {})
        }
        
        return Message(
            content=encrypted_payload,
            content_type=ContentType.ENCRYPTED,
            content_encoding="binary",
            metadata=meta
        )
    
    @staticmethod
    def create_json_message(data: Dict, metadata: Optional[Dict] = None) -> Message:
        """Create JSON message."""
        return Message(
            content=data,
            content_type=ContentType.JSON,
            content_encoding="utf-8",
            metadata=metadata or {}
        )


# Example usage
if __name__ == '__main__':
    print("Protocol Handler — Test Sequence")
    print("=" * 50)
    
    handler = ProtocolHandler()
    
    # Test 1: Binary message
    print("\n[Test 1] Binary message:")
    msg1 = Message(content=b"Secret probe data", content_type=ContentType.BINARY)
    encoded1 = handler.encode(msg1)
    print(f"Encoded: {encoded1[:20]}... ({len(encoded1)} bytes)")
    
    decoded1 = handler.decode(encoded1)
    print(f"Decoded: {decoded1.content[:20]}...")
    print(f"Type: {decoded1.content_type}")
    
    # Test 2: JSON message
    print("\n[Test 2] JSON message:")
    msg2 = Message(
        content={"probe-id": "NP-001", "status": "active", "targets": 47},
        content_type=ContentType.JSON,
        metadata={"mission": "recon", "level": "omega"}
    )
    encoded2 = handler.encode(msg2)
    print(f"Encoded: {encoded2[:40]}...")
    
    decoded2 = handler.decode(encoded2)
    print(f"Decoded: {decoded2.content}")
    print(f"Metadata: {decoded2.metadata}")
    
    # Test 3: Encrypted message
    print("\n[Test 3] Encrypted message:")
    msg3 = ProtocolHandler.create_encrypted_message(
        encrypted_payload=b"\x00\x01\x02\x03...encrypted...",
        probe_id="NP-ALPHA",
        encryption_type="xchacha20-poly1305",
        metadata={"target": "178.62.233.87", "layer": 3}
    )
    encoded3 = handler.encode(msg3)
    print(f"Encoded length: {len(encoded3)} bytes")
    
    decoded3 = handler.decode(encoded3)
    print(f"Probe ID: {decoded3.metadata.get('probe-id')}")
    print(f"Encryption: {decoded3.metadata.get('encryption')}")
    
    print("\n" + "=" * 50)
    print("Protocol Handler ready for Socket Arsenal integration.")
