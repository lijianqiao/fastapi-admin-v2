"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: password_policy.py
@DateTime: 2025/08/27 11:45:06
@Docs: 密码策略校验工具。
"""

import re


def validate_password(
    password: str,
    *,
    min_length: int,
    require_uppercase: bool,
    require_lowercase: bool,
    require_digits: bool,
    require_special: bool,
) -> bool:
    """
    校验密码是否符合策略

    Args:
        password (str): 密码
        min_length (int): 最小长度
        require_uppercase (bool): 是否要求大写字母
        require_lowercase (bool): 是否要求小写字母
        require_digits (bool): 是否要求数字
        require_special (bool): 是否要求特殊字符

    Returns:
        bool: 是否符合策略
    """
    if len(password) < min_length:
        return False
    if require_uppercase and not re.search(r"[A-Z]", password):
        return False
    if require_lowercase and not re.search(r"[a-z]", password):
        return False
    if require_digits and not re.search(r"\d", password):
        return False
    if require_special and not re.search(r"[^A-Za-z0-9]", password):
        return False
    return True


__all__ = ["validate_password"]
