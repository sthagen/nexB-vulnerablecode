#
# Copyright (c) nexB Inc. and others. All rights reserved.
# VulnerableCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/vulnerablecode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from vulnerabilities.api import PermissionBasedUserRateThrottle
from vulnerabilities.models import ApiUser


def simulate_throttle_usage(url, client, mock_use_count):
    throttle = PermissionBasedUserRateThrottle()
    request = client.get(url).wsgi_request

    if cache_key := throttle.get_cache_key(request, view=None):
        print(cache_key)
        now = throttle.timer()
        cache.set(cache_key, [now] * mock_use_count)


class PermissionBasedRateThrottleApiTests(APITestCase):
    def setUp(self):
        # Reset the api throttling to properly test the rate limit on anon users.
        # DRF stores throttling state in cache, clear cache to reset throttling.
        # See https://www.django-rest-framework.org/api-guide/throttling/#setting-up-the-cache
        cache.clear()

        permission_low = Permission.objects.get(codename="throttle_0_low")
        permission_medium = Permission.objects.get(codename="throttle_1_medium")
        permission_high = Permission.objects.get(codename="throttle_2_high")
        permission_unrestricted = Permission.objects.get(codename="throttle_3_unrestricted")

        # user with low permission
        self.th_low_user = ApiUser.objects.create_api_user(username="z@mail.com")
        self.th_low_user.user_permissions.add(permission_low)
        self.th_low_user_auth = f"Token {self.th_low_user.auth_token.key}"
        self.th_low_user_csrf_client = APIClient(enforce_csrf_checks=True)
        self.th_low_user_csrf_client.credentials(HTTP_AUTHORIZATION=self.th_low_user_auth)

        # basic user without any special throttling perm
        self.basic_user = ApiUser.objects.create_api_user(username="a@mail.com")
        self.basic_user_auth = f"Token {self.basic_user.auth_token.key}"
        self.basic_user_csrf_client = APIClient(enforce_csrf_checks=True)
        self.basic_user_csrf_client.credentials(HTTP_AUTHORIZATION=self.basic_user_auth)

        # medium permission
        self.th_medium_user = ApiUser.objects.create_api_user(username="b@mail.com")
        self.th_medium_user.user_permissions.add(permission_medium)
        self.th_medium_user_auth = f"Token {self.th_medium_user.auth_token.key}"
        self.th_medium_user_csrf_client = APIClient(enforce_csrf_checks=True)
        self.th_medium_user_csrf_client.credentials(HTTP_AUTHORIZATION=self.th_medium_user_auth)

        # high permission
        self.th_high_user = ApiUser.objects.create_api_user(username="c@mail.com")
        self.th_high_user.user_permissions.add(permission_high)
        self.th_high_user_auth = f"Token {self.th_high_user.auth_token.key}"
        self.th_high_user_csrf_client = APIClient(enforce_csrf_checks=True)
        self.th_high_user_csrf_client.credentials(HTTP_AUTHORIZATION=self.th_high_user_auth)

        # unrestricted throttling perm
        self.th_unrestricted_user = ApiUser.objects.create_api_user(username="d@mail.com")
        self.th_unrestricted_user.user_permissions.add(permission_unrestricted)
        self.th_unrestricted_user_auth = f"Token {self.th_unrestricted_user.auth_token.key}"
        self.th_unrestricted_user_csrf_client = APIClient(enforce_csrf_checks=True)
        self.th_unrestricted_user_csrf_client.credentials(
            HTTP_AUTHORIZATION=self.th_unrestricted_user_auth
        )

        # unrestricted throttling for group user
        group, _ = Group.objects.get_or_create(name="Test Unrestricted")
        group.permissions.add(permission_unrestricted)

        self.th_group_user = ApiUser.objects.create_api_user(username="g@mail.com")
        self.th_group_user.groups.add(group)
        self.th_group_user_auth = f"Token {self.th_group_user.auth_token.key}"
        self.th_group_user_csrf_client = APIClient(enforce_csrf_checks=True)
        self.th_group_user_csrf_client.credentials(HTTP_AUTHORIZATION=self.th_group_user_auth)

        self.csrf_client_anon = APIClient(enforce_csrf_checks=True)
        self.csrf_client_anon_1 = APIClient(enforce_csrf_checks=True)

    def test_user_with_low_perm_throttling(self):
        simulate_throttle_usage(
            url="/api/packages",
            client=self.th_low_user_csrf_client,
            mock_use_count=10799,
        )

        response = self.th_low_user_csrf_client.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # exhausted 10800/hr allowed requests.
        response = self.th_low_user_csrf_client.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_basic_user_throttling(self):
        simulate_throttle_usage(
            url="/api/packages",
            client=self.basic_user_csrf_client,
            mock_use_count=14399,
        )

        response = self.basic_user_csrf_client.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # exhausted 14400/hr allowed requests.
        response = self.basic_user_csrf_client.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_user_with_medium_perm_throttling(self):
        simulate_throttle_usage(
            url="/api/packages",
            client=self.th_medium_user_csrf_client,
            mock_use_count=14399,
        )

        response = self.th_medium_user_csrf_client.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # exhausted 14400/hr allowed requests for user with 14400 perm.
        response = self.th_medium_user_csrf_client.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_user_with_high_perm_throttling(self):
        simulate_throttle_usage(
            url="/api/packages",
            client=self.th_high_user_csrf_client,
            mock_use_count=17999,
        )

        response = self.th_high_user_csrf_client.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # exhausted 18000/hr allowed requests for user with 18000 perm.
        response = self.th_high_user_csrf_client.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_user_with_unrestricted_perm_throttling(self):
        simulate_throttle_usage(
            url="/api/packages",
            client=self.th_unrestricted_user_csrf_client,
            mock_use_count=20000,
        )

        # no throttling for user with unrestricted perm.
        response = self.th_unrestricted_user_csrf_client.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_in_group_with_unrestricted_perm_throttling(self):
        simulate_throttle_usage(
            url="/api/packages",
            client=self.th_group_user_csrf_client,
            mock_use_count=20000,
        )

        # no throttling for user in group with unrestricted perm.
        response = self.th_group_user_csrf_client.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anon_throttling(self):
        simulate_throttle_usage(
            url="/api/packages",
            client=self.csrf_client_anon,
            mock_use_count=3599,
        )

        response = self.csrf_client_anon.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # exhausted 3600/hr allowed requests for anon.
        response = self.csrf_client_anon.get("/api/packages")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(
            response.data.get("message"),
            "Your request has been throttled. Please contact support@nexb.com",
        )

        response = self.csrf_client_anon.get("/api/vulnerabilities")
        # 429 - too many requests for anon user
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(
            response.data.get("message"),
            "Your request has been throttled. Please contact support@nexb.com",
        )

        data = json.dumps({"purls": ["pkg:foo/bar"]})

        response = self.csrf_client_anon.post(
            "/api/packages/bulk_search", data=data, content_type="application/json"
        )
        # 429 - too many requests for anon user
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(
            response.data.get("message"),
            "Your request has been throttled. Please contact support@nexb.com",
        )
