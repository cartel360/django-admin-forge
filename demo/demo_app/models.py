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


class Subscription(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.CharField(max_length=30, default="starter")
    status = models.CharField(max_length=20, default="active")
    expires_at = models.DateField()
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["expires_at"]

    def __str__(self) -> str:
        return f"{self.customer.company_name} ({self.plan})"


class ApiKey(models.Model):
    name = models.CharField(max_length=80)
    owner_email = models.EmailField()
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="invoices")
    invoice_number = models.CharField(max_length=32, unique=True)
    amount_cents = models.PositiveIntegerField(default=0)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.invoice_number
