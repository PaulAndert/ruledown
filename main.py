import requests
import shutil
import os
import sys

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
step = 10

def get_thumbnail_urls(user_id, page):
    page = page * 50 - 50
    url = f'https://rule34.xxx/index.php?page=favorites&s=view&id={user_id}&pid={page}'
    
    result = requests.get(url, headers=headers)
    html = result.content.decode()

    image_ids = []
    for line in html.split('\n'):
        # <img src="https://wimg.rule34.xxx/thumbnails//2507/<name>.ext" title="..." border="0" alt="image_thumb">
        if '<img src' in line:
            image_ids.append(line.split('<img src="')[1][:-2])

    return image_ids

def get_first_image_url(th_url):
    image_url = th_url.replace('https://wimg.rule34.xxx/thumbnails//', 'https://rule34.xxx//samples/')
    image_url = image_url.replace('/thumbnail_', '/sample_')
    image_url = image_url.split('?')[0]
    return image_url

def get_second_image_url(th_url):
    image_url = th_url.replace('https://wimg.rule34.xxx/thumbnails//', 'https://wimg.rule34.xxx//images/')
    image_url = image_url.replace('/thumbnail_', '/')
    image_url = image_url.split('?')[0]
    return image_url

def download_image(image_url, path):

    request = None

    for ext in ['jpg', 'jpeg', 'png', 'gif']:
        image_url = os.path.splitext(image_url)[0] + '.' + ext
        
        name_split = image_url.split('/')
        name = name_split[len(name_split)-1]

        request = requests.get(image_url, stream=True, headers=headers)
        if request.status_code == 200:
            with open(path + name, 'wb') as f:
                request.raw.decode_content = True
                shutil.copyfileobj(request.raw, f)
            return 200

    return request.status_code

def get_all_pages(user_id):
    url = f'https://rule34.xxx/index.php?page=favorites&s=view&id={user_id}'
    
    result = requests.get(url, headers=headers)
    html = result.content.decode()

    for line in html.split('>'):
        if 'name="lastpage"' in line:
            # <a href="#" onclick="document.location='?page=favorites&amp;s=view&amp;id=<user_id>&amp;pid=<highest_pid>'; return false;" name="lastpage">&gt;&gt;</a>
            page_count = int(int(line.split(';')[3][4:-1]) / 50)
            page_numbers = []
            for i in range(1,page_count+1):
                page_numbers.append(i)
            return page_numbers

    return [1]

def check_if_already_exists(th_url, path):
    name_split = th_url.split('/')
    name = name_split[len(name_split)-1]
    name = name.split('?')[0]
    name = name.split('_')[1]
    name = name.split('.')[0]
    for file in os.listdir(path):
        if name in file:
            return True

def print_progress(skipped, downloaded, pages_size):
    
    images_max = pages_size * 50

    skipped_vis = ''
    if skipped == 0:
        skipped_vis = '          '
    else:
        skipped_border = (skipped / images_max) * 10
        for i in range(0, 10):
            if i < skipped_border:
                skipped_vis += '#'
            else:
                skipped_vis += ' '
    downloaded_vis = ''
    if downloaded == 0:
        downloaded_vis = '          '
    else:
        downloaded_border = (downloaded / images_max) * 10
        for i in range(0, 10):
            if i < downloaded_border:
                downloaded_vis += '#'
            else:
                downloaded_vis += ' '

    print('\x1b[1A\x1b[2K', end='')
    print('\x1b[1A\x1b[2K', end='')
    print(f'Images skipped:    [{skipped_vis}] {skipped}/{images_max}')
    print(f'Images downloaded: [{downloaded_vis}] {downloaded}/{images_max}')
    

def main():
    print("Download Rule34 Favorites Page")

    user_id = None
    page = None
    path = './'

    if len(sys.argv) > 1:
        args = sys.argv
        args.pop(0)
        for arg in args:
            if '-uid' in arg:
                user_id = arg.split('-uid=')[1]
            if '-page' in arg:
                page = arg.split('-page=')[1]
            if '-path' in arg:
                path = arg.split('-path=')[1]
                if path[:-1] != '/':
                    path += '/'
            if '-h' in arg or '-help' in arg:
                print("""
-uid=<number>       : user id, found in the URL of your My Profile Page
-page=<number>      : page number that should be downloaded (enter 'all' to download all pages)
-path=<string>      : path where all images should be saved to
-h | -help          : user id, found in the URL of your 'My Profile' Page
""")
                return

    if user_id == None:
        print('\nYou can find your Profile ID in the URL of the \'My Profile\' page.')
        user_id = input('Profile ID: ')

    if page == None:
        print('\nPlease state the Page that you want downloaded (or insert \'all\' to download all favorites)')
        page = input('Page: ')

    pages = []
    if page == 'all':
        pages = get_all_pages(user_id)
    else:
        pages.append(int(page))

    print('\n')

    skipped = 0
    downloaded = 0
    for page in pages:
        for th_url in get_thumbnail_urls(user_id, page):

            print_progress(skipped, downloaded, len(pages))
            if check_if_already_exists(th_url, path):
                skipped += 1
                continue

            image_url = get_first_image_url(th_url)

            if download_image(image_url, path) != 200:
                image_url = get_second_image_url(th_url)
                resp = download_image(image_url, path)
                if resp != 200:
                    print(f'ERROR: {image_url} produced http code: {resp}')
            downloaded += 1

    print_progress(skipped, downloaded, len(pages))

main()