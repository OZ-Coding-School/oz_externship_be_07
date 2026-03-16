from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from apps.community.models.post_model import Post, PostAttachment, PostImage


class Command(BaseCommand):
    help = "PostImage/PostAttachment admin 테스트 데이터 생성"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--posts", type=int, default=5, help="대상 게시글 수 (기본: 5)")
        parser.add_argument("--images-per-post", type=int, default=2, help="게시글당 이미지 수 (기본: 2)")
        parser.add_argument("--attachments-per-post", type=int, default=2, help="게시글당 첨부파일 수 (기본: 2)")

    def handle(self, *args: Any, **options: Any) -> None:
        num_posts = max(1, options["posts"])
        images_per_post = max(0, options["images_per_post"])
        attachments_per_post = max(0, options["attachments_per_post"])

        posts = list(Post.objects.order_by("-created_at")[:num_posts])
        if not posts:
            self.stdout.write(self.style.ERROR("생성 실패: 게시글 데이터가 없습니다."))
            return

        created_images = 0
        skipped_images = 0
        created_attachments = 0
        skipped_attachments = 0

        for post in posts:
            # 이미지 샘플 생성
            for idx in range(1, images_per_post + 1):
                img_url = f"https://picsum.photos/seed/admin_seed_post_{post.id}_{idx}/640/360"
                if PostImage.objects.filter(post=post, img_url=img_url).exists():
                    skipped_images += 1
                    continue
                PostImage.objects.create(post=post, img_url=img_url)
                created_images += 1

            # 첨부파일 샘플 생성
            for idx in range(1, attachments_per_post + 1):
                file_name = f"admin_seed_post_{post.id}_{idx}.pdf"
                file_url = f"https://example.com/admin-seed/post-{post.id}/{file_name}"

                if PostAttachment.objects.filter(post=post, file_name=file_name).exists():
                    skipped_attachments += 1
                    continue

                PostAttachment.objects.create(
                    post=post,
                    file_name=file_name,
                    file_url=file_url,
                )
                created_attachments += 1

        total_images = PostImage.objects.count()
        total_attachments = PostAttachment.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                "완료: "
                f"이미지 생성 {created_images} / 건너뜀 {skipped_images} / 총 {total_images} | "
                f"첨부 생성 {created_attachments} / 건너뜀 {skipped_attachments} / 총 {total_attachments}"
            )
        )
