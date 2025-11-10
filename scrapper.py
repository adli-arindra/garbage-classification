import os
import glob
import random
import time
from PIL import Image
from icrawler.builtin import GoogleImageCrawler, BingImageCrawler, BaiduImageCrawler
from icrawler.downloader import ImageDownloader

class RotatingUserAgentDownloader(ImageDownloader):
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    ]

    def get_headers(self, referer):
        headers = super().get_headers(referer)
        headers["User-Agent"] = random.choice(self.USER_AGENTS)
        return headers


def convert_images_to_jpg(folder_name):
    image_files = glob.glob(os.path.join(folder_name, "*"))
    saved_count = len(glob.glob(os.path.join(folder_name, "*.jpg")))

    for img_path in image_files:
        if img_path.endswith(".jpg"):
            continue
        try:
            with Image.open(img_path) as im:
                rgb_im = im.convert("RGB")
                new_path = os.path.join(folder_name, f"{saved_count}.jpg")
                rgb_im.save(new_path, format="JPEG")
            os.remove(img_path)
            saved_count += 1
        except Exception as e:
            print(f"Skipped {img_path}: {e}")
    return saved_count


def get_remaining_count(folder_name, max_num):
    return max_num - len(glob.glob(os.path.join(folder_name, "*.jpg")))


def generate_keywords(label):
    """You can expand this if you want to add variations or synonyms per label."""
    return [
        label + " waste",
        label + " garbage",
        label + " trash",
        ]


def scrape_images(label_list, output_root="scraped", max_num=1000):
    crawlers = [
        ("Google", GoogleImageCrawler),
        ("Bing", BingImageCrawler),
        ("Baidu", BaiduImageCrawler),
    ]

    for label in label_list:
        folder_name = os.path.join(output_root, label.replace(" ", "_").lower())
        os.makedirs(folder_name, exist_ok=True)

        print(f"\n⏳ Scraping '{label}' into {folder_name} ...")

        for engine_name, Crawler in crawlers:
            for keyword in generate_keywords(label):
                remaining = get_remaining_count(folder_name, max_num)
                if remaining <= 0:
                    break

                print(f"🔍 {engine_name}: Searching '{keyword}' for {remaining} more images...")

                crawler = Crawler(
                    downloader_cls=RotatingUserAgentDownloader,
                    storage={"root_dir": folder_name},
                    downloader_threads=4,
                )

                try:
                    crawler.crawl(keyword=keyword, max_num=remaining, min_size=(128, 128))
                except Exception as e:
                    print(f"⚠️ {engine_name} failed with '{keyword}': {e}")
                    time.sleep(5)

                convert_images_to_jpg(folder_name)

        final_count = len(glob.glob(os.path.join(folder_name, "*.jpg")))
        print(f"✅ Finished '{label}' with {final_count}/{max_num} images\n")


if __name__ == "__main__":
    labels = [
        "plastic bottle",
        "glass",
        "metal can",
        "paper",
        "cardboard",
        "brochure",
        "styrofoam",
        "plastic bag",
        "mask",
        "straws",
        "battery",
        "tissue",
        "diaper",
        "food",
        "leafs"
    ]

    scrape_images(labels, output_root="scrapped", max_num=500)