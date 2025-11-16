#!/usr/bin/env python3
"""
全面测试脚本 - 岗责驱动的周工作计划管理系统
Comprehensive Testing Script for Weekly Plan Management System

测试内容 (Test Coverage):
1. 岗位职责数据结构验证 (Job Responsibilities Data Structure Validation)
2. 13个岗位完整性检查 (13 Job Positions Completeness Check)
3. 任务类型计数验证 (Task Type Count Validation)
4. 重复项检测 (Duplicate Detection)
5. 双语术语一致性 (Bilingual Terminology Consistency)
6. 层级结构验证 (Hierarchical Structure Validation)
7. 文档-代码一致性 (Documentation-Code Consistency)
"""

import sys
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime


def extract_roles_data():
    """从init_data.py文件中提取岗位数据"""
    # Import from the extracted file
    sys.path.insert(0, str(Path(__file__).parent))
    from roles_data_extracted import roles_data
    return roles_data


# 提取岗位数据
roles_data = extract_roles_data()


class ComprehensiveTestSuite:
    """全面测试套件"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "warnings": [],
            "errors": [],
            "statistics": {},
            "details": {}
        }

        # 期望的13个岗位 (Expected 13 job positions)
        self.expected_positions = {
            "研发工程师": "R&D",
            "销售经理": "Sales",
            "工程交付工程师": "On-site Delivery",
            "售后客服": "After-sales",
            "技术支持工程师": "Technical Support",
            "项目经理": "Project Management",
            "售前工程师": "Presales Engineer",
            "项目总监": "Project Director",
            "业务工程师": "Business Engineer",
            "人力资源": "HR",
            "财务": "Finance",
            "行政": "Admin",
            "信息中心": "Internal IT"
        }

        # README.md 中声明的任务类型数量 (Task type counts declared in README.md)
        self.expected_task_counts = {
            "研发工程师": {"responsibilities": 4, "task_types": 13},
            "销售经理": {"responsibilities": 4, "task_types": 13},
            "工程交付工程师": {"responsibilities": 4, "task_types": 16},
            "售后客服": {"responsibilities": 3, "task_types": 8},
            "技术支持工程师": {"responsibilities": 3, "task_types": 9},
            "项目经理": {"responsibilities": 4, "task_types": 11},
            "售前工程师": {"responsibilities": 4, "task_types": 12},
            "项目总监": {"responsibilities": 4, "task_types": 13},
            "业务工程师": {"responsibilities": 4, "task_types": 14},
            "人力资源": {"responsibilities": 3, "task_types": 6},
            "财务": {"responsibilities": 3, "task_types": 7},
            "行政": {"responsibilities": 2, "task_types": 6},
            "信息中心": {"responsibilities": 3, "task_types": 8}
        }

    def log_pass(self, test_name):
        """记录测试通过"""
        self.results["tests_passed"] += 1
        print(f"✅ PASS: {test_name}")

    def log_fail(self, test_name, error):
        """记录测试失败"""
        self.results["tests_failed"] += 1
        self.results["errors"].append(f"{test_name}: {error}")
        print(f"❌ FAIL: {test_name}")
        print(f"   错误: {error}")

    def log_warning(self, message):
        """记录警告"""
        self.results["warnings"].append(message)
        print(f"⚠️  WARNING: {message}")

    def test_1_position_count(self):
        """测试1: 验证岗位数量"""
        print("\n" + "="*60)
        print("测试1: 岗位数量验证 (Position Count Validation)")
        print("="*60)

        actual_count = len(roles_data)
        expected_count = 13

        if actual_count == expected_count:
            self.log_pass(f"岗位数量正确: {actual_count}/13")
        else:
            self.log_fail(f"岗位数量验证", f"期望13个岗位，实际{actual_count}个")

    def test_2_position_completeness(self):
        """测试2: 验证每个岗位的完整性"""
        print("\n" + "="*60)
        print("测试2: 岗位完整性验证 (Position Completeness)")
        print("="*60)

        actual_positions = {}

        for role in roles_data:
            role_name = role["name"]
            role_name_en = role["name_en"]
            actual_positions[role_name] = role_name_en

            # 验证必需字段
            required_fields = ["name", "name_en", "description", "responsibilities"]
            missing_fields = [f for f in required_fields if f not in role]

            if missing_fields:
                self.log_fail(f"岗位 {role_name} 字段完整性",
                            f"缺少字段: {', '.join(missing_fields)}")
            else:
                self.log_pass(f"岗位 {role_name} 字段完整")

        # 验证是否所有期望的岗位都存在
        missing_positions = set(self.expected_positions.keys()) - set(actual_positions.keys())
        extra_positions = set(actual_positions.keys()) - set(self.expected_positions.keys())

        if missing_positions:
            self.log_fail("岗位完整性", f"缺少岗位: {', '.join(missing_positions)}")

        if extra_positions:
            self.log_warning(f"发现未预期的岗位: {', '.join(extra_positions)}")

        # 验证英文名称匹配
        for cn_name, en_name in self.expected_positions.items():
            if cn_name in actual_positions:
                if actual_positions[cn_name] != en_name:
                    self.log_fail(f"岗位 {cn_name} 英文名称",
                                f"期望 '{en_name}'，实际 '{actual_positions[cn_name]}'")
                else:
                    self.log_pass(f"岗位 {cn_name} 英文名称匹配")

    def test_3_hierarchical_structure(self):
        """测试3: 验证层级结构"""
        print("\n" + "="*60)
        print("测试3: 层级结构验证 (Hierarchical Structure)")
        print("="*60)

        for role in roles_data:
            role_name = role["name"]

            # 验证职责列表存在且非空
            if "responsibilities" not in role or not role["responsibilities"]:
                self.log_fail(f"岗位 {role_name} 职责结构",
                            "职责列表为空或不存在")
                continue

            # 验证每个职责的结构
            for resp_idx, resp in enumerate(role["responsibilities"], 1):
                resp_name = resp.get("name", f"职责{resp_idx}")

                # 验证职责必需字段
                if "name" not in resp:
                    self.log_fail(f"岗位 {role_name} - 职责{resp_idx}",
                                "缺少 'name' 字段")
                    continue

                if "task_types" not in resp:
                    self.log_fail(f"岗位 {role_name} - {resp_name}",
                                "缺少 'task_types' 字段")
                    continue

                # 验证任务类型列表非空
                if not resp["task_types"]:
                    self.log_fail(f"岗位 {role_name} - {resp_name}",
                                "任务类型列表为空")
                else:
                    self.log_pass(f"岗位 {role_name} - {resp_name}: "
                                f"{len(resp['task_types'])} 个任务类型")

    def test_4_task_count_validation(self):
        """测试4: 验证任务类型数量"""
        print("\n" + "="*60)
        print("测试4: 任务类型数量验证 (Task Type Count Validation)")
        print("="*60)

        total_responsibilities = 0
        total_task_types = 0

        for role in roles_data:
            role_name = role["name"]

            # 计算职责数量
            resp_count = len(role.get("responsibilities", []))
            total_responsibilities += resp_count

            # 计算任务类型数量
            task_count = sum(len(r.get("task_types", []))
                           for r in role.get("responsibilities", []))
            total_task_types += task_count

            # 验证与README.md中的声明是否一致
            if role_name in self.expected_task_counts:
                expected = self.expected_task_counts[role_name]

                # 验证职责数
                if resp_count != expected["responsibilities"]:
                    self.log_fail(f"岗位 {role_name} 职责数量",
                                f"期望 {expected['responsibilities']}，实际 {resp_count}")
                else:
                    self.log_pass(f"岗位 {role_name} 职责数量: {resp_count}")

                # 验证任务类型数
                if task_count != expected["task_types"]:
                    self.log_fail(f"岗位 {role_name} 任务类型数量",
                                f"期望 {expected['task_types']}，实际 {task_count}")
                else:
                    self.log_pass(f"岗位 {role_name} 任务类型数量: {task_count}")

        # 记录统计信息
        self.results["statistics"]["total_positions"] = len(roles_data)
        self.results["statistics"]["total_responsibilities"] = total_responsibilities
        self.results["statistics"]["total_task_types"] = total_task_types

        print(f"\n📊 统计摘要:")
        print(f"   总岗位数: {len(roles_data)}")
        print(f"   总职责数: {total_responsibilities}")
        print(f"   总任务类型数: {total_task_types}")

        # 验证总任务类型数
        expected_total = 136  # README.md中声明的总数
        if total_task_types != expected_total:
            self.log_fail("总任务类型数量",
                        f"期望 {expected_total}，实际 {total_task_types}")
        else:
            self.log_pass(f"总任务类型数量: {total_task_types}")

    def test_5_duplicate_detection(self):
        """测试5: 检测重复项"""
        print("\n" + "="*60)
        print("测试5: 重复项检测 (Duplicate Detection)")
        print("="*60)

        # 检测岗位名称重复
        position_names = [role["name"] for role in roles_data]
        position_counts = Counter(position_names)
        duplicates = {name: count for name, count in position_counts.items() if count > 1}

        if duplicates:
            self.log_fail("岗位名称重复检测",
                        f"发现重复岗位: {duplicates}")
        else:
            self.log_pass("岗位名称无重复")

        # 检测每个岗位内部的任务类型重复
        for role in roles_data:
            role_name = role["name"]
            all_tasks = []

            for resp in role.get("responsibilities", []):
                all_tasks.extend(resp.get("task_types", []))

            task_counts = Counter(all_tasks)
            duplicates = {task: count for task, count in task_counts.items() if count > 1}

            if duplicates:
                self.log_fail(f"岗位 {role_name} 任务类型重复",
                            f"重复的任务类型: {duplicates}")
            else:
                self.log_pass(f"岗位 {role_name} 任务类型无重复")

    def test_6_bilingual_terminology(self):
        """测试6: 双语术语一致性"""
        print("\n" + "="*60)
        print("测试6: 双语术语一致性 (Bilingual Terminology)")
        print("="*60)

        # 检查每个岗位的中英文名称格式
        for role in roles_data:
            role_name = role.get("name", "")
            role_name_en = role.get("name_en", "")

            # 验证名称非空
            if not role_name or not role_name_en:
                self.log_fail(f"岗位名称格式",
                            f"中文名或英文名为空: '{role_name}' / '{role_name_en}'")
                continue

            # 验证中文名称是中文字符
            if not any('\u4e00' <= char <= '\u9fff' for char in role_name):
                self.log_warning(f"岗位 {role_name} 中文名称格式可能不正确")

            # 验证英文名称是英文字符
            if not role_name_en.replace(" ", "").replace("-", "").replace("&", "").isalpha():
                self.log_warning(f"岗位 {role_name} 英文名称格式可能不正确: '{role_name_en}'")
            else:
                self.log_pass(f"岗位 {role_name} ({role_name_en}) 双语格式正确")

    def test_7_data_quality(self):
        """测试7: 数据质量检查"""
        print("\n" + "="*60)
        print("测试7: 数据质量检查 (Data Quality Check)")
        print("="*60)

        for role in roles_data:
            role_name = role["name"]

            # 检查描述字段
            description = role.get("description", "")
            if not description or len(description) < 5:
                self.log_warning(f"岗位 {role_name} 描述过短或为空")
            else:
                self.log_pass(f"岗位 {role_name} 描述完整")

            # 检查职责名称
            for resp in role.get("responsibilities", []):
                resp_name = resp.get("name", "")
                if not resp_name or len(resp_name) < 2:
                    self.log_fail(f"岗位 {role_name} 职责名称",
                                "职责名称过短或为空")

                # 检查任务类型名称
                for task in resp.get("task_types", []):
                    if not task or len(task) < 2:
                        self.log_fail(f"岗位 {role_name} - {resp_name}",
                                    f"任务类型名称过短或为空: '{task}'")

    def test_8_coverage_analysis(self):
        """测试8: 覆盖度分析"""
        print("\n" + "="*60)
        print("测试8: 岗位覆盖度分析 (Position Coverage Analysis)")
        print("="*60)

        position_categories = {
            "客户面向岗位": ["研发工程师", "销售经理", "工程交付工程师", "售后客服",
                          "技术支持工程师", "项目经理", "售前工程师", "项目总监", "业务工程师"],
            "内部支持岗位": ["人力资源", "财务", "行政", "信息中心"]
        }

        actual_positions = {role["name"] for role in roles_data}

        for category, expected_roles in position_categories.items():
            expected_set = set(expected_roles)
            actual_in_category = expected_set & actual_positions

            coverage = len(actual_in_category) / len(expected_set) * 100

            print(f"\n{category}:")
            print(f"  期望: {len(expected_set)} 个岗位")
            print(f"  实际: {len(actual_in_category)} 个岗位")
            print(f"  覆盖率: {coverage:.1f}%")

            if coverage == 100:
                self.log_pass(f"{category} 覆盖完整")
            else:
                missing = expected_set - actual_in_category
                self.log_fail(f"{category} 覆盖度",
                            f"缺少岗位: {', '.join(missing)}")

    def generate_detailed_report(self):
        """生成详细报告"""
        print("\n" + "="*60)
        print("详细岗位职责报告 (Detailed Position Report)")
        print("="*60)

        for idx, role in enumerate(roles_data, 1):
            print(f"\n{idx}. {role['name']} ({role['name_en']})")
            print(f"   描述: {role.get('description', 'N/A')}")
            print(f"   职责数: {len(role.get('responsibilities', []))}")

            for resp_idx, resp in enumerate(role.get("responsibilities", []), 1):
                print(f"   {resp_idx}. {resp['name']}")
                task_types = resp.get('task_types', [])
                print(f"      任务类型数: {len(task_types)}")
                for task_idx, task in enumerate(task_types, 1):
                    print(f"      - {task}")

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "🔬"*30)
        print("岗责驱动的周工作计划管理系统 - 全面测试")
        print("Weekly Plan Management System - Comprehensive Testing")
        print("🔬"*30)

        # 运行所有测试
        self.test_1_position_count()
        self.test_2_position_completeness()
        self.test_3_hierarchical_structure()
        self.test_4_task_count_validation()
        self.test_5_duplicate_detection()
        self.test_6_bilingual_terminology()
        self.test_7_data_quality()
        self.test_8_coverage_analysis()

        # 生成详细报告
        self.generate_detailed_report()

        # 打印测试摘要
        self.print_summary()

        # 保存测试结果
        self.save_results()

        return self.results

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("📊 测试摘要 (Test Summary)")
        print("="*60)

        total_tests = self.results["tests_passed"] + self.results["tests_failed"]
        pass_rate = (self.results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0

        print(f"\n总测试数: {total_tests}")
        print(f"✅ 通过: {self.results['tests_passed']}")
        print(f"❌ 失败: {self.results['tests_failed']}")
        print(f"⚠️  警告: {len(self.results['warnings'])}")
        print(f"\n通过率: {pass_rate:.1f}%")

        # 统计信息
        if self.results["statistics"]:
            print(f"\n📈 数据统计:")
            for key, value in self.results["statistics"].items():
                print(f"   {key}: {value}")

        # 错误列表
        if self.results["errors"]:
            print(f"\n❌ 错误详情:")
            for error in self.results["errors"]:
                print(f"   - {error}")

        # 警告列表
        if self.results["warnings"]:
            print(f"\n⚠️  警告详情:")
            for warning in self.results["warnings"]:
                print(f"   - {warning}")

        # 最终判断
        print("\n" + "="*60)
        if self.results["tests_failed"] == 0:
            print("🎉 所有测试通过！(All Tests Passed!)")
        else:
            print("⚠️  存在失败的测试，请检查错误详情")
        print("="*60)

    def save_results(self):
        """保存测试结果到文件"""
        output_file = Path(__file__).parent / "test_results.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n💾 测试结果已保存到: {output_file}")

        # 同时生成Markdown格式的报告
        self.generate_markdown_report()

    def generate_markdown_report(self):
        """生成Markdown格式的测试报告"""
        output_file = Path(__file__).parent / "TEST_REPORT.md"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# 全面测试报告 (Comprehensive Test Report)\n\n")
            f.write(f"**测试时间**: {self.results['timestamp']}\n\n")

            # 测试摘要
            f.write("## 测试摘要 (Test Summary)\n\n")
            total_tests = self.results["tests_passed"] + self.results["tests_failed"]
            pass_rate = (self.results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0

            f.write(f"- **总测试数**: {total_tests}\n")
            f.write(f"- **✅ 通过**: {self.results['tests_passed']}\n")
            f.write(f"- **❌ 失败**: {self.results['tests_failed']}\n")
            f.write(f"- **⚠️ 警告**: {len(self.results['warnings'])}\n")
            f.write(f"- **通过率**: {pass_rate:.1f}%\n\n")

            # 数据统计
            if self.results["statistics"]:
                f.write("## 数据统计 (Statistics)\n\n")
                for key, value in self.results["statistics"].items():
                    f.write(f"- **{key}**: {value}\n")
                f.write("\n")

            # 错误详情
            if self.results["errors"]:
                f.write("## ❌ 错误详情 (Errors)\n\n")
                for error in self.results["errors"]:
                    f.write(f"- {error}\n")
                f.write("\n")

            # 警告详情
            if self.results["warnings"]:
                f.write("## ⚠️ 警告详情 (Warnings)\n\n")
                for warning in self.results["warnings"]:
                    f.write(f"- {warning}\n")
                f.write("\n")

            # 13个岗位详细信息
            f.write("## 岗位职责详细信息 (Position Details)\n\n")
            for idx, role in enumerate(roles_data, 1):
                f.write(f"### {idx}. {role['name']} ({role['name_en']})\n\n")
                f.write(f"**描述**: {role.get('description', 'N/A')}\n\n")

                resp_count = len(role.get('responsibilities', []))
                task_count = sum(len(r.get('task_types', [])) for r in role.get('responsibilities', []))
                f.write(f"**职责数**: {resp_count} | **任务类型数**: {task_count}\n\n")

                for resp_idx, resp in enumerate(role.get("responsibilities", []), 1):
                    f.write(f"#### {resp_idx}. {resp['name']}\n\n")
                    task_types = resp.get('task_types', [])
                    for task in task_types:
                        f.write(f"- {task}\n")
                    f.write("\n")

            # 最终结论
            f.write("## 测试结论 (Conclusion)\n\n")
            if self.results["tests_failed"] == 0:
                f.write("🎉 **所有测试通过！(All Tests Passed!)**\n\n")
                f.write("岗位职责数据结构完整、准确，符合系统设计要求。\n")
            else:
                f.write("⚠️ **存在失败的测试**\n\n")
                f.write("请检查上述错误详情，并进行相应修复。\n")

        print(f"📄 Markdown测试报告已保存到: {output_file}")


def main():
    """主函数"""
    suite = ComprehensiveTestSuite()
    results = suite.run_all_tests()

    # 根据测试结果返回适当的退出码
    sys.exit(0 if results["tests_failed"] == 0 else 1)


if __name__ == "__main__":
    main()
