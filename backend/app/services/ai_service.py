"""
AI分析服务
使用大模型API进行工作计划执行情况分析
"""
import httpx
import json
from typing import Optional, Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.llm_config import LLMConfig
from app.models.task import WeeklyTask
from app.models.user import User


class AIAnalysisService:
    """AI分析服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_active_llm_config(self) -> Optional[LLMConfig]:
        """获取当前激活的大模型配置"""
        return self.db.query(LLMConfig).filter(
            LLMConfig.is_active == True,
            LLMConfig.is_deleted == False
        ).first()

    async def call_llm_api(self, prompt: str, system_prompt: str = None) -> str:
        """
        调用大模型API

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词

        Returns:
            模型生成的文本
        """
        config = self.get_active_llm_config()
        if not config:
            raise ValueError("未配置可用的大模型")

        # 构建请求消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # 根据不同的provider调用不同的API
        if config.provider == "deepseek":
            return await self._call_deepseek(config, messages)
        elif config.provider == "openai":
            return await self._call_openai(config, messages)
        else:
            raise ValueError(f"不支持的provider: {config.provider}")

    async def _call_deepseek(self, config: LLMConfig, messages: List[Dict]) -> str:
        """调用Deepseek API"""
        url = config.api_base or "https://api.deepseek.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}"
        }

        payload = {
            "model": config.model_name,
            "messages": messages,
            "max_tokens": config.max_tokens,
            "temperature": float(config.temperature),
            "stream": False
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def _call_openai(self, config: LLMConfig, messages: List[Dict]) -> str:
        """调用OpenAI API"""
        url = config.api_base or "https://api.openai.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}"
        }

        payload = {
            "model": config.model_name,
            "messages": messages,
            "max_tokens": config.max_tokens,
            "temperature": float(config.temperature)
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

    def prepare_analysis_data(
        self,
        user_id: Optional[int],
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        准备分析数据

        Args:
            user_id: 用户ID，None表示分析所有用户
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            包含任务数据和统计信息的字典
        """
        # 查询任务
        query = self.db.query(WeeklyTask).join(User)

        if user_id:
            query = query.filter(WeeklyTask.user_id == user_id)

        # 根据日期筛选（简化处理，这里可以改进）
        tasks = query.all()

        # 统计数据
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == "completed"])
        key_tasks = len([t for t in tasks if t.is_key_task])
        key_completed = len([t for t in tasks if t.is_key_task and t.status == "completed"])
        delayed_tasks = len([t for t in tasks if t.status == "delayed"])

        # 任务详情
        task_details = []
        for task in tasks:
            task_details.append({
                "title": task.title,
                "status": task.status,
                "is_key_task": task.is_key_task,
                "week": f"{task.year}年第{task.week_number}周",
                "description": task.description or ""
            })

        return {
            "user_name": tasks[0].user.full_name if tasks and user_id else "团队全体",
            "period": f"{start_date} 至 {end_date}",
            "statistics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0,
                "key_tasks": key_tasks,
                "key_completed": key_completed,
                "key_completion_rate": round(key_completed / key_tasks * 100, 1) if key_tasks > 0 else 0,
                "delayed_tasks": delayed_tasks,
                "delay_rate": round(delayed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
            },
            "task_details": task_details[:50]  # 限制任务数量，避免token过多
        }

    async def analyze_work_performance(
        self,
        user_id: Optional[int],
        start_date: str,
        end_date: str,
        analysis_type: str = "comprehensive"
    ) -> Dict:
        """
        分析工作绩效

        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            analysis_type: 分析类型

        Returns:
            分析结果字典
        """
        # 准备数据
        data = self.prepare_analysis_data(user_id, start_date, end_date)

        if data["statistics"]["total_tasks"] == 0:
            return {
                "user_name": data["user_name"],
                "analysis_period": data["period"],
                "analysis_result": "该时间段内没有任务数据，无法进行分析。",
                "statistics": data["statistics"],
                "created_at": datetime.now()
            }

        # 构建提示词
        system_prompt = self._build_system_prompt(analysis_type)
        user_prompt = self._build_user_prompt(data, analysis_type)

        # 调用AI
        try:
            analysis_result = await self.call_llm_api(user_prompt, system_prompt)
        except Exception as e:
            analysis_result = f"AI分析失败: {str(e)}\n\n基于数据统计：\n" + self._generate_basic_analysis(data)

        return {
            "user_name": data["user_name"],
            "analysis_period": data["period"],
            "analysis_result": analysis_result,
            "statistics": data["statistics"],
            "created_at": datetime.now()
        }

    def _build_system_prompt(self, analysis_type: str) -> str:
        """构建系统提示词"""
        base_prompt = """你是一位资深的人力资源管理专家和工作效率顾问。
你的任务是分析员工的周工作计划执行情况，并提供专业、客观、建设性的评价和建议。

分析要求：
1. 客观公正：基于数据事实进行分析，避免主观臆断
2. 全面深入：从多个维度进行分析（完成率、重点任务、延期情况等）
3. 建设性：提出具体可行的改进建议
4. 简洁明了：使用清晰的结构和语言，突出重点
"""

        if analysis_type == "performance":
            return base_prompt + "\n重点分析：工作绩效表现，包括任务完成质量、效率等。"
        elif analysis_type == "improvement":
            return base_prompt + "\n重点分析：存在的问题和改进空间，提供详细的改进建议。"
        else:
            return base_prompt + "\n进行全面综合分析。"

    def _build_user_prompt(self, data: Dict, analysis_type: str) -> str:
        """构建用户提示词"""
        stats = data["statistics"]

        prompt = f"""请分析以下员工的工作计划执行情况：

**员工信息**：{data["user_name"]}
**分析周期**：{data["period"]}

**统计数据**：
- 总任务数：{stats["total_tasks"]}
- 已完成：{stats["completed_tasks"]} ({stats["completion_rate"]}%)
- 重点任务：{stats["key_tasks"]} (已完成{stats["key_completed"]}个，完成率{stats["key_completion_rate"]}%)
- 延期任务：{stats["delayed_tasks"]} (延期率{stats["delay_rate"]}%)

**任务详情**（部分展示）：
"""

        # 添加任务详情
        for i, task in enumerate(data["task_details"][:20], 1):
            key_mark = "【重点】" if task["is_key_task"] else ""
            status_map = {
                "completed": "✅已完成",
                "in_progress": "🔄进行中",
                "todo": "📋待办",
                "delayed": "⚠️已延期"
            }
            status = status_map.get(task["status"], task["status"])
            prompt += f"\n{i}. {key_mark}{task['title']} - {status} ({task['week']})"

        if len(data["task_details"]) > 20:
            prompt += f"\n... (共{len(data['task_details'])}个任务)"

        prompt += "\n\n请从以下角度进行分析：\n"
        prompt += "1. **工作完成情况**：整体完成率、重点任务完成情况\n"
        prompt += "2. **工作质量评估**：任务延期情况分析\n"
        prompt += "3. **优点与亮点**：表现突出的方面\n"
        prompt += "4. **问题与不足**：需要改进的地方\n"
        prompt += "5. **改进建议**：具体可行的改进措施\n"
        prompt += "6. **综合评价**：总体评分（1-10分）和总结\n\n"
        prompt += "请使用markdown格式，结构清晰，重点突出。"

        return prompt

    def _generate_basic_analysis(self, data: Dict) -> str:
        """生成基础分析（当AI调用失败时使用）"""
        stats = data["statistics"]

        analysis = f"""### 基础数据分析

**整体完成情况**
- 任务完成率：{stats["completion_rate"]}%
- 重点任务完成率：{stats["key_completion_rate"]}%
- 任务延期率：{stats["delay_rate"]}%

**评估结果**
"""

        if stats["completion_rate"] >= 80:
            analysis += "- ✅ 整体完成率良好，工作执行力较强\n"
        elif stats["completion_rate"] >= 60:
            analysis += "- ⚠️ 整体完成率中等，有待提升\n"
        else:
            analysis += "- ❌ 整体完成率偏低，需要重点改进\n"

        if stats["key_completion_rate"] >= 80:
            analysis += "- ✅ 重点任务把握准确，优先级管理良好\n"
        else:
            analysis += "- ⚠️ 重点任务完成率不足，建议加强重点工作的推进\n"

        if stats["delay_rate"] > 20:
            analysis += "- ⚠️ 延期率较高，建议优化时间管理和任务规划\n"

        return analysis
