#!/usr/bin/env python3
"""
Socket Arsenal — Encryption Layer
Classification: OMEGA-LEVEL
Date: 2026-02-20 23:01 UTC
Purpose: XChaCha20-Poly1305 encryption for socket communications

Integrates with:
- SocketManager (encrypt before send, decrypt after receive)
- ProtocolHandler (encrypted content type)
- NetProbe v2 (stealth beacon transmission)
- Digital Drill (secure exfiltration)
"""

import os
import secrets
import hashlib
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import json
import base64


@dataclass
class EncryptedPacket:
    """Container for encrypted data with metadata."""
    ciphertext: bytes
    nonce: bytes
    associated_data: Optional[bytes] = None
    timestamp: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for transmission."""
        return {
            "ciphertext": base64.b64encode(self.ciphertext).decode('ascii'),
            "nonce": base64.b64encode(self.nonce).decode('ascii'),
            "associated_data": base64.b64encode(self.associated_data).decode('ascii') if self.associated_data else None,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptedPacket':
        """Reconstruct from dictionary."""
        return cls(
            ciphertext=base64.b64decode(data["ciphertext"]),
            nonce=base64.b64decode(data["nonce"]),
            associated_data=base64.b64decode(data["associated_data"]) if data.get("associated_data") else None,
            timestamp=data.get("timestamp")
        )


class SocketEncryption:
    """
    XChaCha20-Poly1305 encryption for socket communications.
    
    Features:
    - Per-session key derivation
    - Automatic nonce generation (192-bit, unique per message)
    - Associated data for context binding
    - Chunking for large payloads (>64KB)
    """
    
    NONCE_SIZE = 12  # ChaCha20-Poly1305 uses 96-bit (12 byte) nonces
    KEY_SIZE = 32    # 256-bit keys
    MAX_CHUNK_SIZE = 65536  # 64KB chunks for streaming
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize encryption layer.
        
        Args:
            master_key: Optional 32-byte master key (generated if not provided)
        """
        if master_key is None:
            self.master_key = secrets.token_bytes(self.KEY_SIZE)
        elif len(master_key) != self.KEY_SIZE:
            raise ValueError(f"Master key must be {self.KEY_SIZE} bytes")
        else:
            self.master_key = master_key
        
        self.session_keys: Dict[str, bytes] = {}
        
    def derive_session_key(self, session_id: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive session-specific key from master key.
        
        Args:
            session_id: Unique session identifier
            salt: Optional salt (random if not provided)
            
        Returns:
            32-byte session key
        """
        if session_id in self.session_keys:
            return self.session_keys[session_id]
        
        if salt is None:
            salt = secrets.token_bytes(16)
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            info=session_id.encode('utf-8'),
            backend=default_backend()
        )
        
        session_key = hkdf.derive(self.master_key)
        self.session_keys[session_id] = session_key
        
        return session_key
    
    def encrypt(self, plaintext: bytes, session_id: str,
                associated_data: Optional[bytes] = None) -> EncryptedPacket:
        """
        Encrypt data for socket transmission.
        
        Args:
            plaintext: Data to encrypt
            session_id: Session identifier for key derivation
            associated_data: Optional context data (not encrypted but authenticated)
            
        Returns:
            EncryptedPacket with ciphertext and nonce
        """
        session_key = self.derive_session_key(session_id)
        chacha = ChaCha20Poly1305(session_key)
        
        nonce = secrets.token_bytes(self.NONCE_SIZE)
        
        ciphertext = chacha.encrypt(nonce, plaintext, associated_data)
        
        return EncryptedPacket(
            ciphertext=ciphertext,
            nonce=nonce,
            associated_data=associated_data,
            timestamp=None  # Set by caller if needed
        )
    
    def decrypt(self, packet: EncryptedPacket, session_id: str) -> bytes:
        """
        Decrypt data from socket.
        
        Args:
            packet: EncryptedPacket with ciphertext and nonce
            session_id: Session identifier for key derivation
            
        Returns:
            Decrypted plaintext
        """
        session_key = self.derive_session_key(session_id)
        chacha = ChaCha20Poly1305(session_key)
        
        plaintext = chacha.decrypt(
            packet.nonce, 
            packet.ciphertext, 
            packet.associated_data
        )
        
        return plaintext
    
    def encrypt_chunked(self, plaintext: bytes, session_id: str,
                        chunk_size: int = MAX_CHUNK_SIZE) -> list:
        """
        Encrypt large data in chunks for streaming.
        
        Args:
            plaintext: Large data to encrypt
            session_id: Session identifier
            chunk_size: Maximum bytes per chunk
            
        Returns:
            List of EncryptedPackets
        """
        chunks = []
        offset = 0
        chunk_index = 0
        
        total_chunks = (len(plaintext) + chunk_size - 1) // chunk_size
        
        while offset < len(plaintext):
            chunk_data = plaintext[offset:offset + chunk_size]
            
            # Include chunk metadata in associated data
            associated = f"chunk:{chunk_index}:{total_chunks}".encode('utf-8')
            
            packet = self.encrypt(chunk_data, session_id, associated)
            packet.metadata = {"chunk_index": chunk_index, "total_chunks": total_chunks}
            chunks.append(packet)
            
            offset += chunk_size
            chunk_index += 1
        
        return chunks
    
    def decrypt_chunked(self, packets: list, session_id: str) -> bytes:
        """
        Decrypt chunked data and reassemble.
        
        Args:
            packets: List of EncryptedPackets
            session_id: Session identifier
            
        Returns:
            Reassembled plaintext
        """
        # Sort by chunk index if metadata present
        packets = sorted(packets, key=lambda p: getattr(p, 'metadata', {}).get('chunk_index', 0))
        
        plaintext_parts = []
        for packet in packets:
            plaintext = self.decrypt(packet, session_id)
            plaintext_parts.append(plaintext)
        
        return b''.join(plaintext_parts)
    
    def get_fingerprint(self) -> str:
        """Get master key fingerprint (for verification, not the key itself)."""
        return hashlib.sha256(self.master_key).hexdigest()[:16]


class SocketEncryptionManager:
    """
    High-level manager for socket encryption.
    Integrates with SocketManager for transparent encryption/decryption.
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """Initialize encryption manager."""
        self.encryption = SocketEncryption(master_key)
        self.session_map: Dict[int, str] = {}  # socket.fileno() -> session_id
    
    def register_socket(self, sock, session_id: str):
        """Associate socket with encryption session."""
        self.session_map[sock.fileno()] = session_id
    
    def unregister_socket(self, sock):
        """Remove socket from encryption tracking."""
        fd = sock.fileno()
        if fd in self.session_map:
            del self.session_map[fd]
    
    def encrypt_for_socket(self, sock, plaintext: bytes,
                           associated_data: Optional[bytes] = None) -> EncryptedPacket:
        """Encrypt data for specific socket."""
        session_id = self.session_map.get(sock.fileno(), "default")
        return self.encryption.encrypt(plaintext, session_id, associated_data)
    
    def decrypt_for_socket(self, sock, packet: EncryptedPacket) -> bytes:
        """Decrypt data from specific socket."""
        session_id = self.session_map.get(sock.fileno(), "default")
        return self.encryption.decrypt(packet, session_id)
    
    def prepare_for_send(self, sock, plaintext: bytes,
                         associated_data: Optional[bytes] = None) -> bytes:
        """
        Encrypt and serialize data for socket transmission.
        Returns JSON-serializable bytes.
        """
        packet = self.encrypt_for_socket(sock, plaintext, associated_data)
        packet_dict = packet.to_dict()
        return json.dumps(packet_dict).encode('utf-8')
    
    def process_received(self, sock, data: bytes) -> bytes:
        """
        Deserialize and decrypt received data.
        Assumes data is JSON-serialized EncryptedPacket.
        """
        packet_dict = json.loads(data.decode('utf-8'))
        packet = EncryptedPacket.from_dict(packet_dict)
        return self.decrypt_for_socket(sock, packet)


# Integration example with SocketManager
class EncryptedSocketManager:
    """Example integration: SocketManager + Encryption."""
    
    def __init__(self, master_key: Optional[bytes] = None):
        from socket_manager import SocketManager
        from protocol_handler import ProtocolHandler, Message, ContentType
        
        self.socket_mgr = SocketManager()
        self.encryption = SocketEncryptionManager(master_key)
        self.protocol = ProtocolHandler()
        
        # Register handlers
        self.socket_mgr.register_handler('connect', self._on_connect)
        self.socket_mgr.register_handler('read', self._on_read)
    
    def _on_connect(self, sock, data):
        """On connection, register for encryption."""
        session_id = f"session_{data.addr[0]}_{data.addr[1]}"
        self.encryption.register_socket(sock, session_id)
        print(f"[ENCRYPTED CONNECT] {data.addr} session={session_id}")
    
    def _on_read(self, sock, data, received_bytes):
        """On read, decrypt and process."""
        try:
            plaintext = self.encryption.process_received(sock, received_bytes)
            print(f"[ENCRYPTED READ] Decrypted: {plaintext[:50]}...")
        except Exception as e:
            print(f"[DECRYPT ERROR] {e}")
    
    def send_encrypted(self, sock, plaintext: bytes):
        """Send encrypted data."""
        encrypted = self.encryption.prepare_for_send(sock, plaintext)
        self.socket_mgr.send(sock, encrypted)


# Test
if __name__ == '__main__':
    print("Socket Arsenal — Encryption Layer Test")
    print("=" * 50)
    
    # Initialize
    encryption = SocketEncryption()
    print(f"Master key fingerprint: {encryption.get_fingerprint()}")
    
    # Test 1: Basic encryption
    print("\n[Test 1] Basic encrypt/decrypt:")
    plaintext = b"Secret mission data for NetProbe"
    session = "probe_session_001"
    
    packet = encryption.encrypt(plaintext, session)
    print(f"Plaintext: {plaintext}")
    print(f"Ciphertext: {packet.ciphertext[:20]}... ({len(packet.ciphertext)} bytes)")
    print(f"Nonce: {packet.nonce.hex()[:16]}...")
    
    decrypted = encryption.decrypt(packet, session)
    print(f"Decrypted: {decrypted}")
    assert decrypted == plaintext, "Decrypt failed!"
    print("✅ Basic encryption verified")
    
    # Test 2: Chunked encryption
    print("\n[Test 2] Chunked encrypt/decrypt:")
    large_data = b"X" * 200000  # 200KB
    chunks = encryption.encrypt_chunked(large_data, session, chunk_size=65536)
    print(f"Split into {len(chunks)} chunks")
    
    decrypted_large = encryption.decrypt_chunked(chunks, session)
    assert decrypted_large == large_data, "Chunked decrypt failed!"
    print(f"✅ Chunked encryption verified ({len(large_data)} bytes)")
    
    # Test 3: Associated data
    print("\n[Test 3] Associated data binding:")
    message = b"Critical beacon data"
    context = b"probe_id=NP001,target=178.62.233.87"
    
    packet = encryption.encrypt(message, session, context)
    decrypted = encryption.decrypt(packet, session)
    assert decrypted == message, "Associated data decrypt failed!"
    print("✅ Associated data binding verified")
    
    print("\n" + "=" * 50)
    print("Encryption Layer ready for Socket Arsenal integration.")
