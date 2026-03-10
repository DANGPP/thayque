"""
Script to insert sample data for Authors, Categories, and Publishers
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_service.settings')
django.setup()

from app.models import Category, Author, Publisher
from django.utils.text import slugify

def insert_sample_data():
    print("Starting to insert sample data...")
    
    # ============ INSERT CATEGORIES ============
    print("\n📚 Inserting Categories...")
    categories_data = [
        {"name": "Lập Trình", "description": "Sách về lập trình và công nghệ phần mềm"},
        {"name": "Văn Học Việt Nam", "description": "Văn học trong nước, tác phẩm của các nhà văn Việt"},
        {"name": "Văn Học Nước Ngoài", "description": "Văn học thế giới, sách dịch"},
        {"name": "Kinh Tế - Quản Trị", "description": "Sách về kinh tế, kinh doanh và quản lý"},
        {"name": "Khoa Học - Công Nghệ", "description": "Sách khoa học, công nghệ và kỹ thuật"},
        {"name": "Kỹ Năng Sống", "description": "Sách phát triển bản thân, kỹ năng mềm"},
        {"name": "Thiếu Nhi", "description": "Sách dành cho trẻ em"},
        {"name": "Tâm Lý - Tình Cảm", "description": "Sách tâm lý học, tình cảm"},
        {"name": "Lịch Sử", "description": "Sách lịch sử Việt Nam và thế giới"},
        {"name": "Triết Học", "description": "Sách triết học, tư tưởng"},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data["name"],
            defaults={
                "slug": slugify(cat_data["name"]),
                "description": cat_data["description"],
                "is_active": True
            }
        )
        categories.append(category)
        status = "✅ Created" if created else "⚠️  Already exists"
        print(f"  {status}: {category.name}")
    
    # ============ INSERT AUTHORS ============
    print("\n✍️  Inserting Authors...")
    authors_data = [
        {"name": "Nguyễn Nhật Ánh", "bio": "Nhà văn nổi tiếng với các tác phẩm thiếu nhi và tuổi học trò", "nationality": "Việt Nam"},
        {"name": "Tô Hoài", "bio": "Nhà văn Việt Nam, tác giả Dế Mèn phiêu lưu ký", "nationality": "Việt Nam"},
        {"name": "Nam Cao", "bio": "Nhà văn hiện thực Việt Nam thời kỳ trước cách mạng", "nationality": "Việt Nam"},
        {"name": "Haruki Murakami", "bio": "Nhà văn nổi tiếng người Nhật Bản", "nationality": "Nhật Bản"},
        {"name": "Paulo Coelho", "bio": "Nhà văn Brazil, tác giả Nhà giả kim", "nationality": "Brazil"},
        {"name": "J.K. Rowling", "bio": "Tác giả series Harry Potter nổi tiếng thế giới", "nationality": "Anh"},
        {"name": "Dale Carnegie", "bio": "Nhà văn Mỹ về kỹ năng giao tiếp và phát triển bản thân", "nationality": "Mỹ"},
        {"name": "Yuval Noah Harari", "bio": "Sử gia và tác giả Sapiens", "nationality": "Israel"},
        {"name": "Nguyễn Hiến Lê", "bio": "Nhà giáo, nhà nghiên cứu văn học và ngôn ngữ học", "nationality": "Việt Nam"},
        {"name": "Tôn Thất Liên", "bio": "Nhà văn Việt Nam với nhiều tác phẩm văn học thiếu nhi", "nationality": "Việt Nam"},
    ]
    
    authors = []
    for author_data in authors_data:
        author, created = Author.objects.get_or_create(
            name=author_data["name"],
            defaults={
                "bio": author_data["bio"],
                "nationality": author_data["nationality"]
            }
        )
        authors.append(author)
        status = "✅ Created" if created else "⚠️  Already exists"
        print(f"  {status}: {author.name} ({author.nationality})")
    
    # ============ INSERT PUBLISHERS ============
    print("\n🏢 Inserting Publishers...")
    publishers_data = [
        {"name": "NXB Trẻ", "description": "Nhà xuất bản sách thiếu nhi và văn học", "address": "TP. Hồ Chí Minh", "phone": "028-39316211"},
        {"name": "NXB Kim Đồng", "description": "Nhà xuất bản sách thiếu nhi hàng đầu Việt Nam", "address": "Hà Nội", "phone": "024-39434730"},
        {"name": "NXB Văn Học", "description": "Nhà xuất bản chuyên về văn học trong và ngoài nước", "address": "Hà Nội", "phone": "024-38222135"},
        {"name": "NXB Lao Động", "description": "Nhà xuất bản sách kinh tế, kỹ năng sống", "address": "Hà Nội", "phone": "024-38514221"},
        {"name": "NXB Hội Nhà Văn", "description": "Nhà xuất bản của Hội Nhà văn Việt Nam", "address": "Hà Nội", "phone": "024-38223340"},
        {"name": "NXB Thế Giới", "description": "Nhà xuất bản chuyên sách dịch và sách nước ngoài", "address": "Hà Nội", "phone": "024-38253841"},
        {"name": "First News", "description": "Công ty phát hành sách hàng đầu Việt Nam", "address": "TP. Hồ Chí Minh", "phone": "028-38437799"},
        {"name": "Alphabooks", "description": "Nhà xuất bản sách về phát triển bản thân", "address": "TP. Hồ Chí Minh", "phone": "028-38236724"},
        {"name": "NXB Chính Trị Quốc Gia", "description": "Nhà xuất bản về chính trị, lịch sử", "address": "Hà Nội", "phone": "024-38221633"},
        {"name": "NXB Tổng Hợp TP.HCM", "description": "Nhà xuất bản đa dạng lĩnh vực", "address": "TP. Hồ Chí Minh", "phone": "028-38221796"},
    ]
    
    publishers = []
    for pub_data in publishers_data:
        publisher, created = Publisher.objects.get_or_create(
            name=pub_data["name"],
            defaults={
                "address": pub_data["address"],
                "phone": pub_data["phone"]
            }
        )
        publishers.append(publisher)
        status = "✅ Created" if created else "⚠️  Already exists"
        print(f"  {status}: {publisher.name}")
    
    # ============ SUMMARY ============
    print("\n" + "="*50)
    print("📊 SUMMARY:")
    print(f"   Categories: {Category.objects.count()} total")
    print(f"   Authors: {Author.objects.count()} total")
    print(f"   Publishers: {Publisher.objects.count()} total")
    print("="*50)
    print("✅ Sample data insertion completed!")

if __name__ == "__main__":
    insert_sample_data()
