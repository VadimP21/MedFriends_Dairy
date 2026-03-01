import uuid

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models


class MfBaseModelNoId(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(_("Дата создания"), auto_now = True,)
    updated_at = models.DateTimeField(_("Дата обновления"), auto_now = True)

    def clean(self) -> None:
        if self.created_at and self.updated_at:
            if self.created_at > self.updated_at:
                raise DjangoValidationError(_("Дата создания не может быть позже даты обновления."))
        return super().clean()

    # def save(self, *args, **kwargs):
    #     if self._state.adding and not self.created_at:
    #         self.created_at = timezone.now()
    #     if not self.updated_at:
    #         self.updated_at = timezone.now()
    #     result = super().save(*args, **kwargs)
    #     self.full_clean()
    #     return result


class MfBaseModel(MfBaseModelNoId):
    class Meta(MfBaseModelNoId.Meta):
        abstract = True

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, null=False, blank=False
    )


def _upload_avatar_to(instance, filename: str) -> str:
    return f"avatars/{instance.id}/{filename}"
