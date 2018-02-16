# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.auth.models import User
from django.db import models

from encrypted_model_fields.fields import EncryptedCharField

from .api.API import API
from .api.BalanceFromAddress import BalanceFromAddress


class Currency(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    crypto = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, default='Portfolio')

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fiat = models.CharField(max_length=10, default='USD')
    portfolio = models.ForeignKey(
        Portfolio,
        blank=True,
        null=True,
        on_delete=models.SET_NULL)

    def __str__(self):
        return "%s %s" % (self.user, self.fiat)


class Exchange(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name


class ExchangeAccount(models.Model):
    portfolio = models.ForeignKey(Portfolio, blank=True, null=True,
        on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    key = EncryptedCharField(max_length=1024)
    secret = EncryptedCharField(max_length=1024)
    passphrase = EncryptedCharField(
        max_length=1024,
        default=None,
        blank=True,
        null=True,
        help_text='<ul><li>Optional</li></ul>')

    def __str__(self):
        return "%s %s" % (self.user.username, self.exchange.name)


class ExchangeBalance(models.Model):
    exchange_account = models.ForeignKey(
        ExchangeAccount,
        on_delete=models.CASCADE
    )
    currency = models.CharField(max_length=10)
    amount = models.FloatField(default=None, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s %s" % (
            self.exchange_account,
            self.amount,
            self.currency,
            self.timestamp)


class ManualInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    currency = models.CharField(max_length=10)
    amount = models.FloatField(default=None, blank=True, null=True)
    portfolio = models.ForeignKey(
        Portfolio,
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s %s %s" % (self.user.username, self.timestamp,
                                self.currency, self.amount)


class AddressInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now=True)
    address = models.CharField(max_length=100)
    amount = models.FloatField(default=None, blank=True, null=True)
    portfolio = models.ForeignKey(
        Portfolio,
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s %s %s %s" % (self.user.username, self.timestamp,
                                   self.currency, self.address, self.amount)

    @property
    def block_explorer_link(self):
        if self.currency == 'BTC':
            addr = 'https://blockchain.info/de/address/{}'.format(self.address)
        elif self.currency == 'BCH':
            addr = 'https://blockdozer.com/insight/address/bitcoincash:{}'\
                                                    .format(self.address)
        elif self.currency == 'LTC':
            addr = 'https://chainz.cryptoid.info/ltc/address.dws?{}.htm'\
                                                    .format(self.address)
        elif self.currency == 'XRP':
            addr = 'https://bithomp.com/explorer/{}'.format(self.address)
        elif self.currency == 'ETH':
            addr = 'https://etherscan.io/address/{}'.format(self.address)
        else:
            addr = "#"
        return addr


class TimeSeries(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    amount = models.FloatField(default=None, blank=True, null=True)
    fiat = models.CharField(max_length=10, default='USD')

    def __str__(self):
        return "%s %s %s %s" % (self.user.username, self.timestamp,
                                self.amount, self.fiat)


class BalanceTimeSeries(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    amount = models.FloatField(default=None, blank=True, null=True)
    currency = models.CharField(max_length=10, default='BTC')
    fiat = models.CharField(max_length=10, default='USD')

    def __str__(self):
        return "%s %s %s %s" % (self.user.username, self.timestamp,
                                self.amount, self.currency)


class CurrencyTimestamp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10, default='BTC')
    timestamp = models.DateTimeField(auto_now=True)


def update_exchange_balances(exchange_accounts):
    has_errors = False
    errors = []
    for exchange_account in exchange_accounts:
        api = API(exchange_account)
        balances, error = api.getBalances()

        if error:
            has_errors = True
            errors.append(error)
        else:
            exchange_balances = ExchangeBalance.objects.filter(
                exchange_account=exchange_account)

            for currency in balances:
                exchange_balance, created = ExchangeBalance.objects.get_or_create(
                    exchange_account=exchange_account,
                    currency=currency)

                exchange_balance.amount = balances[currency]
                exchange_balance.save()

                ct, crt = CurrencyTimestamp.objects.get_or_create(
                                                    user=exchange_account.user,
                                                    currency=currency)
                ct.timestamp = datetime.datetime.now()
                ct.save()

            for exchange_balance in exchange_balances:
                currency = exchange_balance.currency
                if currency not in balances:
                    exchange_balance.delete()

    return (has_errors, errors)

def update_address_input_balances(user):
    address_api = BalanceFromAddress()
    address_inputs = AddressInput.objects.filter(user=user)

    result = address_api.getBalances(address_inputs)

    for address_input in address_inputs:
        address_input.amount = result[address_input.address]
        address_input.save()

        ct, crt = CurrencyTimestamp.objects.get_or_create(
                                            user=user,
                                            currency=address_input.currency)
        ct.timestamp = datetime.datetime.now()
        ct.save()


def get_aggregated_balances(exchange_accounts, manual_inputs, address_inputs):
    crypto_balances = {}
    for exchange_account in exchange_accounts:
        exchange_balances = ExchangeBalance.objects.filter(
            exchange_account=exchange_account)

        # aggregate latest balances
        for exchange_balance in exchange_balances:
            currency = exchange_balance.currency
            amount = exchange_balance.amount

            if currency in crypto_balances:
                crypto_balances[currency] += amount
            else:
                crypto_balances[currency] = amount

    for manual_input in manual_inputs:
        currency = manual_input.currency
        amount = manual_input.amount

        if currency in crypto_balances:
            crypto_balances[currency] += amount
        else:
            crypto_balances[currency] = amount

    for address_input in address_inputs:
        currency = address_input.currency
        amount = address_input.amount

        if currency in crypto_balances:
            crypto_balances[currency] += amount
        else:
            crypto_balances[currency] = amount

    return crypto_balances
