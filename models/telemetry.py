from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Numeric,
    DateTime,
    Index,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.base_model import BaseModel


class DeviceTelemetry(BaseModel):
    """
    设备遥测数据(时序表)。
    每条 = 某设备在某时刻上报的一个测点值,例如 1 号设备 10:00:05 温度 36.5。
    工业数据采集平台的核心表,数据量天然庞大,是练索引的最佳对象。
    """
    # __tablename__ 指定表名;BaseModel 已提供 id / created_at / updated_at / 软删除字段
    __tablename__ = "device_telemetry"

    __table_args__ = (
        Index("idx_device_telemetry_device_id_metric_recorded_at", "device_id", "metric", "recorded_at"),
    )

    # 设备 id(以后会做成外键指向设备表,先用普通整数)
    device_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="设备ID",
    )

    # 测点名:temperature / pressure / voltage ...
    metric: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="测点名称",
    )

    # 采集到的数值
    value: Mapped[float] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        comment="测点数值",
    )

    # 数据真正产生的时间(注意:和 created_at "入库时间" 不是一回事)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="采集时间",
    )

    # ============================================================
    # 👉 你来写:用 __table_args__ 给这张表加索引
    #
    # 业务上最高频的查询是:
    #   "查某台设备某个测点在某时间段的数据"
    #   WHERE device_id = ? AND metric = ? AND recorded_at BETWEEN ? AND ?
    #   ORDER BY recorded_at
    #
    # 任务:用 SQLAlchemy 的 Index() 建一个组合索引来支撑它。
    # 提示:
    #   1. 顶部需要 from sqlalchemy import Index
    #   2. 在类里加一行:
    #        __table_args__ = ( Index("索引名", "列1", "列2", ...), )
    #   3. 想想列顺序:等值条件(device_id, metric)在前,范围/排序列(recorded_at)在后
    #
    # 写完看 docs/面试题库.md 或问我核对。
    # ============================================================

    def __repr__(self):
        return (
            f"DeviceTelemetry(id={self.id}, device_id={self.device_id}, "
            f"metric={self.metric!r}, value={self.value}, recorded_at={self.recorded_at})"
        )
