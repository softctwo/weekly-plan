"""
初始化13个岗位的职责数据
基于PRD附录A和README.md
"""
from sqlalchemy.orm import Session
from ..models.role import Role, Responsibility, TaskType
from ..models.user import User, Department
from ..core.security import get_password_hash


def init_roles_and_responsibilities(db: Session):
    """初始化岗位职责库数据"""

    # 13个岗位的完整数据结构
    roles_data = [
        {
            "name": "研发工程师",
            "name_en": "R&D",
            "description": "负责产品功能开发、缺陷修复、技术预研等",
            "responsibilities": [
                {
                    "name": "产品功能开发",
                    "task_types": [
                        "需求分析与评审",
                        "技术方案设计",
                        "功能编码实现",
                        "单元测试编写",
                        "代码审查 (Code Review)"
                    ]
                },
                {
                    "name": "产品缺陷修复",
                    "task_types": [
                        "内部/客户Bug复现与定位",
                        "代码修复与验证",
                        "补丁包/小版本准备"
                    ]
                },
                {
                    "name": "技术预研与重构",
                    "task_types": [
                        "新技术调研",
                        "代码重构与性能优化"
                    ]
                },
                {
                    "name": "文档撰写",
                    "task_types": [
                        "技术设计文档编写",
                        "开发/运维手册更新"
                    ]
                }
            ]
        },
        {
            "name": "销售经理",
            "name_en": "Sales",
            "description": "负责客户开拓、关系维护、项目推进、合同回款",
            "responsibilities": [
                {
                    "name": "新客户/商机开拓 (金融)",
                    "task_types": [
                        "销售线索跟进",
                        "客户初步接洽与拜访",
                        "产品/公司介绍",
                        "客户需求挖掘与引导"
                    ]
                },
                {
                    "name": "客户关系维护 (金融)",
                    "task_types": [
                        "高层客户定期拜访",
                        "日常客户沟通与关系维护",
                        "关键节点（监管政策变动等）交流"
                    ]
                },
                {
                    "name": "销售项目推进",
                    "task_types": [
                        "协调售前资源（交流、方案）",
                        "产品演示与宣讲",
                        "投标/应标准备",
                        "商务谈判与合同拟定"
                    ]
                },
                {
                    "name": "合同与回款",
                    "task_types": [
                        "跟进合同审批流程",
                        "跟进项目回款"
                    ]
                }
            ]
        },
        {
            "name": "工程交付工程师",
            "name_en": "On-site Delivery",
            "description": "负责现场需求调研、ETL开发、系统部署测试、客户培训",
            "responsibilities": [
                {
                    "name": "项目需求调研 (现场)",
                    "task_types": [
                        "客户业务访谈（数据来源、规则）",
                        "需求规格说明书撰写",
                        "数据字典/接口规范确认",
                        "需求确认会议"
                    ]
                },
                {
                    "name": "ETL开发与配置",
                    "task_types": [
                        "数据抽取脚本开发",
                        "数据清洗/转换逻辑开发",
                        "数据加载脚本开发",
                        "ETL调度配置与测试"
                    ]
                },
                {
                    "name": "系统部署与测试 (现场)",
                    "task_types": [
                        "SIT/UAT环境部署",
                        "配合客户SIT/UAT测试",
                        "测试缺陷修复（ETL或配置）",
                        "生产环境部署"
                    ]
                },
                {
                    "name": "客户培训与上线",
                    "task_types": [
                        "用户/管理员操作培训",
                        "系统上线演练",
                        "上线后现场支持 (Go-live Support)",
                        "交付文档/运维手册移交"
                    ]
                }
            ]
        },
        {
            "name": "售后客服",
            "name_en": "After-sales",
            "description": "负责客户问题受理、在线支持、Bug跟踪上报",
            "responsibilities": [
                {
                    "name": "客户问题受理",
                    "task_types": [
                        "热线/工单接听与登记",
                        "问题初步诊断与分诊"
                    ]
                },
                {
                    "name": "在线支持与解答",
                    "task_types": [
                        "常见问题（操作咨询）解答",
                        "远程协助排查",
                        "数据查询（辅助客户）"
                    ]
                },
                {
                    "name": "Bug跟踪与上报",
                    "task_types": [
                        "Bug复现与确认",
                        "向研发/技术支持提单",
                        "跟进解决方案进度并反馈客户"
                    ]
                }
            ]
        },
        {
            "name": "技术支持工程师",
            "name_en": "Technical Support",
            "description": "负责产品升级维护、补丁安装、复杂问题处理",
            "responsibilities": [
                {
                    "name": "产品升级与维护 (现场)",
                    "task_types": [
                        "客户现场环境勘察",
                        "制定升级/迁移方案",
                        "现场执行产品升级",
                        "系统健康度巡检"
                    ]
                },
                {
                    "name": "补丁安装与验证 (现场)",
                    "task_types": [
                        "补丁发布与客户通知",
                        "现场安装与验证补丁"
                    ]
                },
                {
                    "name": "复杂问题处理 (现场/远程)",
                    "task_types": [
                        "重大故障现场排查 (On-site)",
                        "性能调优（数据库/应用）",
                        "配合客户/第三方联调"
                    ]
                }
            ]
        },
        {
            "name": "项目经理",
            "name_en": "Project Management",
            "description": "负责项目规划、执行监控、风险管理、客户沟通",
            "responsibilities": [
                {
                    "name": "项目启动与规划",
                    "task_types": [
                        "项目启动会（内/外部）",
                        "项目计划（WBS）制定",
                        "协调项目资源（人/物）"
                    ]
                },
                {
                    "name": "项目执行与监控",
                    "task_types": [
                        "主持项目周会/例会",
                        "撰写项目周报/月报",
                        "跟进项目进度与里程碑"
                    ]
                },
                {
                    "name": "风险与变更管理",
                    "task_types": [
                        "风险/问题识别与登记",
                        "推动问题解决",
                        "客户需求变更管理"
                    ]
                },
                {
                    "name": "客户沟通与验收",
                    "task_types": [
                        "客户方项目汇报",
                        "组织项目（阶段/终版）验收"
                    ]
                }
            ]
        },
        {
            "name": "售前工程师",
            "name_en": "Presales Engineer",
            "description": "负责产品演示、解决方案设计、投标支持、内部赋能",
            "responsibilities": [
                {
                    "name": "产品宣讲与演示",
                    "task_types": [
                        "客户需求初步沟通与引导",
                        "标准产品宣讲 (Demo)",
                        "产品PoC (Proof of Concept) 测试支持"
                    ]
                },
                {
                    "name": "解决方案设计 (定制化)",
                    "task_types": [
                        "客户定制化需求分析",
                        "撰写技术/业务解决方案",
                        "方案（技术/业务）交流与澄清"
                    ]
                },
                {
                    "name": "投标支持",
                    "task_types": [
                        "标书技术部分撰写",
                        "投标应答材料准备",
                        "参与现场述标/答疑"
                    ]
                },
                {
                    "name": "内部赋能与交底",
                    "task_types": [
                        "对销售/渠道进行产品培训",
                        "向交付团队（项目总监/PM）进行需求/方案交底"
                    ]
                }
            ]
        },
        {
            "name": "项目总监",
            "name_en": "Project Director",
            "description": "负责项目评估、成本估算、立项、重大项目监控",
            "responsibilities": [
                {
                    "name": "项目前期评估 (配合售前)",
                    "task_types": [
                        "参与售前/重大项目方案评审",
                        "评估客户需求可行性（技术/资源）",
                        "项目范围边界定义"
                    ]
                },
                {
                    "name": "项目成本与工作量估算",
                    "task_types": [
                        "工作任务拆解 (WBS) 估算",
                        "项目（人力/硬件）成本估算",
                        "项目交付周期评估"
                    ]
                },
                {
                    "name": "项目立项与启动",
                    "task_types": [
                        "撰写项目立项报告",
                        "参与公司立项评审",
                        "组建/指定项目核心团队"
                    ]
                },
                {
                    "name": "重大项目监控与协调",
                    "task_types": [
                        "监控重大项目关键里程碑",
                        "协调项目群资源冲突",
                        "介入处理重大项目风险/客户升级",
                        "指导（Mentor）项目经理"
                    ]
                }
            ]
        },
        {
            "name": "业务工程师",
            "name_en": "Business Engineer",
            "description": "负责业务需求梳理、数据逻辑分析、数据映射、UAT验证",
            "responsibilities": [
                {
                    "name": "业务需求访谈与梳理",
                    "task_types": [
                        "客户业务部门访谈（风控、清算等）",
                        "业务流程与场景梳理",
                        "业务术语表（Glossary）定义与对齐"
                    ]
                },
                {
                    "name": "业务数据逻辑分析",
                    "task_types": [
                        "梳理业务指标（KPI）计算规则",
                        "梳理数据（指标）的业务逻辑",
                        "分析数据流转（Data Flow）与加工逻辑"
                    ]
                },
                {
                    "name": "数据映射（Mapping）与规范定义",
                    "task_types": [
                        "根据系统接口要求，梳理源数据",
                        "撰写数据IT Mapping（源-目标）文档",
                        "定义数据清洗、转换、集成的业务规则"
                    ]
                },
                {
                    "name": "业务数据验证 (UAT)",
                    "task_types": [
                        "制定UAT（业务）测试方案",
                        "准备/协调UAT测试用例",
                        "执行/跟进业务数据验证",
                        "UAT缺陷的业务逻辑确认"
                    ]
                }
            ]
        },
        {
            "name": "人力资源",
            "name_en": "HR",
            "description": "负责招聘配置、薪酬绩效、员工关系与培训",
            "responsibilities": [
                {
                    "name": "招聘与配置",
                    "task_types": [
                        "简历筛选与面试安排",
                        "Offer沟通与入职办理"
                    ]
                },
                {
                    "name": "薪酬与绩效",
                    "task_types": [
                        "月度薪酬核算",
                        "绩效考核组织与执行"
                    ]
                },
                {
                    "name": "员工关系与培训",
                    "task_types": [
                        "员工入/离/转手续办理",
                        "组织新员工/专业培训"
                    ]
                }
            ]
        },
        {
            "name": "财务",
            "name_en": "Finance",
            "description": "负责会计核算、财务管理、税务资金管理",
            "responsibilities": [
                {
                    "name": "会计核算",
                    "task_types": [
                        "凭证审核与账务处理",
                        "月度/年度结账"
                    ]
                },
                {
                    "name": "财务管理",
                    "task_types": [
                        "财务报表编制",
                        "成本/费用审核（报销）",
                        "预算编制与分析"
                    ]
                },
                {
                    "name": "税务与资金",
                    "task_types": [
                        "税务申报",
                        "银行/出纳业务"
                    ]
                }
            ]
        },
        {
            "name": "行政",
            "name_en": "Admin",
            "description": "负责日常行政支持和服务",
            "responsibilities": [
                {
                    "name": "日常行政支持",
                    "task_types": [
                        "办公用品采购与管理",
                        "固定资产管理",
                        "办公环境维护"
                    ]
                },
                {
                    "name": "支持服务",
                    "task_types": [
                        "会议室/差旅预订",
                        "访客接待",
                        "公司活动组织"
                    ]
                }
            ]
        },
        {
            "name": "信息中心",
            "name_en": "Internal IT",
            "description": "负责IT基础架构运维、桌面支持、信息安全",
            "responsibilities": [
                {
                    "name": "IT基础架构运维",
                    "task_types": [
                        "服务器/网络维护",
                        "公司内部系统运维（OA, CRM, SVN）",
                        "数据备份与恢复"
                    ]
                },
                {
                    "name": "桌面支持 (Helpdesk)",
                    "task_types": [
                        "员工电脑/账号配置",
                        "软硬件问题排查（现场/远程）"
                    ]
                },
                {
                    "name": "信息安全",
                    "task_types": [
                        "内部安全策略执行",
                        "病毒/安全事件响应"
                    ]
                }
            ]
        }
    ]

    print("开始初始化岗位职责数据...")

    for idx, role_data in enumerate(roles_data, 1):
        # 创建岗位
        role = Role(
            name=role_data["name"],
            name_en=role_data["name_en"],
            description=role_data["description"]
        )
        db.add(role)
        db.flush()  # 获取role.id

        print(f"{idx}. 创建岗位: {role.name} ({role.name_en})")

        # 创建职责和任务类型
        for resp_idx, resp_data in enumerate(role_data["responsibilities"], 1):
            responsibility = Responsibility(
                role_id=role.id,
                name=resp_data["name"],
                sort_order=resp_idx
            )
            db.add(responsibility)
            db.flush()

            print(f"   - 职责 {resp_idx}: {responsibility.name}")

            # 创建任务类型
            for task_idx, task_name in enumerate(resp_data["task_types"], 1):
                task_type = TaskType(
                    responsibility_id=responsibility.id,
                    name=task_name,
                    sort_order=task_idx
                )
                db.add(task_type)

            print(f"     └─ {len(resp_data['task_types'])} 个任务类型")

    db.commit()
    print(f"\n✓ 成功初始化 {len(roles_data)} 个岗位的职责数据")


