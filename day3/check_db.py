import pandas as pd
from sqlalchemy import create_engine, text

# Đường dẫn tới database
DB_PATH = r"D:\train_intern\day3\cafef_database.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

print("🔍 Đang kiểm tra dữ liệu trong cafef_database.db ...\n")

with engine.connect() as conn:
    # Đếm tổng số bài
    total = conn.execute(text("SELECT COUNT(*) FROM articles")).scalar()
    print(f"📊 Tổng số bài viết trong bảng 'articles': {total}\n")

    # Lấy dữ liệu
    df = pd.read_sql_query("""
        SELECT 
            id,
            title,
            link,
            crawled_at
        FROM articles 
        ORDER BY id DESC
    """, conn)

# ====================== CẤU HÌNH HIỂN THỊ ĐẸP ======================
pd.set_option('display.max_colwidth', None)      # Hiển thị toàn bộ nội dung title và link
pd.set_option('display.width', None)             # Không giới hạn chiều rộng
pd.set_option('display.max_rows', None)          # Hiển thị tất cả các hàng
pd.set_option('display.colheader_justify', 'left')  # Căn trái tiêu đề cột

# Đổi tên cột cho dễ nhìn hơn (tùy chọn)
df_display = df.rename(columns={
    'id': 'ID',
    'title': 'Tiêu đề',
    'link': 'Link',
    'crawled_at': 'Thời gian crawl'
})

# In ra màn hình đẹp hơn
print("=" * 140)
print("🔥 DANH SÁCH BÀI VIẾT TỪ CAFÉF.VN (Mới nhất ở trên cùng)")
print("=" * 140)

# In từng bài một cách rõ ràng, dễ đọc
for idx, row in df_display.iterrows():
    print(f"ID: {row['ID']}")
    print(f"Tiêu đề : {row['Tiêu đề']}")
    print(f"Link    : {row['Link']}")
    print(f"Thời gian: {row['Thời gian crawl']}")
    print("-" * 120)   # Dòng phân cách giữa các bài

print(f"\n✅ Tổng cộng {len(df)} bài viết đã được hiển thị.")