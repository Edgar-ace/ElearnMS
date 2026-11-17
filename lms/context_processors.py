from .models import Instructor
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlsplit


def account_roles(request):
    user = getattr(request, "user", None)
    is_instructor = bool(
        user
        and user.is_authenticated
        and not user.is_staff
        and user.email
        and Instructor.objects.filter(email__iexact=user.email).exists()
    )
    referer = request.META.get("HTTP_REFERER", "")
    if referer and url_has_allowed_host_and_scheme(
        referer,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ) and urlsplit(referer).path != request.path:
        back_url = referer
    else:
        back_url = reverse("dashboard")
    return {"is_instructor_account": is_instructor, "back_url": back_url}
