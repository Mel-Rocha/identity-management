from django.db import models


class LanguageChoices(models.TextChoices):
    ENGLISH = "EN", "English"
    SPANISH = "ES", "Spanish"
    PORTUGUESE = "PT", "Portuguese"


class TimezoneChoices(models.TextChoices):
    UTC_MINUS_11 = "UTC-11", "(GMT-11:00) International Date Line West"
    UTC = "UTC+0", "(GMT+0:00) Coordinated Universal Time"
    UTC_PLUS_3 = "UTC+3", "(GMT+3:00) Moscow, St. Petersburg"


class CurrencyChoices(models.TextChoices):
    USD = "USD", "US Dollar"
    EUR = "EUR", "Euro"
    BRL = "BRL", "Brazilian Real"
