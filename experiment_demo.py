import streamlit as st
import pandas as pd
import random
import time
import re

st.set_page_config(page_title="新型在线任务平台内测", layout="centered")

# ==========================================
# 初始化隐藏的后台数据 (绝对不向前台展示组别)
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'Intro'
if 'is_ai' not in st.session_state:
    # 0代表控制组，1代表处理组。仅作为后台数据记录
    st.session_state.is_ai = random.choice([0, 1])
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'matched' not in st.session_state:
    st.session_state.matched = False

# 随机题库
if 'task1_questions' not in st.session_state:
    st.session_state.task1_questions = [(random.randint(11, 99), random.randint(11, 99)) for _ in range(3)]
if 'task2_questions' not in st.session_state:
    st.session_state.task2_questions = [(random.randint(11, 99), random.randint(11, 99)) for _ in range(3)]

def change_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# 页面 1：欢迎页 (包装为内测平台)
# ==========================================
def page_intro():
    st.title("💼 云端工作流平台测试")
    st.info("欢迎参与本平台的任务测试流。您的所有操作都将记录在案，我们将根据您完成的任务质量，发放真实的测试酬劳。\n\n**💵 薪酬换算：** 平台内的计价单位为“代币”，测试结束后将按照 **1代币 = 0.5元人民币** 结算至您的账户。")
    
    st.session_state.data['subject_id'] = st.text_input("请输入您的测试工号/学号：", "001")
    st.session_state.data['gender'] = st.radio("您的性别：", ["男性", "女性"])
    st.session_state.data['confidence'] = st.slider("请评估您对数据处理和基础算术的自信程度（1-10分）：", 1, 10, 5)
    
    if st.button("进入工作台", type="primary"):
        st.session_state.data['treatment_group'] = st.session_state.is_ai # 后台悄悄记录
        change_page('Task 1')

# ==========================================
# 页面 2：Task 1 计件模式 
# ==========================================
def page_task1():
    st.title("📝 模块一：常规数据处理")
    st.write("请完成以下加法核对任务。**每正确处理一条，您将获得 2 代币的基础薪酬**。")
    
    # 无痕区分组别
    if st.session_state.is_ai == 1:
        st.success("💡 **工作台提示：** 本平台已接入最新的 AI 大语言模型。您可以随时调用下方工具提高处理效率。")
        with st.expander("👉 展开 AI 助手"):
            ai_prompt = st.text_input("向AI提问（如：24+19）", key="ai_input_1")
            if st.button("发送", key="btn_ai_1"):
                numbers = re.findall(r'\d+', ai_prompt)
                if len(numbers) >= 2:
                    ans = int(numbers[0]) + int(numbers[1])
                    st.info(f"🤖 **AI：** 运算结果为 **{ans}**。")
                else:
                    st.warning("🤖 **AI：** 请输入需要计算的数字。")
    else:
        st.info("💻 **工作台提示：** 请在规定时间内，确保数据处理的准确率。")

    with st.form("task1_form"):
        user_answers = []
        for i, (a, b) in enumerate(st.session_state.task1_questions):
            ans = st.text_input(f"数据条目 {i+1}：{a} + {b} = ?")
            user_answers.append((a, b, ans))
            
        if st.form_submit_button("提交数据并进入下一模块"):
            score = 0
            for a, b, user_ans in user_answers:
                if user_ans.strip() == str(a + b):
                    score += 1
            st.session_state.data['task1_score'] = score
            st.session_state.data['task1_tokens'] = score * 2 
            change_page('Task 2')

# ==========================================
# 页面 3：Task 2 锦标赛模式 (事后匹配机制)
# ==========================================
def page_task2():
    st.title("🏆 模块二：竞标直通车")
    st.write("规则：本模块为**竞标模式**。您提交的成绩将与平台上随机匹配的**另外 3 名真实接单者**进行比对。**只有组内准确率最高者可获得 8代币/题**，其余人流标（收益为 0）。")
    
    if st.session_state.is_ai == 1:
        st.success("💡 **工作台提示：** 您的 AI 工具包持续生效中。")
        with st.expander("👉 展开 AI 助手"):
            ai_prompt = st.text_input("向AI提问", key="ai_input_2")
            if st.button("发送", key="btn_ai_2"):
                numbers = re.findall(r'\d+', ai_prompt)
                if len(numbers) >= 2:
                    ans = int(numbers[0]) + int(numbers[1])
                    st.info(f"🤖 **AI：** 结果是 **{ans}**！")

    with st.form("task2_form"):
        user_answers = []
        for i, (a, b) in enumerate(st.session_state.task2_questions):
            ans = st.text_input(f"数据条目 {i+1}：{a} + {b} = ?")
            user_answers.append((a, b, ans))
            
        if st.form_submit_button("提交成绩入库"):
            score = 0
            for a, b, user_ans in user_answers:
                if user_ans.strip() == str(a + b):
                    score += 1
            st.session_state.data['task2_score'] = score
            # 此处不给他们算钱，因为是“事后结算”
            change_page('Task 3')

