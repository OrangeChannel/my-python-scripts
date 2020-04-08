import subprocess
import re
def dxdripper(list_of_urls: str):
    splitlist = list_of_urls.splitlines()
    urls = []
    for url in splitlist:
        urls.append(url.replace('/r/', '/l/'))
    files = []
    for url in splitlist:
        files.append(re.search(r'\w*.jpg', url).group())

    for url, file in zip(urls, files):
        subprocess.run(['wget', r'-O', f'/home/stalled/Desktop/dxd/{file}',r'--referer=http://sp.mbga.tv/css/style.css?90918', url])

    for file in files:
        subprocess.run(['pingo', '-sa', f'/home/stalled/Desktop/dxd/{file}'])
