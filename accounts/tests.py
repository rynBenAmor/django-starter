from django.test import TestCase
from django.urls import reverse


class AllauthTemplateTests(TestCase):
    def test_login_template_used(self):
        url = reverse("account_login")  # Or 'allauth:account_login' if namespaced
        response = self.client.get(url)
        self.assertTemplateUsed(response, "account/login.html")

    def test_signup_template_used(self):
        url = reverse("account_signup")  # Or 'allauth:account_signup'
        response = self.client.get(url)
        self.assertTemplateUsed(response, "account/signup.html")
