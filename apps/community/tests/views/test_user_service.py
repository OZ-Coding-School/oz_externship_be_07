from django.test import TransactionTestCase

from apps.community.services.user_search import UserSearchService
from apps.users.models.models import User


class UserSignalAndSearchTest(TransactionTestCase):
    def test_signal_search_flow(self) -> None:
        user = User.objects.create_user(
            email="test@test.com",
            name="test",
            nickname="test",
            password="qwer1234",
            birthday="1995-01-01",
            gender="M",
            status="ACTIVE",
        )

        results = UserSearchService.search_users("te")
        self.assertEqual(len(results), 1)

        user.status = "DEACTIVATED"
        user.save()

        results_after = UserSearchService.search_users("te")
        self.assertEqual(len(results_after), 0)
