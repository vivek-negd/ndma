import logging
import time
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

# Security loggers
logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')


class ThrottlingManager:
    """
    Rate limiting and throttling manager
    
    Features:
    - IP-based rate limiting
    - User-based rate limiting
    - Endpoint-specific throttling
    - Configurable limits per endpoint
    """
    
    THROTTLE_CACHE_PREFIX = "throttle"
    BLOCK_CACHE_PREFIX = "throttle_block"
    
    def __init__(self):
        self.cache = cache
    
    @staticmethod
    def _get_client_ip(request):
        """Extract real client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    def _get_cache_key(self, identifier, endpoint, period='hour'):
        """Generate cache key for throttle tracking"""
        return f"{self.THROTTLE_CACHE_PREFIX}:{endpoint}:{identifier}:{period}"
    
    def _get_block_key(self, identifier):
        """Generate cache key for blocking users"""
        return f"{self.BLOCK_CACHE_PREFIX}:{identifier}"
    
    def check_rate_limit(self, request, endpoint, max_requests=20, period_seconds=3600):
        """
        Check if request should be throttled
        
        Args:
            request: HTTP request object
            endpoint: Name of endpoint (e.g., 'login', 'upload', 'create_user')
            max_requests: Maximum requests allowed in period
            period_seconds: Time period in seconds (default: 1 hour = 3600)
        
        Returns:
            {
                'allowed': bool,
                'remaining': int,
                'reset_time': datetime,
                'message': str
            }
        """
        client_ip = self._get_client_ip(request)
        user_id = getattr(request.user, 'id', None) if request.user.is_authenticated else None
        
        # Use user_id if authenticated, otherwise use IP
        identifier = user_id if user_id else client_ip
        cache_key = self._get_cache_key(identifier, endpoint)
        
        # Check if user is temporarily blocked
        is_blocked = self.cache.get(self._get_block_key(identifier))
        if is_blocked:
            return {
                'allowed': False,
                'remaining': 0,
                'reset_time': datetime.now() + timedelta(minutes=15),
                'message': f'Too many requests. Try again later.',
                'blocked': True
            }
        
        # Get current request count
        current_count = self.cache.get(cache_key, 0)
        
        # Check if limit exceeded
        if current_count >= max_requests:
            # Block user for 15 minutes after exceeding limit
            self.cache.set(self._get_block_key(identifier), True, timeout=900)  # 15 minutes
            
            security_logger.warning(
                f"RATE_LIMIT_EXCEEDED | Endpoint: {endpoint} | Identifier: {identifier} | "
                f"IP: {client_ip} | Current: {current_count}"
            )
            
            return {
                'allowed': False,
                'remaining': 0,
                'reset_time': datetime.now() + timedelta(seconds=period_seconds),
                'message': f'Rate limit exceeded ({max_requests}/{period_seconds}s). Try again later.',
                'blocked': True
            }
        
        # Increment counter
        self.cache.set(cache_key, current_count + 1, timeout=period_seconds)
        
        remaining = max_requests - current_count - 1
        
        return {
            'allowed': True,
            'remaining': remaining,
            'reset_time': datetime.now() + timedelta(seconds=period_seconds),
            'message': f'Request allowed. {remaining} remaining.',
            'blocked': False
        }
    
    def reset_throttle(self, request, endpoint):
        """Reset throttle counter for an identifier"""
        client_ip = self._get_client_ip(request)
        user_id = getattr(request.user, 'id', None) if request.user.is_authenticated else None
        identifier = user_id if user_id else client_ip
        
        cache_key = self._get_cache_key(identifier, endpoint)
        self.cache.delete(cache_key)
        
        security_logger.info(
            f"THROTTLE_RESET | Endpoint: {endpoint} | Identifier: {identifier}"
        )
    
    def unblock_user(self, request):
        """Remove temporary block on user/IP"""
        client_ip = self._get_client_ip(request)
        user_id = getattr(request.user, 'id', None) if request.user.is_authenticated else None
        identifier = user_id if user_id else client_ip
        
        self.cache.delete(self._get_block_key(identifier))
        
        security_logger.info(
            f"USER_UNBLOCKED | Identifier: {identifier} | IP: {client_ip}"
        )


class BruteForceDetector:
    """
    Detect and prevent brute force attacks
    
    Features:
    - Track failed login attempts
    - Automatic account lock after N attempts
    - IP-based blocking
    - Configurable thresholds
    """
    
    FAILED_ATTEMPT_KEY = "brute_force:failed:{}"
    LOCK_KEY = "brute_force:lock:{}"
    
    def __init__(self, max_attempts=5, lockout_duration=900):
        """
        Initialize brute force detector
        
        Args:
            max_attempts: Max failed attempts before lockout (default: 5)
            lockout_duration: Lockout duration in seconds (default: 15 minutes)
        """
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        self.cache = cache
    
    @staticmethod
    def _get_client_ip(request):
        """Extract real client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    def is_account_locked(self, email):
        """Check if account is locked"""
        lock_key = self.LOCK_KEY.format(email)
        return self.cache.get(lock_key, False)
    
    def record_failed_attempt(self, email, request):
        """Record a failed login attempt"""
        client_ip = self._get_client_ip(request)
        attempt_key = self.FAILED_ATTEMPT_KEY.format(email)
        
        # Get current attempt count
        attempts = self.cache.get(attempt_key, 0)
        attempts += 1
        
        security_logger.warning(
            f"LOGIN_ATTEMPT_FAILED | Email: {email} | IP: {client_ip} | "
            f"Attempt: {attempts}/{self.max_attempts}"
        )
        
        # Set expiry to 1 hour for attempt tracking
        self.cache.set(attempt_key, attempts, timeout=3600)
        
        # Lock account if max attempts exceeded
        if attempts >= self.max_attempts:
            lock_key = self.LOCK_KEY.format(email)
            self.cache.set(lock_key, True, timeout=self.lockout_duration)
            
            security_logger.error(
                f"ACCOUNT_LOCKED_BRUTE_FORCE | Email: {email} | IP: {client_ip} | "
                f"Duration: {self.lockout_duration}s"
            )
            
            return {
                'locked': True,
                'message': f'Account locked due to multiple failed attempts. Try again in {self.lockout_duration//60} minutes.',
                'remaining_attempts': 0
            }
        
        remaining = self.max_attempts - attempts
        return {
            'locked': False,
            'message': f'login failed. {remaining} attempts remaining.',
            'remaining_attempts': remaining
        }
    
    def reset_failed_attempts(self, email):
        """Reset failed attempts counter for successful login"""
        attempt_key = self.FAILED_ATTEMPT_KEY.format(email)
        self.cache.delete(attempt_key)
        
        security_logger.info(
            f"LOGIN_SUCCESS_RESET_ATTEMPTS | Email: {email}"
        )
    
    def unlock_account(self, email):
        """Manually unlock an account"""
        lock_key = self.LOCK_KEY.format(email)
        self.cache.delete(lock_key)
        
        attempt_key = self.FAILED_ATTEMPT_KEY.format(email)
        self.cache.delete(attempt_key)
        
        security_logger.info(
            f"ACCOUNT_MANUALLY_UNLOCKED | Email: {email}"
        )


