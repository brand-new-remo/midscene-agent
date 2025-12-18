"""
模板注册表

负责模板的扫描、注册、检索和管理。支持模板分类、版本控制、
依赖解析等功能。
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml

from .exceptions import (
    InvalidTemplateFormatError,
    RegistryError,
    RegistryLoadError,
    TemplateAlreadyExistsError,
    TemplateNotFoundError,
    TemplateValidationError,
)
from .types import Template, TemplateCall


class TemplateRegistry:
    """模板注册表

    负责管理模板的注册、检索和分类。支持：
    - 自动扫描模板文件
    - 模板分类和标签
    - 版本管理
    - 依赖解析
    - 模板缓存
    """

    def __init__(self, templates_dir: str):
        """初始化模板注册表

        Args:
            templates_dir: 模板目录路径
        """
        self.templates_dir = Path(templates_dir)
        self.registry_file = self.templates_dir / "registry.yaml"

        # 模板存储
        self._templates: Dict[str, Template] = {}
        self._template_metadata: Dict[str, Dict] = {}

        # 分类和标签索引
        self._categories: Dict[str, Set[str]] = {}
        self._tags: Dict[str, Set[str]] = {}

        # 缓存
        self._cache: Dict[str, Template] = {}

        # 加载注册表
        self._load_registry()

    def _load_registry(self):
        """加载模板注册表"""
        if not self.registry_file.exists():
            # 如果注册表不存在，创建空的
            self._save_registry()
            return

        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                registry_data = yaml.safe_load(f) or {}

            templates_metadata = registry_data.get("templates", {})

            for template_name, metadata in templates_metadata.items():
                try:
                    # 加载模板文件
                    template = self._load_template_from_file(metadata["path"])
                    self._templates[template_name] = template
                    self._template_metadata[template_name] = metadata

                    # 更新分类索引
                    category = metadata.get("category", "general")
                    if category not in self._categories:
                        self._categories[category] = set()
                    self._categories[category].add(template_name)

                    # 更新标签索引
                    tags = metadata.get("tags", [])
                    for tag in tags:
                        if tag not in self._tags:
                            self._tags[tag] = set()
                        self._tags[tag].add(template_name)

                except Exception as e:
                    print(f"Warning: Failed to load template '{template_name}': {e}")

        except Exception as e:
            raise RegistryLoadError(str(self.registry_file), str(e))

    def _save_registry(self):
        """保存模板注册表"""
        registry_data = {
            "templates": {
                name: metadata for name, metadata in self._template_metadata.items()
            }
        }

        with open(self.registry_file, "w", encoding="utf-8") as f:
            yaml.dump(registry_data, f, default_flow_style=False, allow_unicode=True)

    def _load_template_from_file(self, relative_path: str) -> Template:
        """从文件加载模板

        Args:
            relative_path: 相对于模板目录的相对路径

        Returns:
            加载的模板对象

        Raises:
            InvalidTemplateFormatError: 模板格式无效
        """
        template_path = self.templates_dir / relative_path

        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_data = yaml.safe_load(f)

            if not template_data or "template" not in template_data:
                raise InvalidTemplateFormatError(
                    str(template_path), "Missing 'template' key in template file"
                )

            template = Template.from_dict(template_data)
            return template

        except yaml.YAMLError as e:
            raise InvalidTemplateFormatError(
                str(template_path), f"Invalid YAML format: {e}"
            )
        except Exception as e:
            raise InvalidTemplateFormatError(str(template_path), str(e))

    def register_template(
        self, template: Template, metadata: Optional[Dict] = None
    ) -> str:
        """注册模板

        Args:
            template: 模板对象
            metadata: 可选的元数据，会覆盖模板中的默认元数据

        Returns:
            注册的模板名称

        Raises:
            TemplateAlreadyExistsError: 模板已存在
        """
        template_name = metadata.get("name") if metadata else None
        if not template_name:
            template_name = template.name

        if template_name in self._templates:
            raise TemplateAlreadyExistsError(template_name)

        # 准备元数据
        template_metadata = {
            "name": template_name,
            "category": template.category,
            "tags": template.tags,
            "author": template.author,
            "version": template.version,
            "description": template.description,
            "path": f"custom/{template_name}.yaml",  # 默认路径
            "popularity": 0,
        }

        if metadata:
            template_metadata.update(metadata)

        # 注册模板
        self._templates[template_name] = template
        self._template_metadata[template_name] = template_metadata

        # 更新索引
        category = template_metadata["category"]
        if category not in self._categories:
            self._categories[category] = set()
        self._categories[category].add(template_name)

        for tag in template_metadata["tags"]:
            if tag not in self._tags:
                self._tags[tag] = set()
            self._tags[tag].add(template_name)

        # 保存注册表
        self._save_registry()

        return template_name

    def unregister_template(self, template_name: str) -> bool:
        """注销模板

        Args:
            template_name: 模板名称

        Returns:
            是否成功注销
        """
        if template_name not in self._templates:
            return False

        # 从存储中删除
        template = self._templates.pop(template_name)
        metadata = self._template_metadata.pop(template_name)

        # 从分类索引中删除
        category = metadata.get("category", "general")
        if category in self._categories:
            self._categories[category].discard(template_name)
            if not self._categories[category]:
                del self._categories[category]

        # 从标签索引中删除
        for tag in metadata.get("tags", []):
            if tag in self._tags:
                self._tags[tag].discard(template_name)
                if not self._tags[tag]:
                    del self._tags[tag]

        # 从缓存中删除
        if template_name in self._cache:
            del self._cache[template_name]

        # 保存注册表
        self._save_registry()

        return True

    def get_template(self, name: str) -> Template:
        """获取模板

        Args:
            name: 模板名称

        Returns:
            模板对象

        Raises:
            TemplateNotFoundError: 模板未找到
        """
        # 先从缓存查找
        if name in self._cache:
            return self._cache[name]

        # 从注册表查找
        if name not in self._templates:
            raise TemplateNotFoundError(name)

        template = self._templates[name]

        # 缓存模板
        self._cache[name] = template

        return template

    def list_templates(
        self, category: Optional[str] = None, tag: Optional[str] = None
    ) -> List[str]:
        """列出模板

        Args:
            category: 按分类过滤
            tag: 按标签过滤

        Returns:
            模板名称列表
        """
        template_names = set(self._templates.keys())

        if category:
            template_names &= self._categories.get(category, set())

        if tag:
            template_names &= self._tags.get(tag, set())

        return sorted(list(template_names))

    def get_categories(self) -> List[str]:
        """获取所有分类

        Returns:
            分类名称列表
        """
        return sorted(list(self._categories.keys()))

    def get_tags(self) -> List[str]:
        """获取所有标签

        Returns:
            标签名称列表
        """
        return sorted(list(self._tags.keys()))

    def get_templates_by_category(self, category: str) -> List[str]:
        """根据分类获取模板

        Args:
            category: 分类名称

        Returns:
            模板名称列表
        """
        return sorted(list(self._categories.get(category, set())))

    def get_templates_by_tag(self, tag: str) -> List[str]:
        """根据标签获取模板

        Args:
            tag: 标签名称

        Returns:
            模板名称列表
        """
        return sorted(list(self._tags.get(tag, set())))

    def get_template_metadata(self, name: str) -> Optional[Dict]:
        """获取模板元数据

        Args:
            name: 模板名称

        Returns:
            元数据字典，如果模板不存在则返回 None
        """
        return self._template_metadata.get(name)

    def search_templates(self, query: str) -> List[str]:
        """搜索模板

        Args:
            query: 搜索关键词

        Returns:
            匹配的模板名称列表
        """
        query = query.lower()
        results = []

        for template_name, metadata in self._template_metadata.items():
            # 在名称、描述、标签中搜索
            searchable_text = " ".join(
                [
                    template_name.lower(),
                    metadata.get("description", "").lower(),
                    " ".join(metadata.get("tags", [])).lower(),
                ]
            )

            if query in searchable_text:
                results.append(template_name)

        return results

    def validate_template(self, template: Template) -> List[str]:
        """验证模板

        Args:
            template: 要验证的模板

        Returns:
            错误列表，如果为空则验证通过
        """
        errors = []

        # 检查必需字段
        if not template.name:
            errors.append("Template name is required")

        if not template.steps:
            errors.append("Template must have at least one step")

        # 检查步骤
        step_ids = set()
        for i, step in enumerate(template.steps):
            # 检查步骤ID唯一性
            if step.id:
                if step.id in step_ids:
                    errors.append(f"Duplicate step ID: {step.id}")
                step_ids.add(step.id)

            # 检查必需字段
            if not step.action:
                errors.append(f"Step {i} is missing action")

        # 检查参数
        for param_name, param in template.parameters.items():
            # 验证参数类型
            if param.type not in ["string", "number", "boolean", "url", "selector"]:
                errors.append(
                    f"Invalid parameter type for '{param_name}': {param.type}"
                )

            # 检查默认值类型
            if param.default is not None and not param.validate(param.default):
                errors.append(f"Invalid default value for parameter '{param_name}'")

        return errors

    def refresh(self):
        """刷新注册表

        重新扫描模板目录，加载新的模板和更新现有模板。
        """
        # 清空缓存
        self._cache.clear()

        # 重新加载注册表
        self._load_registry()

    def get_statistics(self) -> Dict:
        """获取注册表统计信息

        Returns:
            统计信息字典
        """
        return {
            "total_templates": len(self._templates),
            "categories": {
                name: len(templates) for name, templates in self._categories.items()
            },
            "tags": {name: len(templates) for name, templates in self._tags.items()},
            "cache_size": len(self._cache),
        }

    def clear_cache(self):
        """清空模板缓存"""
        self._cache.clear()

    def __len__(self) -> int:
        """返回注册表中的模板数量"""
        return len(self._templates)

    def __contains__(self, name: str) -> bool:
        """检查模板是否存在"""
        return name in self._templates

    def __iter__(self):
        """迭代器"""
        return iter(self._templates.keys())

    def __repr__(self) -> str:
        """字符串表示"""
        return f"TemplateRegistry(templates={len(self._templates)}, categories={len(self._categories)})"
