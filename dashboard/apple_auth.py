"""
Apple Authentication Module - GrandSlam SRP-6a Protocol
Handles Apple ID login, 2FA verification, and iTunes Store token management.
Based on proven GrandSlam implementation (JJTech0130).
"""
import hashlib
import hmac as hmac_module
import json
import logging
import os
import time
import uuid
import base64
from urllib.parse import urlencode

import requests
import plistlib

logger = logging.getLogger(__name__)

# Try importing SRP library with Apple-specific configuration
try:
    import srp._pysrp as srp
    srp.rfc5054_enable()
    srp.no_username_in_x()
    SRP_AVAILABLE = True
    logger.info("SRP library loaded with Apple-compatible config (rfc5054, no_username_in_x)")
except ImportError:
    SRP_AVAILABLE = False
    logger.warning("SRP library not available. Apple auth will not work.")

# Try importing cryptography for AES-CBC decryption
try:
    from cryptography.hazmat.primitives import padding as crypto_padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("cryptography library not available. Session decryption will be limited.")


def encrypt_password(password, salt, iterations, protocol):
    """
    Derive SRP password using Apple's s2k/s2k_fo protocol.
    
    For s2k: SHA256(password) -> PBKDF2-SHA256(hash, salt, iterations)
    For s2k_fo: SHA256(password) -> hex encode -> PBKDF2-SHA256(hex_hash, salt, iterations)
    """
    p = hashlib.sha256(password.encode("utf-8")).digest()
    if protocol == "s2k_fo":
        # s2k_fo: convert SHA256 digest to hex string (without null terminator), then to bytes
        p = p.hex().encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", p, salt, iterations, 32)


def create_session_key(usr, name):
    """Create HMAC-SHA256 session key from SRP shared session key."""
    k = usr.get_session_key()
    if k is None:
        raise Exception("No SRP session key available")
    return hmac_module.new(k, name.encode(), hashlib.sha256).digest()


def decrypt_cbc(usr, data):
    """Decrypt AES-CBC encrypted session data using SRP session key."""
    if not CRYPTO_AVAILABLE:
        raise Exception("cryptography library required for session decryption")
    
    extra_data_key = create_session_key(usr, "extra data key:")
    extra_data_iv = create_session_key(usr, "extra data iv:")
    extra_data_iv = extra_data_iv[:16]  # Only first 16 bytes for IV
    
    cipher = Cipher(algorithms.AES(extra_data_key), modes.CBC(extra_data_iv))
    decryptor = cipher.decryptor()
    data = decryptor.update(data) + decryptor.finalize()
    
    # Remove PKCS#7 padding
    padder = crypto_padding.PKCS7(128).unpadder()
    return padder.update(data) + padder.finalize()


