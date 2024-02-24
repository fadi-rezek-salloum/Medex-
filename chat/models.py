from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ThreadManager(models.Manager):
    def by_user(self, user):
        """
        Retrieve all threads involving the given user.
        """
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        return self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()

    def get_or_new(self, user, other_id):
        """
        Get or create a thread between the given user and another user.
        """
        if user.id == other_id:
            return None, False

        qlookup1 = Q(first__id=user.id, second__id=other_id)
        qlookup2 = Q(first__id=other_id, second__id=user.id)

        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()

        if qs.exists():
            return qs.first(), False
        else:
            user2 = User.objects.get(id=other_id)
            if user != user2:
                obj = self.model(first=user, second=user2)
                obj.save()
                return obj, True
            return None, False


class Thread(models.Model):
    first = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_thread_first",
        verbose_name=_("First User"),
    )
    second = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_thread_second",
        verbose_name=_("Second User"),
    )

    updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated Date"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created Date"))

    objects = ThreadManager()

    @property
    def room_group_name(self):
        """
        Return the name of the channel group for this thread.
        """
        return f"chat_{self.id}"

    @property
    def get_last_message(self):
        """
        Get the last message in this thread.
        """
        return self.chatmessage_set.order_by("-created").first()


class ChatMessage(models.Model):
    thread = models.ForeignKey(
        Thread, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Thread")
    )
    user = models.ForeignKey(User, verbose_name=_("Sender"), on_delete=models.CASCADE)

    message = models.TextField(verbose_name=_("Message"))

    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))

    is_read = models.BooleanField(default=False, verbose_name=_("Is Read"))

    def __str__(self):
        """
        Return a truncated version of the message for display.
        """
        return Truncator(self.message).chars(50, html=True)
