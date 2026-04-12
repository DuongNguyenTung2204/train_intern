from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation_email(self, order_id: int):
    try:
        from .models import Order
        order = Order.objects.prefetch_related("items").get(pk=order_id)
        lines = "\n".join(
            f"  {item.quantity}x {item.product_name}  —  {item.unit_price} đ"
            for item in order.items.all()
        )
        send_mail(
            subject=f"[EShop] Order #{order.pk} confirmed!",
            message=(
                f"Hi {order.shipping_name},\n\n"
                f"Order #{order.pk} placed successfully.\n\n"
                f"Items:\n{lines}\n\n"
                f"Total: {order.total_price} đ\n"
                f"Shipping to: {order.shipping_address}\n\n"
                "Thank you for shopping with EShop!\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user_email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def send_order_status_update_email(order_id: int, new_status: str):
    from .models import Order
    try:
        order = Order.objects.get(pk=order_id)
        send_mail(
            subject=f"[EShop] Order #{order.pk} — now {new_status.upper()}",
            message=(
                f"Hi {order.shipping_name},\n\n"
                f"Your order #{order.pk} status is: {new_status.upper()}.\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user_email],
            fail_silently=True,
        )
    except Order.DoesNotExist:
        pass