class SecurityValidator:
    """
    Input validation and sanitization
    
    Features:
    - Email validation
    - Password strength validation
    - Input sanitization
    - SQL injection prevention
    - XSS prevention
    """
    
    import re
    
    @staticmethod
    def validate_email(email):
        """
        Validate email format
        
        Returns: (is_valid: bool, message: str)
        """
        if not email or len(email) > 254:
            return False, "Invalid email length"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not SecurityValidator.re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, "Valid"
    
    @staticmethod
    def validate_password(password, min_length=8):
        """
        Validate password strength
        
        Requirements:
        - Minimum length (default: 8)
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        - At least 1 special character
        
        Returns: (is_valid: bool, message: str)
        """
        if not password or len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"
        
        if len(password) > 1000:
            return False, "Password too long"
        
        if not SecurityValidator.re.search(r'[A-Z]', password):
            return False, "Password must contain at least 1 uppercase letter"
        
        if not SecurityValidator.re.search(r'[a-z]', password):
            return False, "Password must contain at least 1 lowercase letter"
        
        if not SecurityValidator.re.search(r'\d', password):
            return False, "Password must contain at least 1 digit"
        
        if not SecurityValidator.re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least 1 special character"
        
        return True, "Password is strong"
    
    @staticmethod
    def sanitize_input(data):
        """
        Sanitize input to prevent injection attacks
        
        - Removes control characters
        - Removes null bytes
        - Limits length
        """
        if not data:
            return None
        
        if isinstance(data, str):
            # Remove control characters and null bytes
            data = ''.join(char for char in data if ord(char) >= 32 or char in '\n\r\t')
            # Limit length
            data = data[:1000]
        
        return data
    
    @staticmethod
    def is_sql_injection_attempt(data):
        """
        Detect potential SQL injection attempts
        
        Returns: bool (True if suspicious)
        """
        if not isinstance(data, str):
            return False
        
        data_lower = data.lower()
        
        # Check for common SQL injection patterns
        dangerous_patterns = [
            'union', 'select', 'insert', 'update', 'delete', 'drop',
            'exec', 'execute', 'script', 'javascript:', 'onerror=',
            'onclick=', '--', '/*', '*/', 'xp_', 'sp_'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in data_lower:
                return True
        
        return False
    
    @staticmethod
    def is_xss_attempt(data):
        """
        Detect potential XSS (Cross-Site Scripting) attempts
        
        Returns: bool (True if suspicious)
        """
        if not isinstance(data, str):
            return False
        
        data_lower = data.lower()
        
        # Check for common XSS patterns
        xss_patterns = [
            '<script', '</script>', 'javascript:', 'onerror=',
            'onclick=', 'onload=', 'onmouseover=', '<iframe',
            '<embed', '<object', '<img'
        ]
        
        for pattern in xss_patterns:
            if pattern in data_lower:
                return True
        
        return False


class SuspiciousActivityDetector:
    """
    Detect suspicious user activity patterns
    
    Features:
    - Track user activity
    - Detect unusual patterns
    - Alert on suspicious behavior
    """
    
    ACTIVITY_KEY = "activity:{user_id}:{endpoint}"
    
    def __init__(self):
        self.cache = cache
    
    def log_activity(self, user_id, endpoint, action, metadata=None):
        """Log user activity"""
        activity_key = self.ACTIVITY_KEY.format(user_id=user_id, endpoint=endpoint)
        
        activity = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'metadata': metadata or {}
        }
        
        security_logger.info(
            f"USER_ACTIVITY | User ID: {user_id} | Endpoint: {endpoint} | "
            f"Action: {action} | Metadata: {metadata}"
        )
        
        return activity
    
    def is_suspicious(self, user_id, endpoint, threshold=10, time_window=300):
        """
        Check if user activity is suspicious
        
        Args:
            user_id: User ID
            endpoint: Endpoint name
            threshold: Max requests in time window
            time_window: Time window in seconds
        
        Returns: bool (True if suspicious)
        """
        activity_key = f"{self.ACTIVITY_KEY.format(user_id=user_id, endpoint=endpoint)}"
        current_count = self.cache.get(activity_key, 0)
        
        if current_count >= threshold:
            security_logger.warning(
                f"SUSPICIOUS_ACTIVITY | User ID: {user_id} | Endpoint: {endpoint} | "
                f"Requests: {current_count}/{threshold} in {time_window}s"
            )
            return True
        
        # Increment counter
        self.cache.set(activity_key, current_count + 1, timeout=time_window)
        
        return False


