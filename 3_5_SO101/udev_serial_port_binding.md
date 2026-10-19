---
title: "USB 串口设备固定命名教程（udev 规则）"
lang: zh-CN
format:
  pdf:
    toc: true
    number-sections: false
    pdf-engine: xelatex
    documentclass: ctexart
    geometry:
      - margin=1in
    colorlinks: true
    keep-tex: true
    tbl-colwidths: false
execute:
  enabled: false
---

# 背景

USB 串口设备（如 CH340）每次插入时，系统分配的设备名（`/dev/ttyACM0`、`/dev/ttyACM1`...）取决于插入顺序和 USB 端口，不固定。通过 udev 规则可以根据设备的唯一标识（序列号等）创建固定的符号链接，例如 `/dev/ttyLeader` 和 `/dev/ttyFollower`。



# 第一步：查询设备属性

插入设备后，先确认设备名：

```bash
ls /dev/ttyACM*
```

然后用 `udevadm` 查询该设备的详细属性：

```bash
udevadm info -a -n /dev/ttyACM0
```

输出内容很长，我们重点关注 **USB 父设备层级**中的以下字段：

| 字段 | 说明 | 示例值 |
|------|------|--------|
| `ATTRS{idVendor}` | 厂商 ID | `1a86`（南京沁恒 / CH340） |
| `ATTRS{idProduct}` | 产品 ID | `55d3` |
| `ATTRS{serial}` | 设备序列号（唯一标识） | `5B14114326` |
| `ATTRS{product}` | 产品名称 | `USB Single Serial` |

> **关键**：`idVendor` + `idProduct` 标识设备型号，`serial` 标识具体某一个设备。如果有多个同型号设备，必须用 `serial` 区分。

## 示例输出（节选）

```
looking at parent device '/devices/pci0000:00/0000:00:14.0/usb1/1-9':
    ATTRS{idProduct}=="55d3"
    ATTRS{idVendor}=="1a86"
    ATTRS{serial}=="5B14114326"
    ATTRS{product}=="USB Single Serial"
```

对每个需要命名的设备都执行一次查询，记录下各自的 `serial`。



# 第二步：编写 udev 规则

## 规则文件位置

udev 规则文件存放在 `/etc/udev/rules.d/` 目录下，文件名格式为 `数字-名称.rules`，数字越大优先级越高。

## 规则语法

一条规则的基本格式：

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="厂商ID", ATTRS{idProduct}=="产品ID", ATTRS{serial}=="序列号", SYMLINK+="自定义名称", MODE="0666"
```

各部分说明：

| 部分 | 作用 |
|------|------|
| `SUBSYSTEM=="tty"` | 匹配 tty 子系统的设备 |
| `ATTRS{idVendor}=="1a86"` | 匹配厂商 ID |
| `ATTRS{idProduct}=="55d3"` | 匹配产品 ID |
| `ATTRS{serial}=="..."` | 匹配设备序列号（确保唯一性） |
| `SYMLINK+="ttyLeader"` | 创建 `/dev/ttyLeader` 符号链接 |
| `MODE="0666"` | 设置权限为所有用户可读写 |

## 我们的规则

创建文件 `/etc/udev/rules.d/99-fixed-serial-ports.rules`，写入以下内容：

```bash
sudo bash -c 'cat > /etc/udev/rules.d/99-fixed-serial-ports.rules << "EOF"
# Leader 机械臂 (序列号: 5B14114326)
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", ATTRS{serial}=="5B14114326", SYMLINK+="ttyLeader", MODE="0666"

# Follower 机械臂 (序列号: 5B14030919)
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", ATTRS{serial}=="5B14030919", SYMLINK+="ttyFollower", MODE="0666"
EOF'
```



# 第三步：使规则生效

## 方法一：重载规则并触发（无需重启）

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## 方法二：重新插拔设备

拔掉 USB 设备再插入，udev 会自动应用新规则。



# 第四步：验证

```bash
# 检查符号链接是否存在
ls -l /dev/ttyLeader /dev/ttyFollower
```

预期输出类似：

```
lrwxrwxrwx 1 root root 7 Mar 31 12:00 /dev/ttyLeader -> ttyACM0
lrwxrwxrwx 1 root root 7 Mar 31 12:00 /dev/ttyFollower -> ttyACM1
```

> 注意：`-> ttyACMx` 后面的数字可能会变，但 `/dev/ttyLeader` 和 `/dev/ttyFollower` 始终指向正确的物理设备。

在代码中直接使用固定名称即可：

```python
leader_port = "/dev/ttyLeader"
follower_port = "/dev/ttyFollower"
```



# 附：常用排查命令

```bash
# 查看所有已加载的规则
udevadm info -q all -n /dev/ttyACM0

# 测试规则是否匹配（不实际执行）
udevadm test $(udevadm info -q path -n /dev/ttyACM0)

# 实时监控 udev 事件（插拔设备时观察）
udevadm monitor
```



# 我们的设备信息汇总（这个每个人不一样）

| 角色 | 序列号 | 固定设备名 |
|------|--------|------------|
| Leader 臂 | `5B14114326` | `/dev/ttyLeader` |
| Follower 臂 | `5B14030919` | `/dev/ttyFollower` |
