# 调试日志：客户端UI问题 - 单选题和判断题交互异常

**日期:** 2024-07-30

**模块:** `client/client_app.py`

**目标:** 解决客户端应用程序中单选题和判断题的UI交互问题。

## 问题描述

目前客户端应用程序存在两个UI交互问题：

1. **单选题问题**：鼠标滑过选项时会自动选中该选项
2. **判断题问题**：初始状态下所有选项都被选中

## 已尝试的解决方案

### 方案一：修改 `StringVar` 初始化方式

尝试将单选题和判断题的 `tk.StringVar()` 初始化方式修改为 `tk.StringVar(value="")`，以确保初始状态为未选中。

```python
# 修改前
self.answers[q_id] = tk.StringVar()

# 修改后
self.answers[q_id] = tk.StringVar(value="")
```

### 方案二：添加 `command` 回调函数

尝试为 `Radiobutton` 添加 `command` 回调函数，以控制选项的选中行为：

```python
# 添加 command 回调
rb = tk.Radiobutton(
    option_frame,
    text=opt_text,
    variable=self.answers[q_id],
    value=opt,
    takefocus=False,
    indicatoron=1,
    command=lambda o=opt: self.update_single_choice(q_id, o)
)
```

### 方案三：移除 `command` 回调函数

尝试移除 `Radiobutton` 的 `command` 参数，以解决鼠标滑过即选中的问题：

```python
# 移除 command 回调
rb = tk.Radiobutton(
    option_frame,
    text=opt_text,
    variable=self.answers[q_id],
    value=opt,
    takefocus=False,
    indicatoron=1
)
```

## 当前状态

尝试了多种修改方法后，问题仍未解决。由于客户端应用程序的日志中没有显示UI交互信息，无法通过日志确认修改是否有效。

## 下一步建议

1. 考虑使用更直接的方式测试UI交互，例如添加专门的调试代码来记录UI事件
2. 检查 Tkinter 的事件绑定机制，可能需要调整 `Radiobutton` 的其他属性或事件处理方式
3. 考虑使用 `bind` 方法显式控制鼠标事件的处理
4. 检查是否有其他代码（如全局事件处理）可能干扰了 `Radiobutton` 的正常行为

**搁置原因:**
根据用户指示，暂停此问题的调试，待以后解决。