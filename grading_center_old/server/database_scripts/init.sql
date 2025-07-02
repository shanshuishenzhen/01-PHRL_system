-- --------------------------------------------------------
-- 主机:                         127.0.0.1
-- 服务器版本:                   8.0.26 - MySQL Community Server - GPL
-- 服务器操作系统:               Win64
-- --------------------------------------------------------

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `marking_center_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `marking_center_db`;

-- --------------------------------------------------------
-- 表的结构 `exams` (考试信息表)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `exams` (
  `id` int NOT NULL AUTO_INCREMENT,
  `examName` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '考试名称',
  `examCode` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '考试代码',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '考试描述',
  `startTime` datetime NOT NULL COMMENT '考试开始时间',
  `endTime` datetime NOT NULL COMMENT '考试结束时间',
  `duration` int NOT NULL COMMENT '考试时长（分钟）',
  `status` enum('draft','published','ongoing','completed','archived') COLLATE utf8mb4_unicode_ci DEFAULT 'draft' COMMENT '考试状态',
  `totalScore` decimal(5,2) NOT NULL DEFAULT '100.00' COMMENT '考试总分',
  `passScore` decimal(5,2) NOT NULL DEFAULT '60.00' COMMENT '及格分数',
  `maxAttempts` int NOT NULL DEFAULT '1' COMMENT '最大考试次数',
  `allowReview` tinyint(1) DEFAULT '1' COMMENT '是否允许查看答案',
  `shuffleQuestions` tinyint(1) DEFAULT '0' COMMENT '是否随机排列题目',
  `shuffleOptions` tinyint(1) DEFAULT '0' COMMENT '是否随机排列选项',
  `createdBy` int NOT NULL COMMENT '创建者ID',
  `updatedBy` int DEFAULT NULL COMMENT '更新者ID',
  `createdAt` datetime NOT NULL,
  `updatedAt` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `examCode` (`examCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试信息表';

-- --------------------------------------------------------
-- 表的结构 `exam_participants` (考试参与者表)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `exam_participants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `examId` int NOT NULL COMMENT '考试ID',
  `userId` int NOT NULL COMMENT '用户ID',
  `status` enum('invited','confirmed','completed','absent') COLLATE utf8mb4_unicode_ci DEFAULT 'invited' COMMENT '参与状态',
  `startTime` datetime DEFAULT NULL COMMENT '开始考试时间',
  `endTime` datetime DEFAULT NULL COMMENT '结束考试时间',
  `score` decimal(5,2) DEFAULT NULL COMMENT '考试得分',
  `attemptCount` int DEFAULT '0' COMMENT '考试次数',
  `isPassed` tinyint(1) DEFAULT NULL COMMENT '是否通过',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `createdAt` datetime NOT NULL,
  `updatedAt` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `examId` (`examId`),
  KEY `userId` (`userId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试参与者表';

-- --------------------------------------------------------
-- 表的结构 `exam_questions` (考试题目表)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `exam_questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `examId` int NOT NULL COMMENT '考试ID',
  `questionType` enum('single','multiple','true_false','fill_blank','essay') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '题目类型',
  `questionContent` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '题目内容',
  `options` json DEFAULT NULL COMMENT '选项（JSON格式）',
  `correctAnswer` text COLLATE utf8mb4_unicode_ci COMMENT '正确答案',
  `score` decimal(5,2) NOT NULL DEFAULT '1.00' COMMENT '题目分值',
  `difficulty` enum('easy','medium','hard') COLLATE utf8mb4_unicode_ci DEFAULT 'medium' COMMENT '题目难度',
  `orderNum` int NOT NULL DEFAULT '1' COMMENT '题目顺序',
  `isRequired` tinyint(1) DEFAULT '1' COMMENT '是否必答题',
  `explanation` text COLLATE utf8mb4_unicode_ci COMMENT '题目解析',
  `createdBy` int NOT NULL COMMENT '创建者ID',
  `createdAt` datetime NOT NULL,
  `updatedAt` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `examId` (`examId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试题目表';

-- --------------------------------------------------------
-- 表的结构 `users` (用户表)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('student','marker','admin') NOT NULL DEFAULT 'student',
  `createdAt` datetime NOT NULL,
  `updatedAt` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- --------------------------------------------------------
-- 表的结构 `subjective_answers` (主观题答案表)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `subjective_answers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `participantId` int NOT NULL COMMENT '参与者ID',
  `questionId` int NOT NULL COMMENT '题目ID',
  `answerText` text COLLATE utf8mb4_unicode_ci,
  `score` decimal(5,2) DEFAULT NULL,
  `markerId` int DEFAULT NULL COMMENT '评阅人ID',
  `markedAt` datetime DEFAULT NULL,
  `status` enum('pending','marked','disputed') DEFAULT 'pending',
  `createdAt` datetime NOT NULL,
  `updatedAt` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `participantId` (`participantId`),
  KEY `questionId` (`questionId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='主观题答案及评分表';

-- 插入默认管理员用户
INSERT INTO `users` (`username`, `password`, `role`, `createdAt`, `updatedAt`) VALUES ('admin', '$2b$10$f.UPZJ/4cT9rZ..E1ydYx.2zXm9.5dO8aE/M3o5.b.3p4zS6X.93a', 'admin', NOW(), NOW()) ON DUPLICATE KEY UPDATE username='admin';
-- 密码是 '123456' (使用 bcrypt 加密) 