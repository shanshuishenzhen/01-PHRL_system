# 项目开发文档

## 目录结构说明

- src/core：全局总控（主控台）模块
- src/user_management：用户管理模块
- src/exam_management：考试管理模块
- src/question_bank：题库管理模块
- src/grading_center：阅卷中心模块
- src/score_statistics：成绩统计模块
- src/client：客户机模块
- shared/components：公共UI组件
- shared/utils：工具函数
- shared/models：数据模型
- shared/config：配置文件
- docs：开发文档
- tests：测试用例
- main.py：主入口文件

## 开发规范
- 代码风格统一，建议遵循PEP8
- 各模块间通过接口或API通信，避免直接依赖
- 公共组件、工具、模型统一放在shared目录
- 每个模块需有README说明
- 重要接口需有文档说明

## 其他说明
- 如需新增模块，请先在docs中补充说明
- 详细接口文档建议放在各自模块的README或单独md文件中 