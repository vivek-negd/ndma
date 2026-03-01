"""
Health Check & API Monitoring Endpoints

Monitors API status, database connectivity, and system health.
"""

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection
from django.core.cache import cache
import time
import os


class HealthCheckViewSet(viewsets.ViewSet):
    """
    API Health Check & Monitoring
    
    Endpoints:
    - GET /api/v1/health/status/             → Full system status
    - GET /api/v1/health/database/           → Database connectivity
    - GET /api/v1/health/cache/              → Cache system status
    - GET /api/v1/health/alive/              → Quick alive check
    """
    
    permission_classes = [AllowAny]  # Health checks should be accessible without auth
    
    def list(self, request):
        """
        GET /api/v1/health/
        Full system status overview
        """
        return self.get_full_status(request)
    
    def get_full_status(self, request):
        """Full system status with all checks"""
        start_time = time.time()
        
        db_status = self.check_database()
        cache_status = self.check_cache()
        environ_status = self.check_environment()
        app_status = self.check_app_status()
        
        elapsed_time = time.time() - start_time
        
        # Determine overall health
        all_passed = (
            db_status['status'] == 'healthy' and
            cache_status['status'] == 'healthy' and
            app_status['status'] == 'running'
        )
        
        overall_status = 'healthy' if all_passed else 'degraded'
        http_status = status.HTTP_200_OK if all_passed else status.HTTP_503_SERVICE_UNAVAILABLE
        
        response_data = {
            'overall_status': overall_status,
            'timestamp': timezone.now().isoformat(),
            'response_time_ms': round(elapsed_time * 1000, 2),
            'checks': {
                'database': db_status,
                'cache': cache_status,
                'environment': environ_status,
                'application': app_status,
            }
        }
        
        return Response(
            {
                'success': True,
                'code': http_status,
                'message': f"API {overall_status}",
                'data': response_data
            },
            status=http_status
        )
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        GET /api/v1/health/status/
        Get full system status
        """
        return self.get_full_status(request)
    
    @action(detail=False, methods=['get'])
    def alive(self, request):
        """
        GET /api/v1/health/alive/
        Quick lightweight check - is API running?
        """
        return Response(
            {
                'success': True,
                'code': 200,
                'message': "API is running",
                'data': {
                    'status': 'alive',
                    'timestamp': timezone.now().isoformat(),
                }
            }
        )
    
    @action(detail=False, methods=['get'])
    def database(self, request):
        """
        GET /api/v1/health/database/
        Check database connectivity and performance
        """
        start_time = time.time()
        db_check = self.check_database()
        elapsed_time = time.time() - start_time
        
        response_status = status.HTTP_200_OK if db_check['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
        
        db_check['response_time_ms'] = round(elapsed_time * 1000, 2)
        db_check['check_time'] = timezone.now().isoformat()
        
        return Response(
            {
                'success': db_check['status'] == 'healthy',
                'code': response_status,
                'message': db_check.get('message', ''),
                'data': db_check
            },
            status=response_status
        )
    
    @action(detail=False, methods=['get'])
    def cache(self, request):
        """
        GET /api/v1/health/cache/
        Check cache system (Redis/Memcached)
        """
        start_time = time.time()
        cache_check = self.check_cache()
        elapsed_time = time.time() - start_time
        
        response_status = status.HTTP_200_OK if cache_check['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
        
        cache_check['response_time_ms'] = round(elapsed_time * 1000, 2)
        cache_check['check_time'] = timezone.now().isoformat()
        
        return Response(
            {
                'success': cache_check['status'] == 'healthy',
                'code': response_status,
                'message': cache_check.get('message', ''),
                'data': cache_check
            },
            status=response_status
        )
    
    @action(detail=False, methods=['get'])
    def readiness(self, request):
        """
        GET /api/v1/health/readiness/
        Readiness check - is API ready to serve traffic?
        """
        db_status = self.check_database()
        app_status = self.check_app_status()
        
        is_ready = (
            db_status['status'] == 'healthy' and
            app_status['status'] == 'running'
        )
        
        http_status = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(
            {
                'success': is_ready,
                'code': http_status,
                'message': "API is ready" if is_ready else "API not ready",
                'data': {
                    'ready': is_ready,
                    'database_ready': db_status['status'] == 'healthy',
                    'app_ready': app_status['status'] == 'running',
                    'timestamp': timezone.now().isoformat(),
                }
            },
            status=http_status
        )
    
    @staticmethod
    def check_database():
        """Check database connectivity and basic query"""
        try:
            start_time = time.time()
            
            # Execute simple query to test connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            elapsed_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'engine': connection.settings_dict.get('ENGINE', 'unknown'),
                'database': connection.settings_dict.get('NAME', 'unknown'),
                'response_time_ms': round(elapsed_time * 1000, 2),
                'message': 'Database connection successful'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'engine': connection.settings_dict.get('ENGINE', 'unknown'),
                'error': str(e),
                'message': 'Database connection failed'
            }
    
    @staticmethod
    def check_cache():
        """Check cache system (Redis/Memcached/Dummy)"""
        try:
            start_time = time.time()
            
            # Test cache with set/get
            test_key = '_health_check_test'
            test_value = 'test_value'
            
            cache.set(test_key, test_value, timeout=10)
            retrieved = cache.get(test_key)
            cache.delete(test_key)
            
            elapsed_time = time.time() - start_time
            
            if retrieved == test_value:
                return {
                    'status': 'healthy',
                    'backend': str(cache.__class__.__name__),
                    'response_time_ms': round(elapsed_time * 1000, 2),
                    'message': 'Cache system operational'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'backend': str(cache.__class__.__name__),
                    'message': 'Cache get/set verification failed'
                }
        except Exception as e:
            return {
                'status': 'degraded',
                'error': str(e),
                'message': f'Cache system issue: {str(e)}'
            }
    
    @staticmethod
    def check_environment():
        """Check environment configuration"""
        try:
            from django.conf import settings
            
            debug_mode = settings.DEBUG
            allowed_hosts = settings.ALLOWED_HOSTS if hasattr(settings, 'ALLOWED_HOSTS') else []
            
            return {
                'status': 'ok',
                'debug': debug_mode,
                'environment': 'development' if debug_mode else 'production',
                'allowed_hosts_count': len(allowed_hosts),
                'message': 'Environment configured'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Could not read environment'
            }
    
    @staticmethod
    def check_app_status():
        """Check application general status"""
        try:
            from django.apps import apps
            
            installed_apps = len(apps.get_app_configs())
            
            return {
                'status': 'running',
                'installed_apps': installed_apps,
                'timestamp': timezone.now().isoformat(),
                'message': 'Application running normally'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Application error'
            }


# Additional monitoring endpoint for more detailed metrics
class MetricsViewSet(viewsets.ViewSet):
    """
    API Metrics & Statistics
    
    Endpoints:
    - GET /api/v1/metrics/endpoint-stats/    → Endpoint usage statistics
    - GET /api/v1/metrics/system-info/       → System information
    """
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def system_info(self, request):
        """
        GET /api/v1/metrics/system-info/
        System and API information
        """
        try:
            import sys
            import platform
            
            system_info = {
                'python_version': sys.version,
                'platform': platform.platform(),
                'processor': platform.processor(),
                'current_time': timezone.now().isoformat(),
                'api_version': 'v1',
                'django_version': __import__('django').VERSION,
                'drf_version': __import__('rest_framework').VERSION,
            }
            
            return Response(
                {
                    'success': True,
                    'code': 200,
                    'message': "System information retrieved",
                    'data': system_info
                }
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'code': 500,
                    'message': str(e),
                    'data': {'error': str(e)}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def version(self, request):
        """
        GET /api/v1/metrics/version/
        Get API version information
        """
        version_info = {
            'api_version': 'v1',
            'api_status': 'active',
            'build_date': '2026-03-01',
            'timestamp': timezone.now().isoformat(),
        }
        
        return Response(
            {
                'success': True,
                'code': 200,
                'message': "API version information",
                'data': version_info
            }
        )
