from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.community.models.post_model import Post, PostLike


class Command(BaseCommand):
    help = "PostLike admin 테스트 데이터 생성(중복 생성 방지)"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=5, help="사용할 유저 수 (기본: 5)")
        parser.add_argument("--posts", type=int, default=5, help="사용할 게시글 수 (기본: 5)")
        parser.add_argument("--max-create", type=int, default=30, help="최대 생성 건수 (기본: 30)")

    def handle(self, *args, **options):
        num_users = max(1, options["users"])
        num_posts = max(1, options["posts"])
        max_create = max(1, options["max_create"])

        User = get_user_model()
        users = list(User.objects.order_by("id")[:num_users])
        posts = list(Post.objects.order_by("-created_at")[:num_posts])

        if not users:
            self.stdout.write(self.style.ERROR("유저 데이터가 없습니다."))
            return
        if not posts:
            self.stdout.write(self.style.ERROR("게시글 데이터가 없습니다."))
            return

        created_count = 0
        skipped_count = 0

        for post in posts:
            for user in users:
                if created_count >= max_create:
                    break

                if PostLike.objects.filter(user=user, post=post).exists():
                    skipped_count += 1
                    continue

                PostLike.objects.create(
                    user=user,
                    post=post,
                    is_liked=((user.id + post.id) % 2 == 0),
                )
                created_count += 1

            if created_count >= max_create:
                break

        total_count = PostLike.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"생성 {created_count}건 / 건너뜀 {skipped_count}건 / 총 {total_count}건"
            )
        )
