# Source: https://www.django-rest-framework.org/api-guide/responses/

## URL: https://www.django-rest-framework.org/api-guide/responses/

Title: Responses - Django REST framework

URL Source: https://www.django-rest-framework.org/api-guide/responses/

Markdown Content:
[response.py](https://github.com/encode/django-rest-framework/tree/master/rest_framework/response.py)

> Unlike basic HttpResponse objects, TemplateResponse objects retain the details of the context that was provided by the view to compute the response. The final output of the response is not computed until it is needed, later in the response process.
> 
> — [Django documentation](https://docs.djangoproject.com/en/stable/ref/template-response/)

REST framework supports HTTP content negotiation by providing a `Response` class which allows you to return content that can be rendered into multiple content types, depending on the client request.

The `Response` class subclasses Django's `SimpleTemplateResponse`. `Response` objects are initialised with data, which should consist of native Python primitives. REST framework then uses standard HTTP content negotiation to determine how it should render the final response content.

There's no requirement for you to use the `Response` class, you can also return regular `HttpResponse` or `StreamingHttpResponse` objects from your views if required. Using the `Response` class simply provides a nicer interface for returning content-negotiated Web API responses, that can be rendered to multiple formats.

Unless you want to heavily customize REST framework for some reason, you should always use an `APIView` class or `@api_view` function for views that return `Response` objects. Doing so ensures that the view can perform content negotiation and select the appropriate renderer for the response, before it is returned from the view.

* * *

[Creating responses](https://www.django-rest-framework.org/api-guide/responses/#creating-responses)
---------------------------------------------------------------------------------------------------

[Response()](https://www.django-rest-framework.org/api-guide/responses/#response)
---------------------------------------------------------------------------------

**Signature:** `Response(data, status=None, template_name=None, headers=None, content_type=None)`

Unlike regular `HttpResponse` objects, you do not instantiate `Response` objects with rendered content. Instead you pass in unrendered data, which may consist of any Python primitives.

The renderers used by the `Response` class cannot natively handle complex datatypes such as Django model instances, so you need to serialize the data into primitive datatypes before creating the `Response` object.

You can use REST framework's `Serializer` classes to perform this data serialization, or use your own custom serialization.

Arguments:

*   `data`: The serialized data for the response.
*   `status`: A status code for the response. Defaults to 200. See also [status codes](https://www.django-rest-framework.org/api-guide/status-codes/).
*   `template_name`: A template name to use if `HTMLRenderer` is selected.
*   `headers`: A dictionary of HTTP headers to use in the response.
*   `content_type`: The content type of the response. Typically, this will be set automatically by the renderer as determined by content negotiation, but there may be some cases where you need to specify the content type explicitly.

* * *

[Attributes](https://www.django-rest-framework.org/api-guide/responses/#attributes)
-----------------------------------------------------------------------------------

[.data](https://www.django-rest-framework.org/api-guide/responses/#data)
------------------------------------------------------------------------

The unrendered, serialized data of the response.

[.status\_code](https://www.django-rest-framework.org/api-guide/responses/#status_code)
---------------------------------------------------------------------------------------

The numeric status code of the HTTP response.

[.content](https://www.django-rest-framework.org/api-guide/responses/#content)
------------------------------------------------------------------------------

The rendered content of the response. The `.render()` method must have been called before `.content` can be accessed.

[.template\_name](https://www.django-rest-framework.org/api-guide/responses/#template_name)
-------------------------------------------------------------------------------------------

The `template_name`, if supplied. Only required if `HTMLRenderer` or some other custom template renderer is the accepted renderer for the response.

[.accepted\_renderer](https://www.django-rest-framework.org/api-guide/responses/#accepted_renderer)
---------------------------------------------------------------------------------------------------

The renderer instance that will be used to render the response.

Set automatically by the `APIView` or `@api_view` immediately before the response is returned from the view.

The media type that was selected by the content negotiation stage.

Set automatically by the `APIView` or `@api_view` immediately before the response is returned from the view.

[.renderer\_context](https://www.django-rest-framework.org/api-guide/responses/#renderer_context)
-------------------------------------------------------------------------------------------------

A dictionary of additional context information that will be passed to the renderer's `.render()` method.

Set automatically by the `APIView` or `@api_view` immediately before the response is returned from the view.

* * *

[Standard HttpResponse attributes](https://www.django-rest-framework.org/api-guide/responses/#standard-httpresponse-attributes)
-------------------------------------------------------------------------------------------------------------------------------

The `Response` class extends `SimpleTemplateResponse`, and all the usual attributes and methods are also available on the response. For example you can set headers on the response in the standard way:

```
response = Response()
response['Cache-Control'] = 'no-cache'
```

[.render()](https://www.django-rest-framework.org/api-guide/responses/#render)
------------------------------------------------------------------------------

**Signature:** `.render()`

As with any other `TemplateResponse`, this method is called to render the serialized data of the response into the final response content. When `.render()` is called, the response content will be set to the result of calling the `.render(data, accepted_media_type, renderer_context)` method on the `accepted_renderer` instance.

You won't typically need to call `.render()` yourself, as it's handled by Django's standard response cycle.

---


# Crawl Statistics

- **Source:** https://www.django-rest-framework.org/api-guide/responses/
- **Depth:** 5
- **Pages processed:** 1
- **Crawl method:** api
- **Duration:** 1.35 seconds
- **Crawl completed:** 12/24/2024, 8:47:42 AM