def init_admin_user(db: Session):
    """初始化管理员用户"""
    # 检查是否已存在管理员
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print("管理员用户已存在，跳过创建")
        return admin

    # 创建管理员用户
    admin = User(
        username="admin",
        email="admin@weekly-plan.com",
        full_name="系统管理员",
        hashed_password=get_password_hash("admin123"),
        user_type="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    print(f"✓ 创建管理员用户: {admin.username} (密码: admin123)")
    return admin


def init_sample_data(db: Session):
    """初始化示例数据"""
    print("\n开始初始化示例数据...")

    # 创建示例部门
    dept = Department(name="研发部", description="负责产品研发")
    db.add(dept)
    db.commit()
    db.refresh(dept)
    print(f"✓ 创建示例部门: {dept.name}")

    # 创建示例员工
    role = db.query(Role).filter(Role.name == "研发工程师").first()
    if role:
        employee = User(
            username="zhangsan",
            email="zhangsan@example.com",
            full_name="张三",
            hashed_password=get_password_hash("123456"),
            user_type="employee",
            department_id=dept.id,
            is_active=True
        )
        db.add(employee)
        db.commit()

        # 关联岗位
        from ..models.role import UserRoleLink
        link = UserRoleLink(user_id=employee.id, role_id=role.id)
        db.add(link)
        db.commit()

        print(f"✓ 创建示例员工: {employee.username} (密码: 123456)")


def initialize_database(db: Session):
    """完整的数据库初始化流程"""
    print("=" * 60)
    print("岗责驱动的周工作计划管理系统 - 数据库初始化")
    print("=" * 60)

    # 初始化岗位职责数据
    init_roles_and_responsibilities(db)

    # 初始化管理员用户
    init_admin_user(db)

    # 初始化示例数据
    init_sample_data(db)

    print("\n" + "=" * 60)
    print("数据库初始化完成！")
    print("=" * 60)
    print("\n登录信息：")
    print("管理员: admin / admin123")
    print("示例员工: zhangsan / 123456")
    print("=" * 60)
