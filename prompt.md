写个脚本 拉取 https://tlidb.com/cn/ 网站下的页面，只下载 cn/ 目录下的，只需要下载4级链接即可。

1. 安装所需的Python包：
   ```
   pip install -r requirements.txt
   ```

2. 运行脚本：
   ```
   python cn_crawler.py
   ```

脚本将使用多线程技术从 https://tlidb.com/cn/ 下载页面，并将它们保存到当前工作目录下的一个名为 "downloaded_pages" 的目录中。文件将按照原始网站路径的文件夹结构进行组织。

默认使用8个并发线程进行下载，可以通过修改脚本中的 `num_threads` 参数来调整线程数量。