from django.contrib import admin
from .models import Account, Destination, AccountMember, Log

admin.site.register(Account)
admin.site.register(Destination)
admin.site.register(AccountMember)
admin.site.register(Log)
