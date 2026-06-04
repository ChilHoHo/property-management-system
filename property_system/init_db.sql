-- ============================================================
-- 小区物业管理系统 - 数据库高级功能 SQL 脚本
-- 数据库: MySQL 8.0 / property_db
-- 包含: 2个视图 + 3个触发器 + 2个存储过程
-- 使用方法: 在 Navicat 中切换到 property_db 后执行此脚本
-- ============================================================

USE property_db;


-- ============================================================
-- 一、视图 (Views)
-- ============================================================

-- ------------------------------------------------------------
-- 视图1: view_owe_fee - 业主欠费视图
-- 功能: 展示所有未缴物业费，关联业主姓名和房屋地址
-- ------------------------------------------------------------
DROP VIEW IF EXISTS view_owe_fee;
CREATE VIEW view_owe_fee AS
SELECT
    u.name          AS owner_name,
    CONCAT(h.building, '栋', h.unit, '单元', h.room, '室') AS house_addr,
    f.amount        AS amount,
    f.month         AS month
FROM fee f
JOIN house h ON f.house_id = h.id
JOIN `owner` o ON h.owner_id = o.id
JOIN `user` u ON o.user_id = u.id
WHERE f.status = 0
ORDER BY f.month ASC;


-- ------------------------------------------------------------
-- 视图2: view_repair_progress - 报修进度视图
-- 功能: 展示所有报修工单的进度，关联业主姓名和处理员工姓名
-- ------------------------------------------------------------
DROP VIEW IF EXISTS view_repair_progress;
CREATE VIEW view_repair_progress AS
SELECT
    u1.name             AS owner_name,
    r.content           AS content,
    CASE r.status
        WHEN 0 THEN '待处理'
        WHEN 1 THEN '处理中'
        WHEN 2 THEN '已完成'
    END                 AS status,
    COALESCE(u2.name, '未分配') AS staff_name
FROM repair r
JOIN `owner` o ON r.owner_id = o.id
JOIN `user` u1 ON o.user_id = u1.id
LEFT JOIN `user` u2 ON r.staff_id = u2.id
ORDER BY r.status ASC, r.submit_time DESC;


-- ============================================================
-- 二、触发器 (Triggers)
-- ============================================================

-- ------------------------------------------------------------
-- 触发器1: trg_fee_amount_check
-- 功能: 物业费金额不能为负数，插入或更新前校验
-- ------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_fee_amount_check_insert;
DELIMITER $$
CREATE TRIGGER trg_fee_amount_check_insert
BEFORE INSERT ON fee
FOR EACH ROW
BEGIN
    IF NEW.amount < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '物业费金额不能为负数';
    END IF;
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_fee_amount_check_update;
DELIMITER $$
CREATE TRIGGER trg_fee_amount_check_update
BEFORE UPDATE ON fee
FOR EACH ROW
BEGIN
    IF NEW.amount < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '物业费金额不能为负数';
    END IF;
END$$
DELIMITER ;


-- ------------------------------------------------------------
-- 触发器2: trg_repair_complete
-- 功能: 报修状态改为2(已完成)时，自动填充处理时间
-- ------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_repair_complete;
DELIMITER $$
CREATE TRIGGER trg_repair_complete
BEFORE UPDATE ON repair
FOR EACH ROW
BEGIN
    IF NEW.status = 2 AND OLD.status != 2 THEN
        SET NEW.process_time = NOW();
    END IF;
END$$
DELIMITER ;


-- ------------------------------------------------------------
-- 触发器3: trg_repair_house_owner
-- 功能: 业主提交报修时，校验报修房屋是否属于该业主
-- ------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_repair_house_owner;
DELIMITER $$
CREATE TRIGGER trg_repair_house_owner
BEFORE INSERT ON repair
FOR EACH ROW
BEGIN
    DECLARE house_owner_id INT;

    SELECT owner_id INTO house_owner_id
    FROM house
    WHERE id = NEW.house_id;

    IF house_owner_id IS NULL OR house_owner_id != NEW.owner_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '该房屋不属于您，无法提交报修';
    END IF;
END$$
DELIMITER ;


-- ============================================================
-- 三、存储过程 (Stored Procedures)
-- ============================================================

-- ------------------------------------------------------------
-- 存储过程1: fee_stat(IN month VARCHAR(7))
-- 功能: 输入月份，统计总费用、已缴、未缴、收缴率
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS fee_stat;
DELIMITER $$
CREATE PROCEDURE fee_stat(IN p_month VARCHAR(7))
BEGIN
    DECLARE total_amount     DECIMAL(12,2) DEFAULT 0;
    DECLARE paid_amount      DECIMAL(12,2) DEFAULT 0;
    DECLARE unpaid_amount    DECIMAL(12,2) DEFAULT 0;
    DECLARE collection_rate  DECIMAL(5,1)  DEFAULT 0;

    -- 总金额
    SELECT IFNULL(SUM(amount), 0) INTO total_amount
    FROM fee WHERE month = p_month;

    -- 已缴金额
    SELECT IFNULL(SUM(amount), 0) INTO paid_amount
    FROM fee WHERE month = p_month AND status = 1;

    -- 未缴金额
    SELECT IFNULL(SUM(amount), 0) INTO unpaid_amount
    FROM fee WHERE month = p_month AND status = 0;

    -- 收缴率
    IF total_amount > 0 THEN
        SET collection_rate = (paid_amount / total_amount) * 100;
    END IF;

    -- 返回结果
    SELECT
        p_month          AS stat_month,
        total_amount     AS total_amount,
        paid_amount      AS paid_amount,
        unpaid_amount    AS unpaid_amount,
        collection_rate  AS collection_rate;
END$$
DELIMITER ;


-- ------------------------------------------------------------
-- 存储过程2: repair_stat(IN p_start DATE, IN p_end DATE)
-- 功能: 输入时间范围，统计各状态报修数量
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS repair_stat;
DELIMITER $$
CREATE PROCEDURE repair_stat(IN p_start DATE, IN p_end DATE)
BEGIN
    SELECT
        CASE status
            WHEN 0 THEN '待处理'
            WHEN 1 THEN '处理中'
            WHEN 2 THEN '已完成'
        END   AS status_name,
        COUNT(*) AS count
    FROM repair
    WHERE submit_time BETWEEN p_start AND DATE_ADD(p_end, INTERVAL 1 DAY)
    GROUP BY status
    ORDER BY status ASC;
END$$
DELIMITER ;
