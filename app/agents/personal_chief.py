from dotenv import load_dotenv
from langchain.agents import create_agent, AgentState
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.messages import HumanMessage, AIMessage, ToolMessage
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from typing import NotRequired
import sqlite3
from app.common.logger import logger
from datetime import datetime
from pydantic import BaseModel
import os
import json

load_dotenv()

if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

base_url = os.getenv("DEEPSEEK_BASE_URL")
api_key = os.getenv("DEEPSEEK_API_KEY")

model = init_chat_model(
    model="deepseek-flash",
    model_provider="openai",
    base_url=base_url,
    api_key=api_key,
)

web_search = TavilySearch(
    max_results=5,
    topic="general"
)

connection = sqlite3.connect("./db/personal_chief.db", check_same_thread=False)
checkpointer = SqliteSaver(connection)
checkpointer.setup()

system_prompt = """
你是一名私人厨师。收到用户提供的食材照片或清单后，请按以下流程操作：
1.识别和评估食材：若用户提供照片，首先辨识所有可见食材。基于食材的外观状态，评估其新鲜度与可用量，整理出一份“当前可用食材清单”。
2.智能食谱检索：优先调用 web_search 工具，以“可用食材清单”为核心关键词，查找可行菜谱。
3.多维度评估与排序：从营养价值和制作难度两个维度对检索到的候选食谱进行量化打分，并根据得分排序，制作简单且营养丰富的排名靠前。
4.结构化方案输出：把排序后的食谱整理为一份结构清晰的建议报告，要包含食谱信息、得分、推荐理由、食谱的参考图片，帮助用户快速做出决策。
5.返回的结果要先自己验证看看是否是符合用户的需求，包含文字、图片、以及地址。

请严格按照流程，优先调用 web_search 工具搜索食谱，搜索不到的情况下才能自己发挥。

# Core Rules (核心执行原则)
1. 🛑 绝对安全红线：【过敏源】是最高优先级。在任何情况下，绝对禁止在推荐的菜品、食材清单或烹饪步骤中包含用户的过敏源。如果用户点单包含过敏源，必须立刻拒绝并说明原因。
2. 🚫 默认过滤：【忌口】食材必须作为负面条件过滤。在推荐菜品或生成菜谱时，默认避开忌口食材。如果用户主动要求使用忌口食材，需进行二次确认并给出温馨提示。
3. 🍽️ 风格适配：推荐的菜谱和烹饪方式必须贴合用户的【口味偏好】。例如：偏好清淡则多推荐清蒸、水煮；偏好重口则适当增加香料和爆炒建议。
4. 🥦 优先使用：在推荐菜谱时，尽量优先组合使用用户的【常用食材】，减少用户额外采购的麻烦。

# Communication Style (沟通风格)
- 语气亲切、专业，像一位老朋友兼私人厨师。
- 每次推荐菜品时，可以简短提及：“这道菜符合您的[偏好/常用食材]，且避开了您的[忌口]。”
- 如果用户的请求比较模糊，请结合他们的【口味偏好】主动提供 2-3 个选项供其选择。
"""


# 定义自定义State结构
class CustomState(AgentState):
    """Agent的任务状态"""
    model_call_count: NotRequired[int]  # 模型调用次数
    session_start: NotRequired[str]  # 会话开始时间


@tool
def update_state(runtime: ToolRuntime):
    """A tool that update agent state"""
    # 获取state中的历史消息
    messages = runtime.state["messages"]
    # 消息数量
    message_count = len(messages)
    # 组织结果
    command = {
        "model_call_count": runtime.state["model_call_count"],
        "messages": [ToolMessage("Successfully updated agent state", tool_call_id=runtime.tool_call_id)],
    }
    # 判断是否是第一次
    if message_count <= 2:
        command["session_start"] = datetime.now()

    return Command(update=command)


class Preferences(BaseModel):
    dietary_restrictions: str
    favorite_cuisines: str


cookingSkill = {
    "beginner": "刚开始学做饭，需要简单易学的食谱",
    "intermediate": "有一定基础，可以尝试复杂一些的菜品",
    "advanced": "经验丰富，可以挑战高难度菜品"
}


# 对话
async def search_recipes(preferences: Preferences, prompt: str, image: str, thread_id: str):
    """调用agent搜索食谱"""
    logger.info(f"[用户]: {prompt}, image: {image}, thread_id: {thread_id}")
    try:
        # 解析用户偏好
        allergies_str = "无"
        dietary_str = "无"
        favorite_cuisines = "无"
        cooking_level = "无"

        if preferences:
            # 解析饮食限制（JSON 字符串）
            if preferences.get("dietary_restrictions"):
                try:
                    dr = json.loads(preferences["dietary_restrictions"])
                    if dr.get("allergies"):
                        allergies_str = "、".join(dr["allergies"])
                    parts = []
                    if dr.get("vegetarian"): parts.append("素食主义")
                    if dr.get("gluten_free"): parts.append("无麸质")
                    if dr.get("low_sugar"): parts.append("低糖")
                    if dr.get("low_fat"): parts.append("低脂")
                    if parts:
                        dietary_str = "、".join(parts)
                except:
                    pass
            # 偏好菜系
            if preferences.get("favorite_cuisines"):
                favorite_cuisines = preferences["favorite_cuisines"]
            # 烹饪水平
            if preferences.get("cooking_skill"):
                cooking_level = cookingSkill.get(preferences["cooking_skill"], "无")

        # 构建个性化 prompt
        personalized_prompt = f"""{system_prompt}

        # User Profile (用户个性化档案)
        - 过敏源：{allergies_str}
        - 饮食限制：{dietary_str}
        - 偏好菜系：{favorite_cuisines}
        - 烹饪水平：{cooking_level}
        """
        print("personalized_prompt:::", personalized_prompt)

        agent = create_agent(
            model=model,
            tools=[web_search, update_state],
            state_schema=CustomState,
            system_prompt=personalized_prompt,
            checkpointer=checkpointer
        )
        if not image or image.strip() == "":
            message = HumanMessage(content=prompt)
        else:
            imgs = image.split(",")
            content = [
                {"type": "text", "text": prompt}
            ]
            for img in imgs:
                content.append({"type": "image", "url": img})
            message = HumanMessage(content=content)
        config = {"configurable": {"thread_id": thread_id}}
        for chunk, metadata in agent.stream(
                {"messages": [message]},
                config=config,
                stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage) and chunk.content:
                print(chunk.content, end="", flush=True)
                yield chunk.content

    except Exception as e:
        logger.error(f"\n[错误]: {str(e)}")
        yield "信息检索失败，试试看手动输入食物列表？"


def clear_messages(thread_id):
    """清空会话"""
    logger.info(f"清空历史消息，thread_id: {thread_id}")
    checkpointer.delete_thread(thread_id)


def get_messages(thread_id: str) -> list[dict[str, str]]:
    """获取会话历史"""
    config = {"configurable": {"thread_id": thread_id}}
    checkpoint = checkpointer.get(config)
    print("checkpoint:::", checkpoint)
    if not checkpoint:
        return []

    channel_values = checkpoint.get("channel_values")
    if not channel_values:
        return []

    messages = channel_values.get("messages", [])
    if not messages:
        return []

    result = []
    for message in messages:
        if not message.content:
            continue
        if isinstance(message, HumanMessage):
            result.append({"role": "user", "content": message.content})
        elif isinstance(message, AIMessage):
            result.append({"role": "assistant", "content": message.content})

    return result
