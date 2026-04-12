from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    if created:
        from .tasks import send_order_confirmation_email
        send_order_confirmation_email.delay(instance.pk)
    elif instance.status != Order.Status.PENDING:
        from .tasks import send_order_status_update_email
        send_order_status_update_email.delay(instance.pk, instance.status)
