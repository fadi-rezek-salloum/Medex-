from rest_framework.generics import CreateAPIView

from .models import ContactMessage
from .serializers import ContactMessageSerializer


class CreateContactMessageView(CreateAPIView):
    queryset = ContactMessage.objects.all()
    http_method_names = [
        "post",
    ]
    serializer_class = ContactMessageSerializer
