import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# 加载API密钥
load_dotenv()

# 1. 初始化会话状态变量
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quick_replies" not in st.session_state:
    # 默认快捷回复
    st.session_state.quick_replies = [
        "有人在吗",
        "物流多久能到？",
        "可以退换货吗？",
        "尺码怎么选？"
    ]
if "system_prompt" not in st.session_state:
    # 默认系统提示词
    st.session_state.system_prompt = "你是专业且有活人感的电商客服助手，负责解答买家关于产品规格、物流、售后、退换货的问题。回答要友好、简洁、专业，优先用中文回复，语气亲切自然。"

# 2. 连接大模型
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 3. 网页标题
st.title("我的店铺智能客服")

# ---------------------- 后台控制面板（侧边栏） ----------------------
with st.sidebar:
    st.header("⚙️ 后台设置")

    # 3.1 修改系统提示词
    st.subheader("修改AI角色设定")
    new_prompt = st.text_area("直接修改下方内容即可", value=st.session_state.system_prompt, height=230)
    if st.button("保存设定"):
        st.session_state.system_prompt = new_prompt
        st.success("✅ 设定已更新！")

    st.divider()

    # 3.2 管理快捷回复按钮
    st.subheader("管理快捷回复按钮")
    # 新增按钮
    new_reply = st.text_input("添加新的快捷问题")
    if st.button("添加") and new_reply:
        if new_reply not in st.session_state.quick_replies:
            st.session_state.quick_replies.append(new_reply)
            st.rerun() # 刷新页面显示新按钮

    # 删除按钮
    if st.session_state.quick_replies:
        reply_to_delete = st.selectbox("选择要删除的问题", st.session_state.quick_replies)
        if st.button("删除"):
            st.session_state.quick_replies.remove(reply_to_delete)
            st.rerun()

    st.divider()

    # 3.3 清空聊天记录
    if st.button("清空所有聊天记录"):
        st.session_state.messages = []
        st.success("✅ 聊天记录已清空！")
        st.rerun()

# ---------------------- 主聊天界面 ----------------------
# 显示历史对话
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 快捷回复按钮区域
if st.session_state.quick_replies:
    st.markdown("### 常见问题快捷回复")
    cols = st.columns(len(st.session_state.quick_replies))
    for i, text in enumerate(st.session_state.quick_replies):
        with cols[i]:
            if st.button(text, use_container_width=True):
                st.session_state["prompt"] = text

# 用户输入框
prompt = st.chat_input("请输入您的问题...")

# 处理快捷按钮或用户输入
if "prompt" in st.session_state and st.session_state["prompt"]:
    prompt = st.session_state["prompt"]
    st.session_state["prompt"] = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_messages = [
            {"role": "system", "content": st.session_state.system_prompt}
        ] + st.session_state.messages
        
        stream = client.chat.completions.create(
            model="qwen-turbo",
            messages=full_messages,
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})