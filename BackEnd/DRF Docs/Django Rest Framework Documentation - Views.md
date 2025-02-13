# Source: https://www.django-rest-framework.org/api-guide/views/

## URL: https://www.django-rest-framework.org/api-guide/views/

Title: Views - Django REST framework

URL Source: https://www.django-rest-framework.org/api-guide/views/

Markdown Content:
[decorators.py](https://github.com/encode/django-rest-framework/tree/master/rest_framework/decorators.py) [views.py](https://github.com/encode/django-rest-framework/tree/master/rest_framework/views.py)

[Class-based Views](https://www.django-rest-framework.org/api-guide/views/#class-based-views)
---------------------------------------------------------------------------------------------

> Django's class-based views are a welcome departure from the old-style views.
> 
> — [Reinout van Rees](https://reinout.vanrees.org/weblog/2011/08/24/class-based-views-usage.html)

REST framework provides an `APIView` class, which subclasses Django's `View` class.

`APIView` classes are different from regular `View` classes in the following ways:

*   Requests passed to the handler methods will be REST framework's `Request` instances, not Django's `HttpRequest` instances.
*   Handler methods may return REST framework's `Response`, instead of Django's `HttpResponse`. The view will manage content negotiation and setting the correct renderer on the response.
*   Any `APIException` exceptions will be caught and mediated into appropriate responses.
*   Incoming requests will be authenticated and appropriate permission and/or throttle checks will be run before dispatching the request to the handler method.

Using the `APIView` class is pretty much the same as using a regular `View` class, as usual, the incoming request is dispatched to an appropriate handler method such as `.get()` or `.post()`. Additionally, a number of attributes may be set on the class that control various aspects of the API policy.

For example:

```
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

class ListUsers(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)
```

* * *

**Note**: The full methods, attributes on, and relations between Django REST Framework's `APIView`, `GenericAPIView`, various `Mixins`, and `Viewsets` can be initially complex. In addition to the documentation here, the [Classy Django REST Framework](http://www.cdrf.co/) resource provides a browsable reference, with full methods and attributes, for each of Django REST Framework's class-based views.

* * *

[API policy attributes](https://www.django-rest-framework.org/api-guide/views/#api-policy-attributes)
-----------------------------------------------------------------------------------------------------

The following attributes control the pluggable aspects of API views.

### [.renderer\_classes](https://www.django-rest-framework.org/api-guide/views/#renderer_classes)

### [.parser\_classes](https://www.django-rest-framework.org/api-guide/views/#parser_classes)

### [.authentication\_classes](https://www.django-rest-framework.org/api-guide/views/#authentication_classes)

### [.throttle\_classes](https://www.django-rest-framework.org/api-guide/views/#throttle_classes)

### [.permission\_classes](https://www.django-rest-framework.org/api-guide/views/#permission_classes)

### [.content\_negotiation\_class](https://www.django-rest-framework.org/api-guide/views/#content_negotiation_class)

[API policy instantiation methods](https://www.django-rest-framework.org/api-guide/views/#api-policy-instantiation-methods)
---------------------------------------------------------------------------------------------------------------------------

The following methods are used by REST framework to instantiate the various pluggable API policies. You won't typically need to override these methods.

### [.get\_throttles(self)](https://www.django-rest-framework.org/api-guide/views/#get_throttlesself)

### [.get\_permissions(self)](https://www.django-rest-framework.org/api-guide/views/#get_permissionsself)

### [.get\_content\_negotiator(self)](https://www.django-rest-framework.org/api-guide/views/#get_content_negotiatorself)

### [.get\_exception\_handler(self)](https://www.django-rest-framework.org/api-guide/views/#get_exception_handlerself)

[API policy implementation methods](https://www.django-rest-framework.org/api-guide/views/#api-policy-implementation-methods)
-----------------------------------------------------------------------------------------------------------------------------

The following methods are called before dispatching to the handler method.

### [.check\_permissions(self, request)](https://www.django-rest-framework.org/api-guide/views/#check_permissionsself-request)

### [.check\_throttles(self, request)](https://www.django-rest-framework.org/api-guide/views/#check_throttlesself-request)

### [.perform\_content\_negotiation(self, request, force=False)](https://www.django-rest-framework.org/api-guide/views/#perform_content_negotiationself-request-forcefalse)

[Dispatch methods](https://www.django-rest-framework.org/api-guide/views/#dispatch-methods)
-------------------------------------------------------------------------------------------

The following methods are called directly by the view's `.dispatch()` method. These perform any actions that need to occur before or after calling the handler methods such as `.get()`, `.post()`, `put()`, `patch()` and `.delete()`.

### [.initial(self, request, \*args, \*\*kwargs)](https://www.django-rest-framework.org/api-guide/views/#initialself-request-args-kwargs)

Performs any actions that need to occur before the handler method gets called. This method is used to enforce permissions and throttling, and perform content negotiation.

You won't typically need to override this method.

### [.handle\_exception(self, exc)](https://www.django-rest-framework.org/api-guide/views/#handle_exceptionself-exc)

Any exception thrown by the handler method will be passed to this method, which either returns a `Response` instance, or re-raises the exception.

The default implementation handles any subclass of `rest_framework.exceptions.APIException`, as well as Django's `Http404` and `PermissionDenied` exceptions, and returns an appropriate error response.

If you need to customize the error responses your API returns you should subclass this method.

### [.initialize\_request(self, request, \*args, \*\*kwargs)](https://www.django-rest-framework.org/api-guide/views/#initialize_requestself-request-args-kwargs)

Ensures that the request object that is passed to the handler method is an instance of `Request`, rather than the usual Django `HttpRequest`.

You won't typically need to override this method.

### [.finalize\_response(self, request, response, \*args, \*\*kwargs)](https://www.django-rest-framework.org/api-guide/views/#finalize_responseself-request-response-args-kwargs)

Ensures that any `Response` object returned from the handler method will be rendered into the correct content type, as determined by the content negotiation.

You won't typically need to override this method.

* * *

[Function Based Views](https://www.django-rest-framework.org/api-guide/views/#function-based-views)
---------------------------------------------------------------------------------------------------

> Saying \[that class-based views\] is always the superior solution is a mistake.
> 
> — [Nick Coghlan](http://www.boredomandlaziness.org/2012/05/djangos-cbvs-are-not-mistake-but.html)

REST framework also allows you to work with regular function based views. It provides a set of simple decorators that wrap your function based views to ensure they receive an instance of `Request` (rather than the usual Django `HttpRequest`) and allows them to return a `Response` (instead of a Django `HttpResponse`), and allow you to configure how the request is processed.

[@api\_view()](https://www.django-rest-framework.org/api-guide/views/#api_view)
-------------------------------------------------------------------------------

**Signature:** `@api_view(http_method_names=['GET'])`

The core of this functionality is the `api_view` decorator, which takes a list of HTTP methods that your view should respond to. For example, this is how you would write a very simple view that just manually returns some data:

```
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view()
def hello_world(request):
    return Response({"message": "Hello, world!"})
```

This view will use the default renderers, parsers, authentication classes etc specified in the [settings](https://www.django-rest-framework.org/api-guide/settings/).

By default only `GET` methods will be accepted. Other methods will respond with "405 Method Not Allowed". To alter this behavior, specify which methods the view allows, like so:

```
@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})
```

[API policy decorators](https://www.django-rest-framework.org/api-guide/views/#api-policy-decorators)
-----------------------------------------------------------------------------------------------------

To override the default settings, REST framework provides a set of additional decorators which can be added to your views. These must come _after_ (below) the `@api_view` decorator. For example, to create a view that uses a [throttle](https://www.django-rest-framework.org/api-guide/throttling/) to ensure it can only be called once per day by a particular user, use the `@throttle_classes` decorator, passing a list of throttle classes:

```
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle

class OncePerDayUserThrottle(UserRateThrottle):
    rate = '1/day'

@api_view(['GET'])
@throttle_classes([OncePerDayUserThrottle])
def view(request):
    return Response({"message": "Hello for today! See you tomorrow!"})
```

These decorators correspond to the attributes set on `APIView` subclasses, described above.

The available decorators are:

*   `@renderer_classes(...)`
*   `@parser_classes(...)`
*   `@authentication_classes(...)`
*   `@throttle_classes(...)`
*   `@permission_classes(...)`

Each of these decorators takes a single argument which must be a list or tuple of classes.

[View schema decorator](https://www.django-rest-framework.org/api-guide/views/#view-schema-decorator)
-----------------------------------------------------------------------------------------------------

To override the default schema generation for function based views you may use the `@schema` decorator. This must come _after_ (below) the `@api_view` decorator. For example:

```
from rest_framework.decorators import api_view, schema
from rest_framework.schemas import AutoSchema

class CustomAutoSchema(AutoSchema):
    def get_link(self, path, method, base_url):
        # override view introspection here...

@api_view(['GET'])
@schema(CustomAutoSchema())
def view(request):
    return Response({"message": "Hello for today! See you tomorrow!"})
```

This decorator takes a single `AutoSchema` instance, an `AutoSchema` subclass instance or `ManualSchema` instance as described in the [Schemas documentation](https://www.django-rest-framework.org/api-guide/schemas/). You may pass `None` in order to exclude the view from schema generation.

```
@api_view(['GET'])
@schema(None)
def view(request):
    return Response({"message": "Will not appear in schema!"})
```

---


# Crawl Statistics

- **Source:** https://www.django-rest-framework.org/api-guide/views/
- **Depth:** 5
- **Pages processed:** 1
- **Crawl method:** api
- **Duration:** 1.51 seconds
- **Crawl completed:** 12/24/2024, 8:48:16 AM

