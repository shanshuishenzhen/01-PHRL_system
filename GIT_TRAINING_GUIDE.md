# Git & GitHub 新手图文培训手册（Windows10）

> 本文适合零基础新手，涵盖命令行、图形界面（GitHub Desktop）、网页端操作，含常见问题与冲突解决。可直接打印或分享。

---

## 目录
1. [安装 Git（Windows10）](#install)
2. [安装 GitHub Desktop（图形界面）](#desktop)
3. [Git 基本配置](#config)
4. [命令行常用操作](#cli)
5. [GitHub Desktop 常用操作](#gui)
6. [GitHub 网页端常用操作](#web)
7. [常见问题与冲突解决](#faq)
8. [在 GitHub 网页端删除整个项目（仓库）](#delete)
9. [项目中哪些文件/文件夹不应上传GitHub及原因](#no-upload)

---

<a name="install"></a>
## 1. 安装 Git（Windows10）

1. 打开 [Git 官网](https://git-scm.com/download/win)，下载安装包。
2. 双击安装，全部默认即可。
3. 安装完成后，右键任意文件夹，出现"Git Bash Here"即安装成功。

![Git安装界面](https://docs.github.com/assets/images/help/settings/git-config.png)

---

<a name="desktop"></a>
## 2. 安装 GitHub Desktop（图形界面）

1. 打开 [GitHub Desktop 官网](https://desktop.github.com/)，下载安装包。
2. 安装并登录你的 GitHub 账号。

![GitHub Desktop](https://docs.github.com/assets/images/help/desktop/desktop-overview.png)

---

<a name="config"></a>
## 3. Git 基本配置

### 命令行配置用户名和邮箱
```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

### 检查配置
```bash
git config --list
```

---

<a name="cli"></a>
## 4. 命令行常用操作

### 初始化仓库
```bash
cd 你的项目目录
git init
```

### 添加 .gitignore 文件
```bash
echo .venv/ > .gitignore
echo node_modules/ >> .gitignore
```

### 添加并提交代码
```bash
git add .
git commit -m "首次提交"
```

### 关联远程仓库
```bash
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main
```

### 日常同步
```bash
git pull
git add .
git commit -m "修改说明"
git push
```

---

<a name="gui"></a>
## 5. GitHub Desktop 常用操作

1. **克隆远程仓库**
   - 打开 GitHub Desktop，File → Clone repository → 输入仓库地址。
2. **新建本地仓库**
   - File → New repository → 选择本地路径。
3. **添加/提交/推送**
   - 变更会自动显示，填写 Summary，点击 Commit to main。
   - 点击 Push origin 推送到 GitHub。
4. **拉取最新代码**
   - 点击 Pull origin。

![GitHub Desktop 操作界面](https://docs.github.com/assets/images/help/desktop/desktop-commit.png)

---

<a name="web"></a>
## 6. GitHub 网页端常用操作

### 上传文件
1. 进入仓库主页，点击 `Add file` → `Upload files`。
2. 拖拽或选择文件，填写说明，点击提交。

### 新建/编辑文件
- `Add file` → `Create new file`，输入内容后提交。
- 编辑已有文件，点击铅笔图标，修改后提交。

### 删除文件
- 进入文件，点击垃圾桶图标，填写说明后提交。

### 下载文件/仓库
- 单文件：点击 Raw → 右键另存为。
- 整仓库：点击 Code → Download ZIP。

### 查看历史/回滚
- 进入文件，点击 History 查看历史版本。
- 需要回滚时，选择历史版本，点击 Revert 或手动复制内容。

### 分支与 Pull Request
- 新建/切换分支，发起 Pull Request 合并代码。

![GitHub 网页端操作](https://docs.github.com/assets/images/help/repository/repo-file-edit-edit.png)

---

<a name="faq"></a>
## 7. 常见问题与冲突解决

### 1. 推送时报错 refusing to merge unrelated histories
```bash
git pull origin main --allow-unrelated-histories
# 然后再 git push
```

### 2. GitHub 不支持密码推送，如何用 token？
- 进入 GitHub → Settings → Developer settings → Personal access tokens → 生成新 token。
- 推送时用 token 作为密码。

### 3. 文件夹无法网页上传？
- GitHub 网页端不支持直接上传整个文件夹，需用 Git 客户端或 GitHub Desktop。

### 4. 冲突解决
- 拉取代码时如遇冲突，命令行会提示冲突文件。
- 用 VSCode 或 GitHub Desktop 打开，手动选择保留内容，保存后：
```bash
git add 冲突文件
git commit -m "解决冲突"
git push
```

### 5. 其他常见问题
- **文件太大推送失败**：建议用 Git LFS 或拆分文件。
- **误删文件恢复**：在 History 里找到旧版本恢复。

---

<a name="delete"></a>
## 8. 在 GitHub 网页端删除整个项目（仓库）

### 中文操作步骤

1. **登录 GitHub 官网**  
   打开 [https://github.com/](https://github.com/) 并登录你的账号。
2. **进入你的仓库主页**  
   右上角点击头像 → Your repositories → 选择要删除的仓库。
3. **进入仓库设置**  
   在仓库页面上方，点击 `Settings`（设置）标签。
4. **滚动到页面底部**  
   一直往下拉，找到最底部的 `Danger Zone`（危险区域）。
5. **找到"Delete this repository"**  
   点击红色按钮 `Delete this repository`。
6. **确认删除**  
   - 系统会弹出确认框，要求你输入仓库的全名（如 `yourname/yourrepo`）。
   - 按提示输入仓库名，点击确认删除。
7. **完成**  
   仓库会被彻底删除，所有代码和历史都无法恢复（请谨慎操作）。

### 英文界面指引

1. **Login to GitHub**  
   Go to [https://github.com/](https://github.com/) and log in.
2. **Go to your repository**  
   Click your avatar (top right) → Your repositories → select the repo you want to delete.
3. **Open repository settings**  
   Click the `Settings` tab at the top of the repo page.
4. **Scroll to the bottom**  
   Find the `Danger Zone` section at the very bottom.
5. **Find and click "Delete this repository"**  
   Click the red `Delete this repository` button.
6. **Confirm deletion**  
   - A dialog will appear, asking you to type the full repo name (e.g., `yourname/yourrepo`).
   - Type the name and confirm deletion.
7. **Done**  
   The repository will be permanently deleted and cannot be recovered.

### 图示参考

1. ![进入仓库设置](https://docs.github.com/assets/images/help/repository/repo-settings.png)
2. ![危险区域](https://docs.github.com/assets/images/help/repository/delete-repo-button.png)
3. ![确认删除](https://docs.github.com/assets/images/help/repository/delete-repo-confirmation.png)

**注意事项 / Note:**
- 删除操作不可恢复，请提前备份重要代码！
- Once deleted, all collaborators lose access and all code/history is lost forever.

---

<a name="no-upload"></a>
## 9. 项目中哪些文件/文件夹不应上传GitHub及原因

### 1. 为什么不建议上传大文件和依赖文件夹？
- GitHub 有单文件大小限制（100MB），整个仓库推荐不超过1GB。
- 依赖文件夹（如 `.venv/`、`node_modules/`）体积巨大，内容可通过配置文件一键重建。
- 依赖包与操作系统、Python/Node版本强相关，不同电脑直接复制可能会出错。
- 上传这些文件会极大拖慢仓库克隆、推送、拉取速度，浪费存储空间。

### 2. 常见不应上传的文件/文件夹

| 类型           | 说明                                   | 忽略方式         |
|----------------|----------------------------------------|------------------|
| `.venv/`       | Python虚拟环境目录                     | `.venv/`         |
| `__pycache__/` | Python缓存目录                         | `__pycache__/`   |
| `*.pyc`        | Python编译生成的二进制文件              | `*.pyc`          |
| `node_modules/`| Node.js依赖包目录                      | `node_modules/`  |
| `.DS_Store`    | Mac系统自动生成的隐藏文件               | `.DS_Store`      |
| `Thumbs.db`    | Windows系统自动生成的缩略图缓存         | `Thumbs.db`      |
| `.idea/`、`.vscode/` | IDE编辑器配置文件夹               | `.idea/`、`.vscode/` |
| `local_dev.db` | 本地数据库文件（如SQLite）              | `local_dev.db`   |
| `*.log`        | 日志文件                               | `*.log`          |

### 3. 如何忽略这些文件？（.gitignore）

在项目根目录新建或编辑 `.gitignore` 文件，内容如下：

```
# Python
.venv/
__pycache__/
*.pyc

# Node.js
node_modules/

# 数据库和日志
*.db
*.log

# 编辑器
.vscode/
.idea/

# 系统文件
.DS_Store
Thumbs.db
```

只要写在 `.gitignore` 里的文件/文件夹，Git 都不会上传到远程仓库。

### 4. 依赖如何管理？
- **Python 项目**：只需上传 `requirements.txt`，其他人用 `pip install -r requirements.txt` 一键安装所有依赖。
- **Node.js 项目**：只需上传 `package.json` 和 `package-lock.json`，其他人用 `npm install` 自动下载依赖。

### 5. 如果误上传了大文件怎么办？
- **还没推送到远程**：  
  删除大文件，`git add .`，`git commit -m "remove large files"`，再推送。
- **已经推送到远程**：  
  需要用 [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) 或 `git filter-branch` 清理历史，操作较复杂，建议提前咨询。

### 6. 进阶：大文件管理（Git LFS）
- 如果确实需要同步大文件（如模型、数据集），可用 [Git LFS](https://git-lfs.github.com/)（大文件存储扩展）。
- 安装后用命令：
  ```bash
  git lfs track "*.zip"
  git add .gitattributes
  git add yourfile.zip
  git commit -m "add large file"
  git push
  ```

### 7. 总结
- 只上传源码、配置、文档、依赖描述文件，不上传依赖包和本地环境。
- 用 `.gitignore` 管理忽略项，保证仓库干净、轻量、可移植。
- 如需同步大文件，优先用云盘或 Git LFS。

---

## 结语

- 推荐多用 GitHub Desktop 辅助命令行，遇到问题多查官方文档或社区教程。
- 养成良好提交习惯，写清楚 commit 说明。
- 有问题随时问 AI 或查阅 [廖雪峰Git教程](https://www.liaoxuefeng.com/wiki/896043488029600)！ 