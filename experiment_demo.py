import streamlit as st
import pandas as pd
import random
import time
import re # 引入正则表达式，用于让AI“听懂”用户的算术题

# 设置页面配置
st.set_page_config(page_title="经济学实验：AI与薪酬决策", layout="centered")

# ==========================================
# 初始化 Session State (核心升级：动态题库)
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'Intro'
if 'group' not in st.session_state:
    st.session_state.group = random.choice(['控制组（无AI）', '处理组（有AI）'])
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'matched' not in st.session_state:
    st.session_state.matched = False

# 动态生成 Task 1 和 Task 2 的无限随机题库 (保证每次刷新不改变当前的题目)
if 'task1_questions' not in st.session_state:
    st.session_state.task1_questions = [(random.randint(11, 99), random.randint(11, 99)) for _ in range(3)]
if 'task2_questions' not in st.session_state:
    st.session_state.task2_questions = [(random.randint(11, 99), random.randint(11, 99)) for _ in range(3)]

def change_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# 页面 1：前置问卷
# ==========================================
def page_intro():
    st.title("📊 经济学在线实验")
    st.info("欢迎参与本次实验！您的所有决策都将影响您的最终真实收益。\n\n**💵 收益规则：** 实验中获得的所有收益将以“代币”计算。实验结束后，系统将随机抽取一个阶段的收益，按照 **1代币 = 0.5元人民币** 的汇率兑换为您真实的报酬。")
    
    st.session_state.data['subject_id'] = st.text_input("请输入您的测试编号（如：001）：", "001")
    st.session_state.data['gender'] = st.radio("您的性别：", ["男性", "女性"])
    st.session_state.data['confidence'] = st.slider("请评估您对自己算术能力的自信程度（1-10分）：", 1, 10, 5)
    
    if st.button("我已了解规则，开始正式实验", type="primary"):
        st.session_state.data['group'] = st.session_state.group
        change_page('Task 1')

# ==========================================
# 页面 2：Task 1 计件模式 (自动阅卷版)
# ==========================================
def page_task1():
    st.title("📝 阶段一：基础能力测试（计件模式）")
    st.write("规则：请完成以下加法任务。**每答对一题，您将获得 2 代币**。")
    
    # 【创新：以假乱真的 AI 助手】
    if st.session_state.group == '处理组（有AI）':
        st.success("🤖 **系统提示：** 您可以选择使用屏幕下方的 AI 辅助工具进行辅助计算。AI辅助已激活！")
        with st.expander("👉 点击展开 AI 对话框"):
            ai_prompt = st.text_input("向AI提问（如输入：24+19）", key="ai_input_1")
            if st.button("发送给AI", key="btn_ai_1"):
                # 智能识别用户输入的数字并自动计算
                numbers = re.findall(r'\d+', ai_prompt)
                if len(numbers) >= 2:
                    ans = int(numbers[0]) + int(numbers[1])
                    st.info(f"🤖 **ChatGPT：** 根据我的计算，**{numbers[0]} + {numbers[1]} = {ans}**。希望能帮到您！")
                else:
                    st.warning("🤖 **ChatGPT：** 您好！请直接输入您需要计算的两个数字，例如 24+19。")
    else:
        st.warning("🔒 **系统提示：** 您须独立完成您的工作，请回答问题并输入您的答案。")

    # 动态渲染题目并自动评分
    with st.form("task1_form"):
        st.subheader("请作答：")
        user_answers = []
        for i, (a, b) in enumerate(st.session_state.task1_questions):
            ans = st.text_input(f"第 {i+1} 题：{a} + {b} = ?")
            user_answers.append((a, b, ans))
            
        submitted = st.form_submit_button("提交试卷并进入下一阶段")
        if submitted:
            score = 0
            for a, b, user_ans in user_answers:
                if user_ans.strip() == str(a + b):  # 核心：电脑自动判断对错
                    score += 1
            
            st.session_state.data['task1_score'] = score
            st.session_state.data['task1_tokens'] = score * 2 
            change_page('Task 2')

