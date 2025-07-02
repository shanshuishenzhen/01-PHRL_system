# 项目上传 GitHub 全流程指南

以本地项目（如 `D:\01-PHRL_system`）为例，适用于初学者和团队协作。

---

## 1. 注册并创建 GitHub 仓库

1. 打开 [GitHub官网](https://github.com/) 注册账号（如已有可跳过）。
2. 登录后，点击右上角 ➕，选择"New repository"。
3. 填写仓库名（如 `PHRL_exam_system`），可选描述，建议选择"Private"（私有）或"Public"（公开）。
4. 不要勾选"Initialize with a README"，点击"Create repository"。

---

## 2. 本地初始化 Git 仓库

1. **安装 Git**  
   下载并安装 [Git for Windows](https://git-scm.com/download/win)。

2. **打开命令行**  
   在 `D:\01-PHRL_system` 目录下，右键选择"Git Bash Here"或用 PowerShell/cmd 进入该目录。

3. **初始化仓库**
   ```bash
   git init
   ```

4. **添加 .gitignore 文件**  
   在项目根目录新建 `.gitignore` 文件，内容如下（可根据实际情况调整）：
   ```
   # Python
   .venv/
   __pycache__/
   *.pyc

   # Node.js
   node_modules/

   # IDE/Editor
   .vscode/
   .idea/

   # OS
   .DS_Store
   Thumbs.db
   ```

---

## 3. 提交本地代码

1. **添加所有文件**
   ```bash
   git add .
   ```

2. **提交代码**
   ```bash
   git commit -m "初始化项目，上传全部代码"
   ```

---

## 4. 关联远程仓库

1. **复制 GitHub 仓库地址**  
   进入你刚刚创建的 GitHub 仓库页面，点击"Code"按钮，复制 `https://github.com/你的用户名/仓库名.git`。

2. **添加远程仓库**
   ```bash
   git remote add origin https://github.com/你的用户名/仓库名.git
   ```

---

## 5. 推送到 GitHub

1. **推送主分支代码**
   ```bash
   git branch -M main
   git push -u origin main
   ```
   > 第一次推送需要输入 GitHub 账号和密码（或 token）。

---

## 6. 后续开发与同步

- **本地有新改动时：**
  ```bash
  git add .
  git commit -m "你的修改说明"
  git push
  ```

- **在单位/家里切换开发时：**
  ```bash
  git pull
  ```

---

## 7. 常见问题

- **推送报错：refusing to merge unrelated histories**
  ```bash
  git pull origin main --allow-unrelated-histories
  # 然后再 git push
  ```

- **token 登录（2021年后 GitHub 不支持密码推送）**
  - 进入 GitHub → Settings → Developer settings → Personal access tokens → 生成新 token，推送时用 token 作为密码。

---

## 8. 在 GitHub 官网管理文件的常用操作

### 1. 上传新文件/文件夹

1. 进入你的仓库主页（https://github.com/）。
2. 点击页面上方的 `Add file` 按钮，选择 `Upload files`。
3. 拖拽文件到上传区域，或点击 `choose your files` 选择本地文件。
4. 可以一次上传多个文件，但**不能直接上传整个文件夹**（需先压缩为 zip 或用 Git 客户端上传文件夹）。
5. 填写下方的 `Commit changes` 说明，点击绿色按钮完成上传。

### 2. 在线新建/编辑文件

- **新建文件**：
  - 点击 `Add file` → `Create new file`。
  - 输入文件名和内容，填写 `Commit changes` 说明，点击提交。
- **在线编辑文件**：
  - 在文件列表中点击要编辑的文件。
  - 点击右上角的铅笔图标（Edit this file）。
  - 修改内容后，填写 `Commit changes` 说明，点击提交。

### 3. 删除文件

1. 找到要删除的文件，点击进入。
2. 点击右上角的垃圾桶图标（Delete this file）。
3. 填写 `Commit changes` 说明，点击提交。

### 4. 下载单个文件或整个仓库

- **下载单个文件**：点击文件，右上角点击 `Raw`，右键另存为即可。
- **下载整个仓库**：在仓库主页，点击绿色 `Code` 按钮，选择 `Download ZIP`。

### 5. 查看历史和回滚

- 点击任意文件，选择 `History`，可以查看该文件的所有历史版本。
- 需要回滚时，可以点击某个历史版本，选择 `Revert` 或手动复制内容恢复。

### 6. 分支与 Pull Request

- 可以在网页上新建分支、切换分支、发起 Pull Request（合并请求），适合多人协作和代码审核。

### 7. 注意事项

- **大文件/大批量操作**建议用 Git 客户端（命令行或 GitHub Desktop）操作，网页端适合小文件和简单修改。
- **文件夹上传**只能通过 Git 客户端或 GitHub Desktop，网页端不支持直接上传整个文件夹。

---

## 总结

1. 注册 GitHub 并新建仓库
2. 本地 `git init`，写好 `.gitignore`
3. `git add .` → `git commit -m "注释"`
4. `git remote add origin ...`
5. `git push -u origin main`

这样你就能在家和单位无缝同步开发，永远不会丢失代码！