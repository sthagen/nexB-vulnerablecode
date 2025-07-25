#
# Copyright (c) nexB Inc. and others. All rights reserved.
# VulnerableCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/vulnerablecode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.validators import validate_email
from django_altcha import AltchaField

from vulnerabilities.models import ApiUser


class PackageSearchForm(forms.Form):

    search = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Package name, purl or purl fragment"},
        ),
    )


class VulnerabilitySearchForm(forms.Form):

    search = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Vulnerability id or alias such as CVE or GHSA"}
        ),
    )


class AdvisorySearchForm(forms.Form):

    search = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Advisory id or alias such as CVE or GHSA"}),
    )


class ApiUserCreationForm(forms.ModelForm):
    """Support a simplified creation for API-only users directly from the UI."""

    captcha = AltchaField(floating=True, hidefooter=True)

    class Meta:
        model = ApiUser
        fields = (
            "email",
            "first_name",
            "last_name",
        )

    def __init__(self, *args, **kwargs):
        super(ApiUserCreationForm, self).__init__(*args, **kwargs)
        email_field = self.fields["email"]
        first_name_field = self.fields["first_name"]
        last_name_field = self.fields["last_name"]
        email_field.required = True
        email_field.widget.attrs["class"] = "input"
        email_field.widget.attrs["placeholder"] = "Email"
        first_name_field.widget.attrs["class"] = "input"
        first_name_field.widget.attrs["placeholder"] = "First Name"
        last_name_field.widget.attrs["class"] = "input"
        last_name_field.widget.attrs["placeholder"] = "Last Name"
        email_field.label = ""
        first_name_field.label = ""
        last_name_field.label = ""

    def save(self, commit=True):
        return ApiUser.objects.create_api_user(
            username=self.cleaned_data["email"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )

    def clean_username(self):
        username = self.cleaned_data["email"]
        validate_email(username)
        return username

    def save_m2m(self):
        pass


class PipelineSchedulePackageForm(forms.Form):
    search = forms.CharField(
        required=True,
        label=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search a pipeline...",
                "class": "input ",
            },
        ),
    )


class AdminLoginForm(AdminAuthenticationForm):
    captcha = AltchaField(floating=True, hidefooter=True)
