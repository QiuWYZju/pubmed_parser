import calendar
import collections
try:
    from collections.abc import Iterable
except:
    from collections import Iterable
from time import strptime
from six import string_types
from lxml import etree
from itertools import chain


def remove_namespace(tree):
    """
    Strip namespace from parsed XML
    """
    for node in tree.iter():
        try:
            has_namespace = node.tag.startswith("{")
        except AttributeError:
            continue  # node.tag is not a string (node is a comment or similar)
        if has_namespace:
            node.tag = node.tag.split("}", 1)[1]


def read_xml(path, nxml=False):
    """
    Parse tree from given XML path
    """
    try:
        tree = etree.parse(path)
        if ".nxml" in path or nxml:
            remove_namespace(tree)  # strip namespace when reading an XML file
    except:
        try:
            tree = etree.fromstring(path)
        except Exception:
            print(
                "Error: it was not able to read a path, a file-like object, or a string as an XML"
            )
            raise
    return tree


# def stringify_children(node):
#     """
#     Filters and removes possible Nones in texts and tails
#     ref: http://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml
#     """
#     parts = (
#         [node.text]
#         + list(chain(*([c.text, c.tail] for c in node.getchildren())))
#         + [node.tail]
#     )
#     return "".join(filter(None, parts))
# def stringify_children(node, preserve_format=True):
#     """
#     Joins all string parts excluding empty parts.
    
#     Parameters
#     ----------
#     node : lxml node
#     preserve_format : bool
#         If True, preserve basic format tags like <italic>, <bold>, <sup>
    
#     Returns
#     -------
#     str : stringified node content
#     """
#     if not preserve_format:
#         parts = (
#             [node.text]
#             + list(chain(*([c.text, c.tail] for c in node.getchildren())))
#             + [node.tail]
#         )
#         return "".join(filter(None, parts))
    
#     # 新行为：保留基本格式标记
#     parts = []
    
#     # 处理当前节点的文本
#     if node.text:
#         parts.append(node.text.strip())
    
#     # 递归处理所有子节点
#     for child in node:
#         child_str = stringify_children(child, preserve_format=True)
        
#         # 为特定标签添加格式标记
#         # if child.tag == 'italic':
#         #     parts.append(f'<i>{child_str}</i>')
#         # elif child.tag == 'bold':
#         #     parts.append(f'<b>{child_str}</b>')
#         # if child.tag == 'sup':
#         #     parts.append(f'<sup>{child_str}</sup>')
#         # elif child.tag == 'sub':
#         #     parts.append(f'<sub>{child_str}</sub>')
#         # 根据标签类型包装文本
#         if child.tag == 'sup':
#             parts.append(f'$^{{{child_str}}}$')  # LaTeX 上标格式
#         elif child.tag == 'sub':
#             parts.append(f'$_{{{child_str}}}$')  # LaTeX 下标格式
#         else:
#             parts.append(child_str)  # 其他标签直接使用

        
#         # 处理尾随文本
#         if child.tail:
#             parts.append(child.tail.strip())
    
#     return "".join(filter(None, parts))
# 或者更简洁的版本，专注于处理 sup 和 sub 标签
def stringify_children(node, preserve_format=True):
    """
    Joins all string parts excluding empty parts.
    
    Parameters
    ----------
    node : lxml node
    preserve_format : bool
        If True, preserve basic format tags like <italic>, <bold>, <sup>, <sub>
    
    Returns
    -------
    str : stringified node content
    """
    if not preserve_format:
        parts = (
            [node.text]
            + list(chain(*([c.text, c.tail] for c in node.getchildren())))
            + [node.tail]
        )
        return "".join(filter(None, parts))
    
    parts = []
    
    # 添加当前节点的文本
    if node.text:
        parts.append(node.text)
    
    # 处理所有子节点
    for child in node.getchildren():
        # 递归处理子节点
        child_str = stringify_children(child, preserve_format)
        
        # 根据标签类型处理
        if child.tag == 'sup':
            parts.append(f'$^{{{child_str}}}$')
        elif child.tag == 'sub':
            parts.append(f'$_{{{child_str}}}$')
        else:
            # 对于其他标签，直接使用其内容
            parts.append(child_str)
        
        # 添加子节点的尾部文本
        if child.tail:
            parts.append(child.tail)
    
    result = "".join(filter(None, parts))
    return result
def stringify_affiliation(node):
    """
    Filters and removes possible Nones in texts and tails
    ref: http://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml
    """
    parts = (
        [node.text]
        + list(
            chain(
                *(
                    [c.text if (c.tag != "label" and c.tag != "sup") else "", c.tail]
                    for c in node.getchildren()
                )
            )
        )
        + [node.tail]
    )
    return " ".join(filter(None, parts))


def stringify_affiliation_rec(node):
    """
    Flatten and join list to string
    ref: http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
    """
    parts = _recur_children(node)
    parts_flatten = list(_flatten(parts))
    return " ".join(parts_flatten).strip()


def _flatten(l):
    """
    Flatten list into one dimensional
    """
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, string_types):
            for sub in _flatten(el):
                yield sub
        else:
            yield el


def _recur_children(node):
    """
    Recursive through node to when it has multiple children
    """
    if len(node.getchildren()) == 0:
        parts = (
            ([node.text or ""] + [node.tail or ""])
            if (node.tag != "label" and node.tag != "sup")
            else ([node.tail or ""])
        )
        return parts
    else:
        parts = (
            [node.text or ""]
            + [_recur_children(c) for c in node.getchildren()]
            + [node.tail or ""]
        )
        return parts


def month_or_day_formater(month_or_day):
    """
    Parameters
    ----------
    month_or_day: str or int
        must be one of the following:
            (i)  month: a three letter month abbreviation, e.g., 'Jan'.
            (ii) day: an integer.

    Returns
    -------
    numeric: str
        a month of the form 'MM' or a day of the form 'DD'.
        Note: returns None if:
            (a) the input could not be mapped to a known month abbreviation OR
            (b) the input was not an integer (i.e., a day).
    """
    if month_or_day.replace(".", "") in filter(None, calendar.month_abbr):
        to_format = strptime(month_or_day.replace(".", ""), "%b").tm_mon
    elif month_or_day.strip().isdigit() and "." not in str(month_or_day):
        to_format = int(month_or_day.strip())
    else:
        return None

    return ("0" if to_format < 10 else "") + str(to_format)


def pretty_print(node):
    """
    Pretty print a given lxml node
    """
    print(etree.tostring(node, pretty_print=True).decode("utf-8"))
