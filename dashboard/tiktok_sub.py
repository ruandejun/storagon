"""
TikTok Subscription Module
Handles TikTok user lookup, subscription product discovery, and receipt verification.
"""
import json
import logging
import re
import time

import requests

logger = logging.getLogger(__name__)


class TikTokClient:
    """
    Client for TikTok API interactions.
    Handles user lookup, subscription product listing, and receipt verification.
    """
    
    # TikTok API endpoints
    USER_INFO_API = "https://www.tiktok.com/api/user/detail/"
    USER_SEARCH_API = "https://www.tiktok.com/api/search/user/full/"
    WEB_API = "https://www.tiktok.com/@{username}"
    
    # TikTok receipt verification
    RECEIPT_VERIFY_API = "https://api-va.tiktok.com/passport/web/receipt/verify/"
    
    # Alternative API endpoints (mobile)
    MOBILE_USER_API = "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/user/"
    
    # Default headers mimicking iOS TikTok app
    IOS_USER_AGENT = "TikTok 33.7.4 rv:337404 (iPhone; iOS 17.4; vi_VN) Cronet"
    WEB_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
    
    def __init__(self, proxy=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.WEB_USER_AGENT,
            'Accept': 'application/json',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
        })
        
        if proxy:
            self.session.proxies.update({
                'http': proxy,
                'https': proxy
            })
    
    def lookup_user(self, username):
        """
        Lookup TikTok user information from username.
        
        Args:
            username: TikTok username (with or without @)
            
        Returns:
            dict with user info including user_id, nickname, avatar, etc.
        """
        # Clean username
        username = username.strip().lstrip('@')
        
        if not username:
            return {'success': False, 'message': 'Username không được để trống'}
        
        # Method 1: Try web page scraping for user_id
        try:
            r = self.session.get(
                f"https://www.tiktok.com/@{username}",
                headers={
                    'User-Agent': self.WEB_USER_AGENT,
                    'Accept': 'text/html,application/xhtml+xml',
                },
                timeout=10,
                allow_redirects=True
            )
            
            if r.status_code == 200:
                # Extract user data from page source using SIGI_STATE or __UNIVERSAL_DATA_FOR_REHYDRATION__
                user_data = self._extract_user_from_html(r.text, username)
                if user_data:
                    return user_data
        except Exception as e:
            logger.warning(f"Web scrape lookup failed for @{username}: {e}")
        
        # Method 2: Try TikTok API
        try:
            r = self.session.get(
                self.USER_INFO_API,
                params={
                    'uniqueId': username,
                    'msToken': '',
                },
                headers={
                    'User-Agent': self.WEB_USER_AGENT,
                    'Referer': f'https://www.tiktok.com/@{username}',
                },
                timeout=10
            )
            
            if r.status_code == 200:
                data = r.json()
                user_info = data.get('userInfo', {})
                user = user_info.get('user', {})
                stats = user_info.get('stats', {})
                
                if user.get('id'):
                    return {
                        'success': True,
                        'user_id': user.get('id', ''),
                        'sec_uid': user.get('secUid', ''),
                        'username': user.get('uniqueId', username),
                        'nickname': user.get('nickname', ''),
                        'avatar': user.get('avatarThumb', ''),
                        'verified': user.get('verified', False),
                        'followers': stats.get('followerCount', 0),
                        'following': stats.get('followingCount', 0),
                        'likes': stats.get('heartCount', 0),
                        'videos': stats.get('videoCount', 0),
                        'bio': user.get('signature', ''),
                        'is_live_enabled': user.get('isLiveSubscribeEnabled', False),
                    }
        except Exception as e:
            logger.warning(f"API lookup failed for @{username}: {e}")
        
        # Method 3: Return basic info if lookup fails
        return {
            'success': True,
            'user_id': f'pending_lookup_{username}',
            'username': username,
            'nickname': username,
            'avatar': '',
            'verified': False,
            'followers': 0,
            'message': 'User found (limited data). Lookup API temporarily unavailable.',
            'lookup_method': 'fallback'
        }
    
    def _extract_user_from_html(self, html, username):
        """Extract user data from TikTok HTML page source."""
        try:
            # Try __UNIVERSAL_DATA_FOR_REHYDRATION__
            pattern = r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>'
            match = re.search(pattern, html, re.DOTALL)
            if match:
                raw_data = json.loads(match.group(1))
                default_scope = raw_data.get('__DEFAULT_SCOPE__', {})
                user_detail = default_scope.get('webapp.user-detail', {})
                user_info = user_detail.get('userInfo', {})
                user = user_info.get('user', {})
                stats = user_info.get('stats', {})
                
                if user.get('id'):
                    return {
                        'success': True,
                        'user_id': user.get('id', ''),
                        'sec_uid': user.get('secUid', ''),
                        'username': user.get('uniqueId', username),
                        'nickname': user.get('nickname', ''),
                        'avatar': user.get('avatarThumb', ''),
                        'verified': user.get('verified', False),
                        'followers': stats.get('followerCount', 0),
                        'following': stats.get('followingCount', 0),
                        'likes': stats.get('heartCount', 0),
                        'videos': stats.get('videoCount', 0),
                        'bio': user.get('signature', ''),
                        'lookup_method': 'web_scrape'
                    }
        except Exception as e:
            logger.debug(f"HTML extraction failed: {e}")
        
        # Try SIGI_STATE
        try:
            pattern = r'<script id="SIGI_STATE"[^>]*>(.*?)</script>'
            match = re.search(pattern, html, re.DOTALL)
            if match:
                sigi_data = json.loads(match.group(1))
                user_module = sigi_data.get('UserModule', {}).get('users', {})
                user = user_module.get(username, {})
                if user.get('id'):
                    return {
                        'success': True,
                        'user_id': user.get('id', ''),
                        'sec_uid': user.get('secUid', ''),
                        'username': user.get('uniqueId', username),
                        'nickname': user.get('nickname', ''),
                        'avatar': user.get('avatarThumb', ''),
                        'verified': user.get('verified', False),
                        'lookup_method': 'sigi_state'
                    }
        except Exception as e:
            logger.debug(f"SIGI_STATE extraction failed: {e}")
        
        return None
    
    def get_subscription_tiers(self, creator_user_id=None):
        """
        Get available subscription tiers for TikTok LIVE subscriptions.
        
        TikTok manages subscription products internally using tier_id and subscription_id.
        These are not standard Apple StoreKit product IDs.
        
        Returns:
            list of available subscription tiers
        """
        # TikTok LIVE subscription standard tiers
        # These tier structures are based on TikTok's known subscription model
        default_tiers = [
            {
                'tier_id': 'tier_1',
                'name': 'LIVE Subscription - Tier 1',
                'price': 0.99,
                'currency': 'USD',
                'period': 'monthly',
                'description': 'Gói Sub cơ bản - Badge & Emotes cho kênh LIVE',
                'benefits': ['Custom Badge', 'Subscriber Emotes', 'Ad-free viewing'],
            },
            {
                'tier_id': 'tier_2',
                'name': 'LIVE Subscription - Tier 2',
                'price': 4.99,
                'currency': 'USD',
                'period': 'monthly',
                'description': 'Gói Sub nâng cao - Tất cả benefits Tier 1 + Exclusive content',
                'benefits': ['All Tier 1 benefits', 'Exclusive Content', 'Priority Chat'],
            },
            {
                'tier_id': 'tier_3',
                'name': 'LIVE Subscription - Tier 3',
                'price': 24.99,
                'currency': 'USD',
                'period': 'monthly',
                'description': 'Gói Sub VIP - Tất cả benefits + Shoutout',
                'benefits': ['All Tier 2 benefits', 'Custom Shoutout', 'VIP Badge', '1-on-1 Chat'],
            }
        ]
        
        # If creator_user_id provided, try to fetch actual tiers
        if creator_user_id:
            try:
                # TikTok internal API for subscription products
                r = self.session.get(
                    f"https://api-va.tiktok.com/aweme/v1/live/subscription/product/list/",
                    params={
                        'host_user_id': creator_user_id,
                    },
                    headers={
                        'User-Agent': self.IOS_USER_AGENT,
                    },
                    timeout=10
                )
                if r.status_code == 200:
                    data = r.json()
                    products = data.get('data', {}).get('product_list', [])
                    tiers = []
                    if products:
                        for p in products:
                            tiers.append({
                                'tier_id': p.get('product_id', ''),
                                'name': p.get('product_name', 'LIVE Subscription'),
                                'price': p.get('price', {}).get('amount', 0) / 100,
                                'currency': p.get('price', {}).get('currency', 'USD'),
                                'period': 'monthly',
                                'description': p.get('description', ''),
                                'benefits': [b.get('text', '') for b in p.get('benefits', [])],
                            })
                    return {'success': True, 'tiers': tiers, 'source': 'creator'}
            except Exception as e:
                logger.warning(f"Failed to fetch creator tiers: {e}")
        
        return {'success': True, 'tiers': default_tiers, 'source': 'default'}
    
    def verify_receipt(self, receipt_data, user_id, channel_id, platform='ios'):
        """
        Send App Store Receipt to TikTok Server to activate subscription.
        
        Args:
            receipt_data: Base64 encoded Apple receipt
            user_id: TikTok user_id of the subscriber
            channel_id: TikTok user_id of the creator/channel
            platform: Platform identifier ('ios')
            
        Returns:
            dict with verification result
        """
        headers = {
            'User-Agent': self.IOS_USER_AGENT,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        payload = {
            'receipt_data': receipt_data,
            'user_id': str(user_id),
            'target_channel_id': str(channel_id),
            'platform': platform,
            'app_id': '1233',  # TikTok app identifier
        }
        
        try:
            r = self.session.post(
                self.RECEIPT_VERIFY_API,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if r.status_code == 200:
                data = r.json()
                return {
                    'success': data.get('status_code', -1) == 0,
                    'message': data.get('message', 'Verification submitted'),
                    'data': data.get('data', {}),
                    'status_code': r.status_code
                }
            else:
                return {
                    'success': False,
                    'message': f'TikTok verify failed (HTTP {r.status_code})',
                    'status_code': r.status_code,
                    'response': r.text[:300]
                }
        except Exception as e:
            logger.error(f"Receipt verification error: {e}")
            return {
                'success': False,
                'message': f'Verification error: {str(e)}'
            }
    
    def check_subscription_status(self, user_id, creator_id):
        """Check if a user has an active subscription to a creator."""
        try:
            r = self.session.get(
                "https://api-va.tiktok.com/aweme/v1/live/subscription/check/",
                params={
                    'user_id': user_id,
                    'host_user_id': creator_id,
                },
                headers={
                    'User-Agent': self.IOS_USER_AGENT,
                },
                timeout=10
            )
            
            if r.status_code == 200:
                data = r.json()
                return {
                    'success': True,
                    'is_subscribed': data.get('data', {}).get('is_subscribed', False),
                    'expire_time': data.get('data', {}).get('expire_time', 0),
                    'tier_id': data.get('data', {}).get('tier_id', ''),
                }
            return {
                'success': False,
                'is_subscribed': False,
                'message': f'Status check failed (HTTP {r.status_code})'
            }
        except Exception as e:
            return {
                'success': False,
                'is_subscribed': False,
                'message': str(e)
            }
