from django.db import models


class Customer(models.Model):
    company_name = models.CharField(max_length=120)
    contact_email = models.EmailField()
    plan = models.CharField(max_length=30, default="starter")
    seats = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.company_name
