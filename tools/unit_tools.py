"""单位换算工具（长度 / 速度）"""

# 单位 -> (类型, 折算到基准单位的系数)；长度基准是米，速度基准是米每秒
_UNITS = {
    "毫米": ("length", 0.001), "mm": ("length", 0.001),
    "厘米": ("length", 0.01), "cm": ("length", 0.01),
    "米": ("length", 1.0), "m": ("length", 1.0),
    "千米": ("length", 1000.0), "公里": ("length", 1000.0), "km": ("length", 1000.0),
    "米每秒": ("speed", 1.0), "m/s": ("speed", 1.0),
    "千米每小时": ("speed", 1 / 3.6), "km/h": ("speed", 1 / 3.6),
}


def convert_unit(value, from_unit, to_unit):
    """单位换算：结果 = 数值 × 源单位系数 ÷ 目标单位系数"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return f"数值无效：{value}"

    f, t = from_unit.strip(), to_unit.strip()
    if f not in _UNITS or t not in _UNITS:
        return (f"不支持的单位（{from_unit} → {to_unit}）。"
                "支持：长度 毫米/厘米/米/千米（mm/cm/m/km）；速度 米每秒/千米每小时（m/s、km/h）")
    if _UNITS[f][0] != _UNITS[t][0]:
        return f"单位类型不同，无法换算：{from_unit} 是{_UNITS[f][0]}，{to_unit} 是{_UNITS[t][0]}"

    out = value * _UNITS[f][1] / _UNITS[t][1]
    return f"{value} {from_unit} = {out:g} {to_unit}"
