"""API views for the Merchants document model."""

import json
import time

from django.http import JsonResponse, HttpResponse, HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from ..opensearch_models import Merchant


@method_decorator(csrf_exempt, name="dispatch")
class MerchantView(View):
    """API views for the Merchants index."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """List the first 10 merchants."""
        del request  # unused

        search = Merchant.search()
        search = search.query("match_all")
        search = search.source(["_id", "name", "description", "website"])
        search = search.sort("name")
        search = search.extra(size=10)

        response = search.execute()

        merchants_serialized = [
            {
                "id": hit.meta.id,
                "name": hit.name,
                "description": hit.description,
                "website": hit.website,
            }
            for hit in response
        ]

        return JsonResponse({"merchants": merchants_serialized})

    def post(self, request: HttpRequest) -> HttpResponse:
        """Create a new merchant."""
        now = int(time.time() * 1000)
        try:
            data = json.loads(request.body)
            merchant = Merchant(
                name=data["name"],
                description=data["description"],
                website=data["website"],
                created=now,
                updated=now,
                deleted=None,
            )
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"error": "Invalid data"}, status=400)

        merchant.save()
        merchant_serialized = {
            "id": merchant.meta.id,
            "name": merchant.name,
            "description": merchant.description,
            "website": merchant.website,
        }

        return JsonResponse({"merchant": merchant_serialized}, status=201)