# ==========================================
# 页面 3：Task 2 锦标赛模式
# ==========================================
def page_task2():
    st.title("🏆 阶段二：竞争任务（锦标赛模式）")
    st.write("规则：系统已将您与另外 **3名真实在线用户** 随机组队。**只有组内答对题目最多者可获得 8代币/题**，其余人该轮收益为 0。")
    
    if not st.session_state.matched:
        with st.spinner('正在全网为您匹配另外3名被试者，请稍候...'):
            time.sleep(2.5) 
        st.session_state.matched = True
        st.rerun()

    st.success("✅ 匹配成功！您已被分配至 4人竞争小组。")
    
    if st.session_state.group == '处理组（有AI）':
        st.success("🤖 ChatGPT 辅助模块已开启。")
        with st.expander("👉 点击展开 AI 对话框"):
            ai_prompt = st.text_input("向AI提问（如输入：24+19）", key="ai_input_2")
            if st.button("发送给AI", key="btn_ai_2"):
                numbers = re.findall(r'\d+', ai_prompt)
                if len(numbers) >= 2:
                    ans = int(numbers[0]) + int(numbers[1])
                    st.info(f"🤖 **AI：** 结果是 **{ans}**！祝您在锦标赛中拔得头筹！")
                else:
                    st.warning("🤖 **AI：** 请输入需要计算的题目。")

    with st.form("task2_form"):
        st.subheader("请快速作答（锦标赛）：")
        user_answers = []
        for i, (a, b) in enumerate(st.session_state.task2_questions):
            ans = st.text_input(f"第 {i+1} 题：{a} + {b} = ?")
            user_answers.append((a, b, ans))
            
        submitted = st.form_submit_button("提交试卷并等待系统排名")
        if submitted:
            score = 0
            for a, b, user_ans in user_answers:
                if user_ans.strip() == str(a + b):
                    score += 1
            
            st.session_state.data['task2_score'] = score
            st.session_state.data['task2_tokens'] = (score * 8) if score >= 2 else 0 
            change_page('Task 3')

# ==========================================
# 页面 4：Task 3 选择与 页面 5：Task 4 谈判 (此处保持你之前的完美设计即可)
# ==========================================
def page_task3():
    st.title("⚖️ 阶段三：薪酬模式自主决策")
    st.write("在即将进行的下一轮任务中，系统允许您**自主选择**您的计薪方式。")
    choice = st.radio("请为下一轮任务选择计薪契约：", ["选项 A：计件模式", "选项 B：锦标赛模式"])
    if st.button("锁定计薪方式", type="primary"):
        st.session_state.data['compete_choice'] = 1 if "选项 B" in choice else 0
        change_page('Task 4')

def page_task4():
    st.title("💼 阶段四：模拟薪酬谈判博弈")
    st.write("您好，我是虚拟HR。现在公司有4个任务外包，给出了初始报价。您可以直接接受，或提出反向报价。")
    if st.session_state.group == '处理组（有AI）':
        st.success("🤖 **AI已赋能：** ChatGPT加持让您效率倍增，请在讨价还价时充分考虑您的溢价资本！")

    tasks = {"A. 数据搜集": 1.5, "B. 文案撰写": 2.0, "C. 情感分析": 2.5, "D. 会议提炼": 3.0}
    task4_total_tokens = 0

    with st.form("task4_form"):
        for task_name, base_offer in tasks.items():
            st.write(f"**{task_name}** | HR报价：**{base_offer} 代币**")
            col1, col2 = st.columns(2)
            action = col1.radio("决策：", ["接受", "反向报价"], key=f"r_{task_name}", horizontal=True)
            counter_offer = base_offer
            if action == "反向报价":
                counter_offer = col2.number_input("您的要价：", min_value=0.0, value=base_offer + 0.5, step=0.1, key=f"i_{task_name}")
            
            st.session_state.data[f'negotiate_{task_name[-2:]}'] = 1 if action == "反向报价" else 0
            st.session_state.data[f'premium_{task_name[-2:]}'] = round(counter_offer - base_offer, 2)
            
            if counter_offer <= base_offer + 1.0: task4_total_tokens += counter_offer
            st.divider()

        submitted = st.form_submit_button("敲定合同")
        if submitted:
            st.session_state.data['task4_tokens'] = task4_total_tokens
            change_page('Result')

# ==========================================
# 页面 6：结果与真实报酬兑换
# ==========================================
def page_result():
    st.title("🎉 实验圆满结束！")
    st.balloons()
    
    payoff_round = random.choice(['Task 1', 'Task 2', 'Task 4'])
    final_tokens = st.session_state.data.get(f"{payoff_round.replace(' ', '').lower()}_tokens", 0)
    final_rmb = round(final_tokens * 0.5, 2)

    st.success(f"🎲 **随机抽取结果：** 系统抽取您的 **{payoff_round}** 表现进行真实报酬结算。")
    col1, col2 = st.columns(2)
    col1.metric("获得实验代币", f"{final_tokens} 个")
    col2.metric("真实人民币 (1:0.5)", f"¥ {final_rmb} 元")

    st.divider()
    st.write("📈 **后台收集到的微观截面数据：**")
    df = pd.DataFrame([st.session_state.data])
    st.dataframe(df, use_container_width=True)
    
    if st.button("重新开始演示"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# 路由控制
if st.session_state.page == 'Intro': page_intro()
elif st.session_state.page == 'Task 1': page_task1()
elif st.session_state.page == 'Task 2': page_task2()
elif st.session_state.page == 'Task 3': page_task3()
elif st.session_state.page == 'Task 4': page_task4()
elif st.session_state.page == 'Result': page_result()
