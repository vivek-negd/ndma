from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email_address, password=None, **extra_fields):
        if not email_address:
            raise ValueError("Email address is required")

        email_address = self.normalize_email(email_address)

        user = self.model(
            email_address=email_address,   # 🔥 FIXED FIELD NAME
            **extra_fields
        )

        user.set_password(password)   # 🔥 MUST hash password
        user.save(using=self._db)

        return user

    def create_superuser(self, email_address, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email_address, password, **extra_fields)