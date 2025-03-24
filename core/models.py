import uuid
from django.db import models
from django.contrib.auth.models import User, Group


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Account(BaseModel):
    name = models.CharField(max_length=255)
    app_secret_token = models.CharField(max_length=255, unique=True)
    website = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts_created")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts_updated", blank=True,
                                   null=True)

    def __str__(self):
        return self.name


class Destination(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="destinations")
    url = models.URLField()
    http_method = models.CharField(max_length=10, choices=[("GET", "GET"), ("POST", "POST"), ("PUT", "PUT")])
    headers = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="destinations_created")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="destinations_updated", blank=True,
                                   null=True)

    def __str__(self):
        return f"{self.account.name} -> {self.url}"


class AccountMember(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="account_memberships")
    role = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.role.name} in {self.account.name}"


class Log(BaseModel):
    event_id = models.CharField(max_length=255, unique=True, db_index=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="logs")
    received_timestamp = models.DateTimeField(db_index=True)
    processed_timestamp = models.DateTimeField(null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name="logs", blank=True, null=True)
    received_data = models.JSONField()
    status = models.CharField(max_length=20, choices=[("success", "Success"), ("failed", "Failed")])

    def __str__(self):
        return f"Log {self.event_id} - {self.status}"
