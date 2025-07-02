
📋 手动上传说明

如果自动推送失败，请尝试以下手动方法：

方法1: 使用GitHub Desktop
1. 下载并安装 GitHub Desktop
2. 克隆仓库: https://github.com/shanshuishenzhen/01-PHRL_system
3. 将本地文件复制到克隆的仓库目录
4. 在GitHub Desktop中提交并推送

方法2: 使用Web界面上传
1. 访问: https://github.com/shanshuishenzhen/01-PHRL_system
2. 点击 "uploading an existing file"
3. 将项目文件打包为zip上传
4. 解压并整理文件结构

方法3: 使用SSH
1. 生成SSH密钥: ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
2. 添加SSH密钥到GitHub账户
3. 更改远程URL: git remote set-url origin git@github.com:shanshuishenzhen/01-PHRL_system.git
4. 推送: git push -u origin main

方法4: 分批推送
1. 创建.gitignore忽略大文件
2. 分批添加文件: git add 目录名/
3. 分批提交和推送

网络问题排查:
- 检查防火墙设置
- 尝试使用VPN
- 检查代理设置
- 联系网络管理员
