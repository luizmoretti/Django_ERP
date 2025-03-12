import json
from django.http import JsonResponse
from django.http import HttpResponse
from django.urls import resolve
from django.http import Http404
import logging

logger = logging.getLogger(__name__)

class JSONResponse404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Se a resposta for 404, converte para JSON
        if response.status_code == 404:
            accept = request.headers.get('accept', '')
            
            # Se o cliente aceita JSON ou se é uma requisição AJAX
            if 'application/json' in accept or request.headers.get('x-requested-with') == 'XMLHttpRequest':
                logger.warning(
                    f"[MIDDLEWARE - JSONResponse404Middleware] Resource not found: {request.path}",
                    extra={
                        'status_code': 404,
                        'path': request.path,
                        'method': request.method,
                        'user_id': request.user.id if request.user.is_authenticated else None
                    }
                )
                
                return JsonResponse(
                    {'detail': 'Not found'},
                    status=404
                )
        
        return response

    def process_exception(self, request, exception):
        # Trata exceções Http404 explicitamente
        if isinstance(exception, Http404):
            logger.warning(
                f"[MIDDLEWARE - JSONResponse404Middleware] Resource not found (Http404): {request.path}",
                extra={
                    'status_code': 404,
                    'path': request.path,
                    'method': request.method,
                    'user_id': request.user.id if request.user.is_authenticated else None
                }
            )
            
            return JsonResponse(
                {'detail': 'Not found'},
                status=404
            )
            
class AnonymousUserMiddleware:
    """
    Middleware to handle access to 'employeer' attributes in AnonymousUser
    during access to API documentation.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check if the request is for documentation
        url_name = resolve(request.path_info).url_name
        if url_name in ['redoc', 'swagger-ui', 'schema-json'] and not request.user.is_authenticated:
            # Add a dummy employeer attribute to AnonymousUser
            # for documentation purposes only
            class DummyEmployeer:
                def __init__(self):
                    self.id = None
                    self.companie_id = None
                    
            request.user.employeer = DummyEmployeer()
            
        response = self.get_response(request)
        return response