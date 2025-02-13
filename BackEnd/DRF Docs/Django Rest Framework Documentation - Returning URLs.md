# Source: https://www.django-rest-framework.org/api-guide/reverse/

## URL: https://www.django-rest-framework.org/api-guide/reverse/

Title: Returning URLs - Django REST framework

URL Source: https://www.django-rest-framework.org/api-guide/reverse/

Markdown Content:
Returning URLs - Django REST framework
===============

[GitHub](https://github.com/encode/django-rest-framework/tree/master) [Next](https://www.django-rest-framework.org/api-guide/exceptions/) [Previous](https://www.django-rest-framework.org/api-guide/format-suffixes/) [Search](https://www.django-rest-framework.org/api-guide/reverse/#mkdocs_search_modal) [Django REST framework](https://www.django-rest-framework.org/)

*   [Home](https://www.django-rest-framework.org/)
*   [Tutorial](https://www.django-rest-framework.org/api-guide/reverse/#)
    *   [Quickstart](https://www.django-rest-framework.org/tutorial/quickstart/)
    *   [1 - Serialization](https://www.django-rest-framework.org/tutorial/1-serialization/)
    *   [2 - Requests and responses](https://www.django-rest-framework.org/tutorial/2-requests-and-responses/)
    *   [3 - Class based views](https://www.django-rest-framework.org/tutorial/3-class-based-views/)
    *   [4 - Authentication and permissions](https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/)
    *   [5 - Relationships and hyperlinked APIs](https://www.django-rest-framework.org/tutorial/5-relationships-and-hyperlinked-apis/)
    *   [6 - Viewsets and routers](https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/)
*   [API Guide](https://www.django-rest-framework.org/api-guide/reverse/#)
    *   [Requests](https://www.django-rest-framework.org/api-guide/requests/)
    *   [Responses](https://www.django-rest-framework.org/api-guide/responses/)
    *   [Views](https://www.django-rest-framework.org/api-guide/views/)
    *   [Generic views](https://www.django-rest-framework.org/api-guide/generic-views/)
    *   [Viewsets](https://www.django-rest-framework.org/api-guide/viewsets/)
    *   [Routers](https://www.django-rest-framework.org/api-guide/routers/)
    *   [Parsers](https://www.django-rest-framework.org/api-guide/parsers/)
    *   [Renderers](https://www.django-rest-framework.org/api-guide/renderers/)
    *   [Serializers](https://www.django-rest-framework.org/api-guide/serializers/)
    *   [Serializer fields](https://www.django-rest-framework.org/api-guide/fields/)
    *   [Serializer relations](https://www.django-rest-framework.org/api-guide/relations/)
    *   [Validators](https://www.django-rest-framework.org/api-guide/validators/)
    *   [Authentication](https://www.django-rest-framework.org/api-guide/authentication/)
    *   [Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
    *   [Caching](https://www.django-rest-framework.org/api-guide/caching/)
    *   [Throttling](https://www.django-rest-framework.org/api-guide/throttling/)
    *   [Filtering](https://www.django-rest-framework.org/api-guide/filtering/)
    *   [Pagination](https://www.django-rest-framework.org/api-guide/pagination/)
    *   [Versioning](https://www.django-rest-framework.org/api-guide/versioning/)
    *   [Content negotiation](https://www.django-rest-framework.org/api-guide/content-negotiation/)
    *   [Metadata](https://www.django-rest-framework.org/api-guide/metadata/)
    *   [Schemas](https://www.django-rest-framework.org/api-guide/schemas/)
    *   [Format suffixes](https://www.django-rest-framework.org/api-guide/format-suffixes/)
    *   [Returning URLs](https://www.django-rest-framework.org/api-guide/reverse/)
    *   [Exceptions](https://www.django-rest-framework.org/api-guide/exceptions/)
    *   [Status codes](https://www.django-rest-framework.org/api-guide/status-codes/)
    *   [Testing](https://www.django-rest-framework.org/api-guide/testing/)
    *   [Settings](https://www.django-rest-framework.org/api-guide/settings/)
*   [Topics](https://www.django-rest-framework.org/api-guide/reverse/#)
    *   [Documenting your API](https://www.django-rest-framework.org/topics/documenting-your-api/)
    *   [Internationalization](https://www.django-rest-framework.org/topics/internationalization/)
    *   [AJAX, CSRF & CORS](https://www.django-rest-framework.org/topics/ajax-csrf-cors/)
    *   [HTML & Forms](https://www.django-rest-framework.org/topics/html-and-forms/)
    *   [Browser Enhancements](https://www.django-rest-framework.org/topics/browser-enhancements/)
    *   [The Browsable API](https://www.django-rest-framework.org/topics/browsable-api/)
    *   [REST, Hypermedia & HATEOAS](https://www.django-rest-framework.org/topics/rest-hypermedia-hateoas/)
*   [Community](https://www.django-rest-framework.org/api-guide/reverse/#)
    *   [Tutorials and Resources](https://www.django-rest-framework.org/community/tutorials-and-resources/)
    *   [Third Party Packages](https://www.django-rest-framework.org/community/third-party-packages/)
    *   [Contributing to REST framework](https://www.django-rest-framework.org/community/contributing/)
    *   [Project management](https://www.django-rest-framework.org/community/project-management/)
    *   [Release Notes](https://www.django-rest-framework.org/community/release-notes/)
    *   [3.15 Announcement](https://www.django-rest-framework.org/community/3.15-announcement/)
    *   [3.14 Announcement](https://www.django-rest-framework.org/community/3.14-announcement/)
    *   [3.13 Announcement](https://www.django-rest-framework.org/community/3.13-announcement/)
    *   [3.12 Announcement](https://www.django-rest-framework.org/community/3.12-announcement/)
    *   [3.11 Announcement](https://www.django-rest-framework.org/community/3.11-announcement/)
    *   [3.10 Announcement](https://www.django-rest-framework.org/community/3.10-announcement/)
    *   [3.9 Announcement](https://www.django-rest-framework.org/community/3.9-announcement/)
    *   [3.8 Announcement](https://www.django-rest-framework.org/community/3.8-announcement/)
    *   [3.7 Announcement](https://www.django-rest-framework.org/community/3.7-announcement/)
    *   [3.6 Announcement](https://www.django-rest-framework.org/community/3.6-announcement/)
    *   [3.5 Announcement](https://www.django-rest-framework.org/community/3.5-announcement/)
    *   [3.4 Announcement](https://www.django-rest-framework.org/community/3.4-announcement/)
    *   [3.3 Announcement](https://www.django-rest-framework.org/community/3.3-announcement/)
    *   [3.2 Announcement](https://www.django-rest-framework.org/community/3.2-announcement/)
    *   [3.1 Announcement](https://www.django-rest-framework.org/community/3.1-announcement/)
    *   [3.0 Announcement](https://www.django-rest-framework.org/community/3.0-announcement/)
    *   [Kickstarter Announcement](https://www.django-rest-framework.org/community/kickstarter-announcement/)
    *   [Mozilla Grant](https://www.django-rest-framework.org/community/mozilla-grant/)
    *   [Funding](https://www.django-rest-framework.org/community/funding/)
    *   [Jobs](https://www.django-rest-framework.org/community/jobs/)

×

### Documentation search

Close

*   [Returning URLs](https://www.django-rest-framework.org/api-guide/reverse/#returning-urls)
*   [reverse](https://www.django-rest-framework.org/api-guide/reverse/#reverse)
*   [reverse\_lazy](https://www.django-rest-framework.org/api-guide/reverse/#reverse_lazy)

* * *

[reverse.py](https://github.com/encode/django-rest-framework/tree/master/rest_framework/reverse.py)

[Returning URLs](https://www.django-rest-framework.org/api-guide/reverse/#returning-urls)
=========================================================================================

> The central feature that distinguishes the REST architectural style from other network-based styles is its emphasis on a uniform interface between components.
> 
> — Roy Fielding, [Architectural Styles and the Design of Network-based Software Architectures](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm#sec_5_1_5)

As a rule, it's probably better practice to return absolute URIs from your Web APIs, such as `http://example.com/foobar`, rather than returning relative URIs, such as `/foobar`.

The advantages of doing so are:

*   It's more explicit.
*   It leaves less work for your API clients.
*   There's no ambiguity about the meaning of the string when it's found in representations such as JSON that do not have a native URI type.
*   It makes it easy to do things like markup HTML representations with hyperlinks.

REST framework provides two utility functions to make it more simple to return absolute URIs from your Web API.

There's no requirement for you to use them, but if you do then the self-describing API will be able to automatically hyperlink its output for you, which makes browsing the API much easier.

[reverse](https://www.django-rest-framework.org/api-guide/reverse/#reverse)
---------------------------------------------------------------------------

**Signature:** `reverse(viewname, *args, **kwargs)`

Has the same behavior as [`django.urls.reverse`](https://docs.djangoproject.com/en/stable/ref/urlresolvers/#reverse), except that it returns a fully qualified URL, using the request to determine the host and port.

You should **include the request as a keyword argument** to the function, for example:

```
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from django.utils.timezone import now

class APIRootView(APIView):
    def get(self, request):
        year = now().year
        data = {
            ...
            'year-summary-url': reverse('year-summary', args=[year], request=request)
        }
        return Response(data)
```

[reverse\_lazy](https://www.django-rest-framework.org/api-guide/reverse/#reverse_lazy)
--------------------------------------------------------------------------------------

**Signature:** `reverse_lazy(viewname, *args, **kwargs)`

Has the same behavior as [`django.urls.reverse_lazy`](https://docs.djangoproject.com/en/stable/ref/urlresolvers/#reverse-lazy), except that it returns a fully qualified URL, using the request to determine the host and port.

As with the `reverse` function, you should **include the request as a keyword argument** to the function, for example:

```
api_root = reverse_lazy('api-root', request=request)
```

Documentation built with [MkDocs](http://www.mkdocs.org/).

---


# Crawl Statistics

- **Source:** https://www.django-rest-framework.org/api-guide/reverse/
- **Depth:** 5
- **Pages processed:** 1
- **Crawl method:** api
- **Duration:** 1.35 seconds
- **Crawl completed:** 12/24/2024, 8:59:34 AM