# ==========================================
# 页面 4：Task 3 竞争意愿选择
# ==========================================
def page_task3():
    st.title("⚖️ 模块三：契约偏好设置")
    st.write("在未来的任务分发中，平台允许接单者自主选择结算契约类型。")
    choice = st.radio("请为您接下来的工作选择签约模式：", 
                      ["选项 A：稳健计件制（每处理对一条，固定结算 2 代币）", 
                       "选项 B：高额竞标制（成绩与同期他人比对，赢家每条 8 代币，输家 0 代币）"])
    if st.button("确认契约类型", type="primary"):
        st.session_state.data['compete_choice'] = 1 if "选项 B" in choice else 0
        change_page('Task 4')

# ==========================================
# 页面 5：Task 4 薪酬谈判博弈 (精准底线版)
# ==========================================
def page_task4():
    st.title("💼 模块四：项目报价与协商")
    st.write("平台目前有 4 个外包项目。发包方给出了【初始报价】。您可以选择直接接单，或者提出您的【反向报价（要价）】。")
    st.warning("⚠️ 注意：发包方在后台设置了严格的【最高预算底线】。如果您自己填写的要价超过了对方的底线，系统将自动判定流标，您将失去该项目的任何收益！")
    
    if st.session_state.is_ai == 1:
        st.success("💡 **工作台提示：** AI 赋能让您具备更高的产出价值，请在报价时酌情考量您的市场竞争力。")

    # 配置定制的任务参数 {"任务名": {"offer": 初始报价, "max": 隐藏最高预算}}
    tasks_config = {
        "A. 数据搜集": {"offer": 1.5, "max": 2.0},
        "B. 文案撰写": {"offer": 2.0, "max": 3.0},
        "C. 市场分析": {"offer": 2.5, "max": 4.0},
        "D. 会议提炼": {"offer": 2.0, "max": 3.0}
    }
    
    task4_total_tokens = 0

    with st.form("task4_form"):
        for task_name, params in tasks_config.items():
            base_offer = params["offer"]
            max_budget = params["max"]
            
            st.write(f"**{task_name}** | 初始报价：**{base_offer} 代币**")
            col1, col2 = st.columns(2)
            action = col1.radio("您的决策：", ["直接接受", "自主填写报价"], key=f"r_{task_name}", horizontal=True)
            
            # 被试者自己输入报价
            counter_offer = base_offer
            if action == "自主填写报价":
                counter_offer = col2.number_input("请输入您的要价：", min_value=0.0, value=base_offer + 0.5, step=0.1, key=f"i_{task_name}")
            
            # 记录数据
            st.session_state.data[f'negotiate_{task_name[-2:]}'] = 1 if action == "自主填写报价" else 0
            st.session_state.data[f'premium_{task_name[-2:]}'] = round(counter_offer - base_offer, 2)
            
            # 后台悄悄判断是否成交
            if counter_offer <= max_budget:
                task4_total_tokens += counter_offer
                st.session_state.data[f'success_{task_name[-2:]}'] = 1 # 谈判成功
            else:
                st.session_state.data[f'success_{task_name[-2:]}'] = 0 # 谈判失败流标
                
            st.divider()

        if st.form_submit_button("敲定所有项目协议"):
            st.session_state.data['task4_tokens'] = task4_total_tokens
            change_page('Result')

# ==========================================
# 页面 6：实验结束与数据展示
# ==========================================
def page_result():
    st.title("🎉 测试结束")
    st.write("感谢您完成本次平台的全部功能测试流程！")
    
    st.info("⏳ **结算通知：** 关于您在【模块二（竞标直通车）】的最终收益，系统需等待同批次其他被试者提交成绩后，进行统一比对和结算发放。")

    st.divider()
    st.write("🔒 **研究者后台数据一览表（被试者不可见）：**")
    st.caption("以下为您本次测试产生的微观截面数据。'treatment_group'=1 代表AI组，'success'=1 代表要价未超过底线谈判成功。")
    
    df = pd.DataFrame([st.session_state.data])
    st.dataframe(df, use_container_width=True)
    
    if st.button("清空缓存，开始下一个被试测试"):
        for key in list(st.session_state.keys()): 
            del st.session_state[key]
        st.rerun()

# 路由控制
if st.session_state.page == 'Intro': page_intro()
elif st.session_state.page == 'Task 1': page_task1()
elif st.session_state.page == 'Task 2': page_task2()
elif st.session_state.page == 'Task 3': page_task3()
elif st.session_state.page == 'Task 4': page_task4()
elif st.session_state.page == 'Result': page_result()
