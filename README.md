# OpeninnoLab Account Creator

使用selenium自动创建 Openinno 平台组群及子账号

## 使用方法

1. `pip install -r requirements.txt`安装依赖项，主要为selenium和webdriver-manager
2. 修改[config.py](./config.py)并替换为您个人的openinnolab账号和密码
3. 修改[main.py](./main.py)的Line199的`group_name`和`sub_num`两个参数以设置群组名称和子账号数量