class AppleAuthClient:
    """
    Client for Apple GrandSlam (SRP-6a) authentication.
    Implements the correct Apple SRP protocol with PBKDF2 password derivation
    and AES-CBC session data decryption.
    """

    # Apple authentication endpoints
    GSA_ENDPOINT = "https://gsa.apple.com/grandslam/GsService2"
    VERIFY_TRUSTEDDEVICE = "https://gsa.apple.com/auth/verify/trusteddevice"
    VALIDATE_ENDPOINT = "https://gsa.apple.com/grandslam/GsService2/validate"
    VERIFY_PHONE = "https://gsa.apple.com/auth/verify/phone/"
    VERIFY_PHONE_CODE = "https://gsa.apple.com/auth/verify/phone/securitycode"
    
    # iTunes Store auth (fallback)
    ITUNES_AUTH_ENDPOINT = "https://buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/authenticate"
    
    # Apple Store endpoints
    BUY_PRODUCT_ENDPOINT = "https://{pod}-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/buyProduct"
    LOOKUP_ENDPOINT = "https://itunes.apple.com/lookup"
    
    # Default storefront (Vietnam)
    DEFAULT_STOREFRONT = "143465-19,32"
    
    # User-Agent mimicking macOS
    USER_AGENT = "akd/1.0 CFNetwork/978.0.7 Darwin/18.7.0"
    GSA_CLIENT_INFO = "<MacBookPro13,2> <macOS;13.1;22C65> <com.apple.AuthKit/1 (com.apple.dt.Xcode/3594.4.19)>"
    STORE_USER_AGENT = "AppStore/3.0 iOS/17.4 model/iPhone15,2 hwp/t8120 build/21E219 (6; dt:251)"
    
    def __init__(self, anisette_url="http://anisette:6969", proxy=None):
        self.anisette_url = anisette_url
        self.proxy = proxy
        self.session = requests.Session()
        self.session_id = str(uuid.uuid4())
        
        # Configure proxy
        if proxy:
            self._configure_proxy(proxy)
        
        # Authentication state
        self.authenticated = False
        self.ds_person_id = None
        self.gs_token = None
        self.idms_token = None
        self.auth_cookies = {}
        self.itunes_token = None
        self.store_front = self.DEFAULT_STOREFRONT
        
        # SRP state (persisted between login and 2FA)
        self._srp_user = None
        self._spd = None
        
    def _configure_proxy(self, proxy_string):
        """Configure session proxy from various formats."""
        if not proxy_string:
            return
        
        proxy_string = proxy_string.strip()
        
        # Auto-prefix if no protocol specified
        if not proxy_string.startswith(('socks5://', 'socks4://', 'http://', 'https://')):
            proxy_string = f'socks5://{proxy_string}'
        
        proxies = {
            'http': proxy_string,
            'https': proxy_string
        }
        self.session.proxies.update(proxies)
        safe_proxy = proxy_string.split('@')[-1] if '@' in proxy_string else proxy_string
        logger.info(f"Proxy configured: {safe_proxy}")
    
    def get_anisette_headers(self):
        """Fetch Anisette device metadata headers from local Anisette Server."""
        try:
            r = requests.get(f"{self.anisette_url}/", timeout=5)
            if r.status_code == 200:
                data = r.json()
                headers = {}
                # Map Anisette server response to Apple headers
                header_mapping = {
                    'X-Apple-I-MD': 'X-Apple-I-MD',
                    'X-Apple-I-MD-M': 'X-Apple-I-MD-M',
                    'X-Apple-I-MD-RINFO': 'X-Apple-I-MD-RINFO',
                    'X-Apple-I-MD-LU': 'X-Apple-I-MD-LU',
                    'X-Apple-I-SRL-NO': 'X-Apple-I-SRL-NO',
                    'X-Mme-Client-Info': 'X-Mme-Client-Info',
                    'X-MMe-Client-Info': 'X-MMe-Client-Info',
                    'X-Mme-Device-Id': 'X-Mme-Device-Id',
                    'X-Apple-I-TimeZone': 'X-Apple-I-TimeZone',
                    'X-Apple-I-Client-Time': 'X-Apple-I-Client-Time',
                    'X-Apple-Locale': 'X-Apple-Locale',
                }
                for src_key, dst_key in header_mapping.items():
                    if src_key in data:
                        headers[dst_key] = str(data[src_key])
                
                # Ensure client info key consistency
                client_info = data.get('X-MMe-Client-Info') or data.get('X-Mme-Client-Info')
                if client_info:
                    headers['X-MMe-Client-Info'] = str(client_info)
                    headers['X-Mme-Client-Info'] = str(client_info)
                
                if headers:
                    logger.info("Anisette headers fetched successfully")
                    return headers
                    
                # Fallback: try direct header format
                return {k: str(v) for k, v in data.items() if k.startswith('X-')}
        except Exception as e:
            logger.warning(f"Failed to fetch Anisette headers: {e}")
        
        # Return minimal fallback headers
        device_id = str(uuid.uuid4()).upper()
        return {
            'X-Apple-I-MD': 'AAAABQAAABCXL...',
            'X-Apple-I-MD-M': 'AAAABQAAABCXL...',
            'X-Apple-I-MD-RINFO': '17106176',
            'X-Mme-Device-Id': device_id,
            'X-Mme-Client-Info': self.GSA_CLIENT_INFO,
            'X-MMe-Client-Info': self.GSA_CLIENT_INFO,
            'X-Apple-I-TimeZone': 'Asia/Ho_Chi_Minh',
            'X-Apple-I-Client-Time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'X-Apple-Locale': 'en_US',
        }
    
    def _generate_cpd(self, anisette):
        """Generate cpd (client provided data) for GrandSlam requests."""
        cpd = {
            'bootstrap': True,
            'icscrec': True,
            'pbe': False,
            'prkgen': True,
            'svct': 'iCloud',
            'loc': anisette.get('X-Apple-Locale', 'en_US'),
        }
        cpd.update(anisette)
        return cpd
    
    def _gsa_request(self, parameters, anisette):
        """
        Send authenticated request to Apple GrandSlam endpoint.
        Returns the Response dict from the plist response.
        """
        body = {
            'Header': {'Version': '1.0.1'},
            'Request': {'cpd': self._generate_cpd(anisette)},
        }
        body['Request'].update(parameters)
        
        client_info = anisette.get('X-MMe-Client-Info') or anisette.get('X-Mme-Client-Info') or self.GSA_CLIENT_INFO
        
        headers = {
            'Content-Type': 'text/x-xml-plist',
            'Accept': '*/*',
            'User-Agent': self.USER_AGENT,
            'X-MMe-Client-Info': client_info,
            'X-Mme-Client-Info': client_info,
        }
        headers.update(anisette)
        
        resp = self.session.post(
            self.GSA_ENDPOINT,
            headers=headers,
            data=plistlib.dumps(body),
            verify=False,
            timeout=15,
        )
        
        logger.info(f"GSA response status: {resp.status_code}")
        
        if resp.status_code != 200:
            raise Exception(f"GSA request failed with HTTP {resp.status_code}: {resp.text[:200]}")
        
        parsed = plistlib.loads(resp.content)
        return parsed.get('Response', {})
    
    def login(self, apple_id, password):
        """
        Authenticate with Apple ID using GrandSlam SRP-6a protocol.
        
        This is a two-phase SRP exchange:
        1. init: Send A (client public key) → receive salt, B (server public key), iterations, protocol
        2. complete: Derive password with PBKDF2, compute M1 → receive M2, encrypted session data
        
        Returns:
            dict with login result including success, requires_2fa, session_id, message
        """
        if not SRP_AVAILABLE:
            return {
                'success': False,
                'requires_2fa': False,
                'session_id': self.session_id,
                'message': 'SRP library không khả dụng. Cần cài đặt: pip install srp'
            }
        
        anisette = self.get_anisette_headers()
        
        try:
            # Phase 1: SRP init
            # Create SRP user with empty password (will be set after receiving salt)
            usr = srp.User(apple_id, bytes(), hash_alg=srp.SHA256, ng_type=srp.NG_2048)
            _, A = usr.start_authentication()
            
            logger.info(f"SRP Phase 1: Sending init for {apple_id}")
            
            r = self._gsa_request(
                {'A2k': A, 'ps': ['s2k', 's2k_fo'], 'u': apple_id, 'o': 'init'},
                anisette
            )
            
            # Check for errors in response
            status = r.get('Status', {})
            if status.get('ec', 0) != 0:
                error_msg = status.get('em', 'Unknown error')
                error_code = status.get('ec', -1)
                logger.error(f"SRP init error: ec={error_code}, em={error_msg}")
                return {
                    'success': False,
                    'requires_2fa': False,
                    'session_id': self.session_id,
                    'message': f'Apple SRP init error: {error_msg} (code: {error_code})'
                }
            
            # Validate response has required SRP parameters
            if 'sp' not in r:
                logger.error(f"SRP init response missing 'sp': {list(r.keys())}")
                return {
                    'success': False,
                    'requires_2fa': False,
                    'session_id': self.session_id,
                    'message': f'SRP init failed: server did not return protocol. Keys: {list(r.keys())}'
                }
            
            protocol = r['sp']
            if protocol not in ['s2k', 's2k_fo']:
                return {
                    'success': False,
                    'requires_2fa': False,
                    'session_id': self.session_id,
                    'message': f'Unsupported SRP protocol: {protocol}'
                }
            
            logger.info(f"SRP Phase 1 OK: protocol={protocol}, iterations={r.get('i', 'N/A')}")
            
            # Phase 2: Compute password with PBKDF2 and complete SRP
            # Apple uses PBKDF2 to derive the password from salt + iterations
            usr.p = encrypt_password(password, r['s'], r['i'], protocol)
            
            M = usr.process_challenge(r['s'], r['B'])
            if M is None:
                return {
                    'success': False,
                    'requires_2fa': False,
                    'session_id': self.session_id,
                    'message': 'SRP challenge failed. Kiểm tra lại password.'
                }
            
            logger.info("SRP Phase 2: Sending complete with M1")
            
            r2 = self._gsa_request(
                {'c': r['c'], 'M1': M, 'u': apple_id, 'o': 'complete'},
                anisette
            )
            
            # Check for errors
            status2 = r2.get('Status', {})
            error_code2 = status2.get('ec', 0)
            
            if error_code2 != 0:
                error_msg2 = status2.get('em', 'Unknown error')
                logger.error(f"SRP complete error: ec={error_code2}, em={error_msg2}")
                
                # Error code -20209 = 2FA required
                if error_code2 == -20209:
                    return {
                        'success': False,
                        'requires_2fa': True,
                        'session_id': self.session_id,
                        'message': 'Apple yêu cầu xác minh 2FA.'
                    }
                
                return {
                    'success': False,
                    'requires_2fa': False,
                    'session_id': self.session_id,
                    'message': f'SRP complete error: {error_msg2} (code: {error_code2})'
                }
            
            # Verify server's session key matches ours
            if 'M2' in r2:
                usr.verify_session(r2['M2'])
                if not usr.authenticated():
                    return {
                        'success': False,
                        'requires_2fa': False,
                        'session_id': self.session_id,
                        'message': 'SRP session verification failed (server impersonation detected).'
                    }
                logger.info("SRP session verified successfully")
            
            # Decrypt session personal data (spd) 
            spd = None
            if 'spd' in r2 and CRYPTO_AVAILABLE:
                try:
                    spd_raw = decrypt_cbc(usr, r2['spd'])
                    spd = plistlib.loads(spd_raw, fmt=plistlib.FMT_XML)
                    logger.info(f"SPD decrypted: keys={list(spd.keys())}")
                except Exception as e:
                    logger.warning(f"SPD decryption failed: {e}")
                    spd = {}
            elif 'spd' in r2:
                logger.warning("SPD present but cryptography library not available for decryption")
                spd = {}
            
            # Save SRP state for potential 2FA flow
            self._srp_user = usr
            self._spd = spd
            
            # Extract tokens from spd
            if spd:
                self.ds_person_id = str(spd.get('adsid', spd.get('dsid', '')))
                self.idms_token = spd.get('GsIdmsToken', spd.get('idms_token', ''))
                self.gs_token = spd.get('GsIdmsToken', '')
                self.itunes_token = spd.get('passwordToken', spd.get('t', {}).get('com.apple.gs.idms.pet', {}).get('token', ''))
                
                logger.info(f"Auth tokens: dsid={self.ds_person_id}, has_idms={bool(self.idms_token)}, has_token={bool(self.itunes_token)}")
            
            # Check if 2FA is required
            # If we got tokens but account has 2FA enabled, Apple requires code verification
            np = r2.get('np', '')  # "next protocol" indicator
            if spd and self.ds_person_id and self.idms_token:
                # We got tokens - try triggering 2FA on trusted devices
                try:
                    self._trigger_2fa(self.ds_person_id, self.idms_token, anisette)
                    logger.info("2FA trigger sent to trusted devices")
                except Exception as e:
                    logger.warning(f"2FA trigger failed (may not be needed): {e}")
                
                return {
                    'success': False,
                    'requires_2fa': True,
                    'session_id': self.session_id,
                    'message': 'Đăng nhập thành công! Vui lòng nhập mã 2FA 6 số từ thiết bị Apple tin cậy.',
                    'account_info': {
                        'apple_id': apple_id,
                        'ds_person_id': self.ds_person_id,
                    }
                }
            
            # If no 2FA required (rare), mark as authenticated
            self.authenticated = True
            return {
                'success': True,
                'requires_2fa': False,
                'session_id': self.session_id,
                'message': 'Đăng nhập Apple ID thành công!',
                'account_info': {
                    'apple_id': apple_id,
                    'ds_person_id': self.ds_person_id,
                    'token_preview': (self.itunes_token or self.gs_token or '')[:20] + '...',
                }
            }
            
        except Exception as e:
            logger.error(f"Apple login error: {e}", exc_info=True)
            return {
                'success': False,
                'requires_2fa': False,
                'session_id': self.session_id,
                'message': f'Login error: {str(e)}'
            }
    
    def _trigger_2fa(self, dsid, idms_token, anisette):
        """
        Trigger 2FA prompt on trusted Apple devices.
        This sends a GET request to the verify/trusteddevice endpoint
        which causes a popup on the user's iPhone/Mac.
        """
        identity_token = base64.b64encode(
            (str(dsid) + ":" + idms_token).encode()
        ).decode()
        
        headers = {
            'Content-Type': 'text/x-xml-plist',
            'User-Agent': 'Xcode',
            'Accept': 'text/x-xml-plist',
            'Accept-Language': 'en-us',
            'X-Apple-Identity-Token': identity_token,
            'X-Apple-App-Info': 'com.apple.gs.xcode.auth',
            'X-Xcode-Version': '11.2 (11B41)',
            'X-MMe-Client-Info': self.GSA_CLIENT_INFO,
        }
        headers.update(anisette)
        
        self.session.get(
            self.VERIFY_TRUSTEDDEVICE,
            headers=headers,
            verify=False,
            timeout=10,
        )
    
    def verify_2fa(self, apple_id, password, code_2fa):
        """
        Verify 2FA code submitted by user.
        
        Supports two methods:
        1. Trusted device code: Submit to /grandslam/GsService2/validate
        2. SMS code: Submit to /auth/verify/phone/securitycode
        
        After 2FA verification, re-authenticates to get final tokens.
        """
        anisette = self.get_anisette_headers()
        
        if not self.ds_person_id or not self.idms_token:
            # If we don't have tokens from Phase 1, re-login with password+2FA
            return self._verify_2fa_reauth(apple_id, password, code_2fa, anisette)
        
        identity_token = base64.b64encode(
            (str(self.ds_person_id) + ":" + self.idms_token).encode()
        ).decode()
        
        headers = {
            'Content-Type': 'text/x-xml-plist',
            'User-Agent': 'Xcode',
            'Accept': 'text/x-xml-plist',
            'Accept-Language': 'en-us',
            'X-Apple-Identity-Token': identity_token,
            'X-Apple-App-Info': 'com.apple.gs.xcode.auth',
            'X-Xcode-Version': '11.2 (11B41)',
            'X-MMe-Client-Info': self.GSA_CLIENT_INFO,
            'security-code': code_2fa,
        }
        headers.update(anisette)
        
        try:
            # Submit 2FA code to trusted device validate endpoint
            logger.info(f"Submitting 2FA code to {self.VALIDATE_ENDPOINT}")
            resp = self.session.get(
                self.VALIDATE_ENDPOINT,
                headers=headers,
                verify=False,
                timeout=10,
            )
            
            logger.info(f"2FA validate response: status={resp.status_code}")
            
            if resp.ok:
                logger.info("2FA code accepted! Token verified.")
                self.authenticated = True
                return {
                    'success': True,
                    'session_id': self.session_id,
                    'message': 'Xác minh 2FA thành công! Token đã được lưu.',
                    'account_info': {
                        'apple_id': apple_id,
                        'ds_person_id': self.ds_person_id,
                        'token_preview': (self.itunes_token or self.gs_token or '')[:20] + '...',
                        'authenticated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                }
            else:
                # Try SMS method
                return self._verify_2fa_sms(apple_id, password, code_2fa, identity_token, anisette)
                
        except Exception as e:
            logger.error(f"2FA verify error: {e}", exc_info=True)
            return {
                'success': False,
                'session_id': self.session_id,
                'message': f'2FA verify error: {str(e)}'
            }
    
    def _verify_2fa_sms(self, apple_id, password, code_2fa, identity_token, anisette):
        """Submit 2FA code via SMS verification endpoint."""
        headers = {
            'User-Agent': 'Xcode',
            'Accept-Language': 'en-us',
            'X-Apple-Identity-Token': identity_token,
            'X-Apple-App-Info': 'com.apple.gs.xcode.auth',
            'X-Xcode-Version': '11.2 (11B41)',
            'X-MMe-Client-Info': self.GSA_CLIENT_INFO,
        }
        headers.update(anisette)
        
        body = {
            'phoneNumber': {'id': 1},
            'mode': 'sms',
            'securityCode': {'code': code_2fa},
        }
        
        try:
            resp = self.session.post(
                self.VERIFY_PHONE_CODE,
                json=body,
                headers=headers,
                verify=False,
                timeout=10,
            )
            
            if resp.ok:
                self.authenticated = True
                return {
                    'success': True,
                    'session_id': self.session_id,
                    'message': 'Xác minh 2FA qua SMS thành công!',
                    'account_info': {
                        'apple_id': apple_id,
                        'ds_person_id': self.ds_person_id,
                        'token_preview': (self.itunes_token or self.gs_token or '')[:20] + '...',
                        'authenticated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                }
            else:
                return {
                    'success': False,
                    'session_id': self.session_id,
                    'message': f'Mã 2FA không chính xác hoặc đã hết hạn. (HTTP {resp.status_code})'
                }
        except Exception as e:
            logger.error(f"SMS 2FA error: {e}")
            return {
                'success': False,
                'session_id': self.session_id,
                'message': f'SMS 2FA error: {str(e)}'
            }
    
    def _verify_2fa_reauth(self, apple_id, password, code_2fa, anisette):
        """Fallback: Re-authenticate with password+2FA code appended."""
        full_password = f"{password}{code_2fa}"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': self.STORE_USER_AGENT,
            'X-Apple-Store-Front': self.store_front,
            'Accept': '*/*',
            **anisette
        }
        
        try:
            r = self.session.post(
                self.ITUNES_AUTH_ENDPOINT,
                headers=headers,
                data=urlencode({
                    'appleId': apple_id,
                    'password': full_password,
                    'attempt': '2',
                    'createSession': 'true',
                }),
                timeout=15,
                allow_redirects=False
            )
            
            if r.status_code == 200:
                self.authenticated = True
                self.auth_cookies = dict(r.cookies)
                
                try:
                    resp_data = plistlib.loads(r.content)
                    self.ds_person_id = resp_data.get('dsPersonId', '')
                    self.itunes_token = resp_data.get('passwordToken', '')
                except Exception:
                    self.itunes_token = r.headers.get('X-Apple-GS-Token', f'2fa_ok_{int(time.time())}')
                
                return {
                    'success': True,
                    'session_id': self.session_id,
                    'message': 'Xác minh 2FA thành công!',
                    'account_info': {
                        'apple_id': apple_id,
                        'ds_person_id': self.ds_person_id,
                        'token_preview': (self.itunes_token or '')[:20] + '...',
                        'authenticated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                }
            else:
                return {
                    'success': False,
                    'session_id': self.session_id,
                    'message': f'Mã 2FA không chính xác (HTTP {r.status_code})'
                }
        except Exception as e:
            logger.error(f"2FA reauth error: {e}")
            return {
                'success': False,
                'session_id': self.session_id,
                'message': f'2FA reauth error: {str(e)}'
            }
    
    def get_session_data(self):
        """Export session data for persistence."""
        return {
            'session_id': self.session_id,
            'authenticated': self.authenticated,
            'ds_person_id': self.ds_person_id,
            'gs_token': self.gs_token,
            'idms_token': self.idms_token,
            'itunes_token': self.itunes_token,
            'auth_cookies': self.auth_cookies,
            'store_front': self.store_front,
        }
    
    def restore_session(self, session_data):
        """Restore session from saved data."""
        self.session_id = session_data.get('session_id', self.session_id)
        self.authenticated = session_data.get('authenticated', False)
        self.ds_person_id = session_data.get('ds_person_id')
        self.gs_token = session_data.get('gs_token')
        self.idms_token = session_data.get('idms_token')
        self.itunes_token = session_data.get('itunes_token')
        self.auth_cookies = session_data.get('auth_cookies', {})
        self.store_front = session_data.get('store_front', self.DEFAULT_STOREFRONT)
        if self.auth_cookies:
            self.session.cookies.update(self.auth_cookies)


class AppleStoreClient:
    """
    Client for Apple iTunes Store purchase operations.
    Handles subscription purchase via MZFinance buyProduct API.
    """
    
    BUY_ENDPOINT = "https://{pod}-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/buyProduct"
    LOOKUP_ENDPOINT = "https://itunes.apple.com/lookup"
    SEARCH_ENDPOINT = "https://itunes.apple.com/search"
    
    # TikTok App Store identifiers
    TIKTOK_ADAM_ID = "1235601864"
    TIKTOK_BUNDLE_ID = "com.ss.iphone.ugc.Aweme"
    
    STORE_USER_AGENT = "AppStore/3.0 iOS/17.4 model/iPhone15,2 hwp/t8120 build/21E219 (6; dt:251)"
    
    def __init__(self, auth_client: AppleAuthClient):
        self.auth = auth_client
        
    def lookup_app(self, adam_id=None):
        """Lookup app information from iTunes Store."""
        adam_id = adam_id or self.TIKTOK_ADAM_ID
        try:
            r = self.auth.session.get(
                f"{self.LOOKUP_ENDPOINT}?id={adam_id}&country=vn",
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                results = data.get('results', [])
                if results:
                    app = results[0]
                    return {
                        'success': True,
                        'app_name': app.get('trackName', ''),
                        'bundle_id': app.get('bundleId', ''),
                        'adam_id': str(app.get('trackId', '')),
                        'price': app.get('price', 0),
                        'currency': app.get('currency', 'USD'),
                        'version': app.get('version', ''),
                    }
            return {'success': False, 'message': 'App not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def buy_product(self, adam_id, bundle_id=None, server_pod="p71"):
        """
        Execute product purchase via MZFinance buyProduct API.
        
        Args:
            adam_id: Apple Adam ID of the product/subscription
            bundle_id: App bundle identifier (defaults to TikTok)
            server_pod: iTunes Store server pod
            
        Returns:
            dict with purchase result and receipt data
        """
        if not self.auth.authenticated:
            return {'success': False, 'message': 'Chưa xác thực Apple ID. Vui lòng login trước.'}
        
        bundle_id = bundle_id or self.TIKTOK_BUNDLE_ID
        url = self.BUY_ENDPOINT.format(pod=server_pod)
        
        anisette = self.auth.get_anisette_headers()
        
        headers = {
            'User-Agent': self.STORE_USER_AGENT,
            'Content-Type': 'application/x-apple-plist',
            'X-Apple-Store-Front': self.auth.store_front,
            'X-Dsid': str(self.auth.ds_person_id or ''),
            'X-Token': self.auth.itunes_token or self.auth.gs_token or '',
            **anisette
        }
        
        # Add auth cookies
        if self.auth.auth_cookies:
            self.auth.session.cookies.update(self.auth.auth_cookies)
        
        purchase_payload = {
            'salableAdamId': str(adam_id),
            'appExtVrsId': '0',
            'price': '0',
            'productType': 'C',  # C = consumable, S = subscription
            'pricingParameters': 'STDQ',
            'hasAskedToFulfillPreorder': 'true',
            'buyWithoutAuthorization': 'true',
            'hasConfirmedTerms': 'true',
            'isInApp': 'true',
            'bid': bundle_id,
        }
        
        try:
            payload_bytes = plistlib.dumps(purchase_payload, fmt=plistlib.FMT_XML)
            r = self.auth.session.post(
                url,
                headers=headers,
                data=payload_bytes,
                timeout=30
            )
            
            if r.status_code == 200:
                try:
                    resp = plistlib.loads(r.content)
                    receipt = resp.get('receipt-data', '')
                    transaction_id = resp.get('transactionId', resp.get('songId', ''))
                    
                    return {
                        'success': True,
                        'message': 'Mua thành công!',
                        'receipt_data': receipt if isinstance(receipt, str) else base64.b64encode(receipt).decode(),
                        'transaction_id': str(transaction_id),
                        'raw_response': {k: str(v)[:100] for k, v in resp.items()} if resp else {}
                    }
                except Exception:
                    # Try raw response
                    return {
                        'success': True,
                        'message': 'Purchase completed (raw response)',
                        'receipt_data': base64.b64encode(r.content).decode()[:500],
                        'transaction_id': f'txn_{int(time.time())}',
                    }
            else:
                return {
                    'success': False,
                    'message': f'Purchase failed (HTTP {r.status_code})',
                    'status_code': r.status_code,
                    'response_preview': r.text[:300]
                }
        except Exception as e:
            logger.error(f"Buy product error: {e}")
            return {'success': False, 'message': f'Purchase error: {str(e)}'}
    
    def get_account_info(self, server_pod="p71"):
        """
        Fetch current Apple account info including payment methods.
        Uses the same authenticated MZFinance session as buyProduct.
        
        Returns:
            dict with account info, including payment method status
        """
        if not self.auth.authenticated:
            return {'success': False, 'message': 'Chưa xác thực Apple ID.'}
        
        url = f"https://{server_pod}-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/accountSummary"
        anisette = self.auth.get_anisette_headers()
        
        headers = {
            'User-Agent': self.STORE_USER_AGENT,
            'Content-Type': 'application/x-apple-plist',
            'X-Apple-Store-Front': self.auth.store_front,
            'X-Dsid': str(self.auth.ds_person_id or ''),
            'X-Token': self.auth.itunes_token or self.auth.gs_token or '',
            **anisette
        }
        
        if self.auth.auth_cookies:
            self.auth.session.cookies.update(self.auth.auth_cookies)
        
        try:
            # Request account summary
            payload = plistlib.dumps({
                'includePaymentSummary': True,
                'includeAccountSummary': True,
            }, fmt=plistlib.FMT_XML)
            
            r = self.auth.session.post(url, headers=headers, data=payload, timeout=15)
            
            if r.status_code == 200:
                try:
                    resp = plistlib.loads(r.content)
                    payment_info = resp.get('paymentSummary', resp.get('payment', {}))
                    
                    has_payment = bool(
                        payment_info.get('creditCardType') or 
                        payment_info.get('lastFourDigits') or
                        payment_info.get('paymentType')
                    )
                    
                    return {
                        'success': True,
                        'has_payment_method': has_payment,
                        'payment_info': {
                            'type': payment_info.get('creditCardType', payment_info.get('paymentType', 'None')),
                            'last_four': payment_info.get('lastFourDigits', ''),
                            'name_on_card': payment_info.get('creditCardHolder', ''),
                            'expiry': payment_info.get('creditCardExpires', ''),
                        },
                        'account': {
                            'first_name': resp.get('firstName', ''),
                            'last_name': resp.get('lastName', ''),
                            'email': resp.get('appleId', ''),
                            'country': resp.get('countryCode', ''),
                            'store_credit': resp.get('creditBalance', '0'),
                        },
                        'raw_keys': list(resp.keys()) if isinstance(resp, dict) else [],
                    }
                except Exception as parse_err:
                    return {
                        'success': True,
                        'has_payment_method': None,
                        'message': f'Account info retrieved but parse error: {parse_err}',
                        'raw_preview': r.text[:500],
                    }
            else:
                return {
                    'success': False,
                    'message': f'Account info failed (HTTP {r.status_code})',
                    'response_preview': r.text[:300],
                }
        except Exception as e:
            logger.error(f"Account info error: {e}")
            return {'success': False, 'message': str(e)}
    
    def add_payment_method(self, card_number, expiry_month, expiry_year, 
                           cvv, first_name, last_name,
                           address_line1="", city="", state="", 
                           zip_code="", country_code="VN",
                           phone="", server_pod="p71"):
        """
        Add or update payment method on Apple account.
        Uses the same authenticated MZFinance session + Anisette headers
        that buyProduct uses.
        
        Args:
            card_number: Credit/debit card number (16 digits)
            expiry_month: Card expiry month (01-12)
            expiry_year: Card expiry year (2-digit or 4-digit)
            cvv: Security code (3-4 digits)
            first_name: Cardholder first name
            last_name: Cardholder last name
            address_line1: Billing address line 1
            city: Billing city
            state: Billing state/province
            zip_code: Billing zip/postal code
            country_code: Billing country (ISO 2-letter, default VN)
            phone: Phone number
            server_pod: iTunes Store server pod (default p71)
            
        Returns:
            dict with result of payment method update
        """
        if not self.auth.authenticated:
            return {'success': False, 'message': 'Chưa xác thực Apple ID.'}
        
        # Validate inputs
        card_clean = card_number.replace(' ', '').replace('-', '')
        if not card_clean.isdigit() or len(card_clean) < 13 or len(card_clean) > 19:
            return {'success': False, 'message': 'Số thẻ không hợp lệ (13-19 chữ số).'}
        
        if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
            return {'success': False, 'message': 'CVV không hợp lệ (3-4 chữ số).'}
        
        # Normalize expiry year to 4-digit
        exp_year = str(expiry_year)
        if len(exp_year) == 2:
            exp_year = f"20{exp_year}"
        
        exp_month = str(expiry_month).zfill(2)
        
        # Detect card type
        card_type = self._detect_card_type(card_clean)
        
        url = f"https://{server_pod}-buy.itunes.apple.com/WebObjects/MZFinance.woa/wa/updateAccountInfo"
        anisette = self.auth.get_anisette_headers()
        
        headers = {
            'User-Agent': self.STORE_USER_AGENT,
            'Content-Type': 'application/x-apple-plist',
            'X-Apple-Store-Front': self.auth.store_front,
            'X-Dsid': str(self.auth.ds_person_id or ''),
            'X-Token': self.auth.itunes_token or self.auth.gs_token or '',
            **anisette
        }
        
        if self.auth.auth_cookies:
            self.auth.session.cookies.update(self.auth.auth_cookies)
        
        # Build payment update payload (plist format matching Apple's internal format)
        payment_payload = {
            'paymentType': 'CreditCard',
            'creditCardType': card_type,
            'creditCardNumber': card_clean,
            'creditCardExpireMonth': exp_month,
            'creditCardExpireYear': exp_year,
            'securityCode': cvv,
            'creditCardHolder': f"{first_name} {last_name}",
            'firstName': first_name,
            'lastName': last_name,
            'addressLine1': address_line1,
            'city': city,
            'state': state,
            'postalCode': zip_code,
            'countryCode': country_code,
            'phone': phone,
            'updatePaymentInfo': True,
            'hasConfirmedTerms': True,
        }
        
        try:
            payload_bytes = plistlib.dumps(payment_payload, fmt=plistlib.FMT_XML)
            
            logger.info(f"Sending payment update to {url} with card type={card_type}, last4={card_clean[-4:]}")
            
            r = self.auth.session.post(
                url,
                headers=headers,
                data=payload_bytes,
                timeout=20
            )
            
            if r.status_code == 200:
                try:
                    resp = plistlib.loads(r.content)
                    
                    # Check for error in response
                    error_msg = resp.get('customerMessage', resp.get('failureType', ''))
                    if error_msg:
                        return {
                            'success': False,
                            'message': f'Apple từ chối: {error_msg}',
                            'error_type': resp.get('failureType', ''),
                            'raw_keys': list(resp.keys()),
                        }
                    
                    return {
                        'success': True,
                        'message': f'Đã thêm thẻ {card_type} ****{card_clean[-4:]} thành công!',
                        'card_type': card_type,
                        'last_four': card_clean[-4:],
                        'expiry': f'{exp_month}/{exp_year}',
                    }
                except Exception:
                    # If response is not plist, check raw
                    if 'success' in r.text.lower() or r.status_code == 200:
                        return {
                            'success': True,
                            'message': f'Thêm thẻ ****{card_clean[-4:]} - Response received',
                            'raw_preview': r.text[:300],
                        }
                    return {
                        'success': False,
                        'message': f'Unexpected response format',
                        'raw_preview': r.text[:300],
                    }
            elif r.status_code == 412:
                # 412 = Precondition Failed (often needs re-auth)
                return {
                    'success': False,
                    'message': 'Session hết hạn. Cần đăng nhập lại Apple ID.',
                    'status_code': 412,
                    'requires_reauth': True,
                }
            else:
                return {
                    'success': False,
                    'message': f'Payment update failed (HTTP {r.status_code})',
                    'status_code': r.status_code,
                    'response_preview': r.text[:300]
                }
        except Exception as e:
            logger.error(f"Payment method update error: {e}")
            return {'success': False, 'message': f'Payment update error: {str(e)}'}
    
    @staticmethod
    def _detect_card_type(card_number):
        """Detect credit card type from card number."""
        if card_number.startswith('4'):
            return 'Visa'
        elif card_number[:2] in ('51', '52', '53', '54', '55') or \
             (2221 <= int(card_number[:4]) <= 2720):
            return 'MasterCard'
        elif card_number[:2] in ('34', '37'):
            return 'Amex'
        elif card_number[:4] in ('6011', '6221', '6229') or \
             card_number[:2] in ('64', '65'):
            return 'Discover'
        elif card_number[:4] in ('3528', '3589') or card_number[:2] == '35':
            return 'JCB'
        elif card_number[:2] in ('62', '81'):
            return 'UnionPay'
        else:
            return 'Visa'  # Default fallback

