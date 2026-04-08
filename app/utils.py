def send_new_post_notification(email: str, post_title: str):
    print(f"📧 [BACKGROUND] Gửi thông báo đến {email}: Bài viết '{post_title}' đã được đăng thành công!")
    # Sau này có thể thêm email thật (smtplib)