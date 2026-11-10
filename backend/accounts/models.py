from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class FoodFlowUserManager(BaseUserManager):
    """Manager for email-based accounts (no username field)."""

    use_in_migrations = True

    def _create(self, email: str, password: str | None, **extra):
        if not email:
            raise ValueError('An email address is required.')
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra):
        extra.setdefault('is_staff', False)
        extra.setdefault('is_superuser', False)
        return self._create(email, password, **extra)

    def create_superuser(self, email: str, password: str | None = None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        if not extra.get('is_staff') or not extra.get('is_superuser'):
            raise ValueError('A superuser must have is_staff=True and is_superuser=True.')
        return self._create(email, password, **extra)


class User(AbstractUser):
    """FoodFlow user — email based login (Swiggy style)."""

    username = None
    email = models.EmailField('email address', unique=True)
    phone = models.CharField('phone number', max_length=20, blank=True, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = FoodFlowUserManager()

    def __str__(self) -> str:
        return self.email
