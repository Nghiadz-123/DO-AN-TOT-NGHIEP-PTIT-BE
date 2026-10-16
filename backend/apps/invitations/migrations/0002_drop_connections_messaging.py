"""Thư mời ứng tuyển thay cho kết bạn (app connections) và nhắn tin (app messaging) đã gỡ khỏi code.

Django không tự xóa bảng của app không còn trong INSTALLED_APPS, nên migration này xóa ba bảng cũ cùng lịch sử
migration của chúng. Không hoàn tác được: dữ liệu kết bạn / tin nhắn cũ bị xóa. DB mới tạo không có các bảng
này thì lệnh chỉ bỏ qua.
"""
from django.db import migrations

DROP_OLD_TABLES = """
DROP TABLE IF EXISTS "messages", "conversations", "connections" CASCADE;
DELETE FROM "django_migrations" WHERE "app" IN ('connections', 'messaging');
"""


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(DROP_OLD_TABLES, reverse_sql=migrations.RunSQL.noop),
    ]