# Usage Example:
"""
from core.security_utils import ThrottlingManager, BruteForceDetector, SecurityValidator

# In your API view:

class LoginView(viewsets.ViewSet):
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        throttle_manager = ThrottlingManager()
        brute_force_detector = BruteForceDetector()
        validator = SecurityValidator()
        
        # 1. Check throttling (20 requests per hour)
        throttle_result = throttle_manager.check_rate_limit(request, 'login', 20)
        if not throttle_result['allowed']:
            return Response(
                {'message': throttle_result['message']},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # 2. Get and validate inputs
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        
        # Sanitize
        email = validator.sanitize_input(email)
        password = validator.sanitize_input(password)
        
        # Check for injection attempts
        if validator.is_sql_injection_attempt(email) or validator.is_xss_attempt(email):
            security_logger.error(f"INJECTION_ATTEMPT | Email: {email}")
            return Response({'message': 'Invalid input'}, status=400)
        
        # Validate format
        is_valid, msg = validator.validate_email(email)
        if not is_valid:
            return Response({'message': msg}, status=400)
        
        # 3. Check brute force
        if brute_force_detector.is_account_locked(email):
            return Response(
                {'message': 'Account locked due to multiple failed attempts'},
                status=status.HTTP_423_LOCKED
            )
        
        # 4. Authenticate user
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                # Reset on success
                brute_force_detector.reset_failed_attempts(email)
                # Generate token...
                return Response({'access': token}, status=200)
            else:
                # Record failed attempt
                result = brute_force_detector.record_failed_attempt(email, request)
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'message': 'Invalid credentials'}, status=401)
"""
