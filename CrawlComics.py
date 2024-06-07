import requests
from lxml import html
import time
import os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse


# Hàm để lấy các thẻ a với đường dẫn cụ thể và lưu các link vào một mảng
def get_links(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    links = []
    if response.status_code == 200:
        tree = html.fromstring(response.content)

        n = 1
        while True:
            xpath = f'/html/body/div[1]/div[1]/div[2]/div/div[4]/div/div[{n}]/div[1]/a'
            link_elements = tree.xpath(xpath)

            if not link_elements:
                break

            for link_element in link_elements:
                link = link_element.get('href')
                if link:
                    # Kiểm tra nếu link không bao gồm giao thức, thêm 'https://truyenqqviet.com'
                    if not link.startswith('http'):
                        link = 'https://truyenqqviet.com' + link
                    links.append(link)
                    print(link)

            n += 1
    else:
        print(f"Request failed with status code: {response.status_code}")

    return links


# Hàm xử lý một liên kết
def process_single_link(link, folder_path, chapter_num):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    response = requests.get(link, headers=headers)

    if response.status_code == 200:
        tree = html.fromstring(response.content)

        page_num = 1
        chapter_links = []
        while True:
            xpath = f'//*[@id="page_{page_num}"]/img'
            img_elements = tree.xpath(xpath)

            if not img_elements:
                break

            for img_element in img_elements:
                img_src = img_element.get('src')
                if img_src:
                    chapter_links.append(img_src)

            page_num += 1

        # Lưu các liên kết hình ảnh vào tệp txt
        if chapter_links:
            # Tạo tên tệp và đường dẫn đầy đủ
            file_path = os.path.join(folder_path, f'Chapter_{chapter_num}.txt')
            with open(file_path, 'w') as file:
                for chapter_link in chapter_links:
                    file.write(chapter_link + '\n')

    else:
        print(f"Failed to access {link} with status code: {response.status_code}")

    time.sleep(2)


# Hàm để xử lý các liên kết từ nhiều URL với đa luồng
def process_links_multithread(urls, base_folder, num_chapters):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {}

        for url in urls:
            # Tạo thư mục con cho mỗi URL
            url_path = urlparse(url).path.replace('/', '_').strip('_')
            folder_path = os.path.join(base_folder, url_path)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            links = get_links(url)
            links = links[:num_chapters]  # Lấy num_chapters liên kết đầu tiên
            chapter_num = 1

            for link in links:
                future = executor.submit(process_single_link, link, folder_path, chapter_num)
                future_to_url[future] = link
                chapter_num += 1

        for future in future_to_url:
            link = future_to_url[future]
            try:
                future.result()
            except Exception as e:
                print(f"Link {link} generated an exception: {e}")


# Yêu cầu người dùng nhập tên thư mục và tạo thư mục nếu chưa tồn tại
base_folder = input("Nhập tên thư mục để lưu các tệp txt: ")
if not os.path.exists(base_folder):
    os.makedirs(base_folder)

# Nhập các URL cần truy cập
urls = input("Nhập các URL (phân tách bằng dấu phẩy): ").split(',')

# Lấy số chương cần xử lý
num_chapters = int(input("Nhập số chương cần xử lý: "))

# Xử lý các liên kết từ nhiều URL với đa luồng
process_links_multithread(urls, base_folder, num_chapters)
