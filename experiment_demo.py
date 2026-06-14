import streamlit as st
import pandas as pd
import random
import time
import re

# ==========================================
# 页面全局配置 (去实验化包装)
# ==========================================
st.set_page_config(page_title="云端在线工作台 - 收益测试", layout="centered")

# ==========================================
# 核心状态初始化 (数据静默运转)
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'Intro'
if 'is_ai' not in st.session_state:
    st.session_state.is_ai = random.choice([0, 1]) # 0无AI，1有AI。对用户绝对隐藏
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'matched' not in st.session_state:
    st.session_state.matched = False

# 随机题库生成 (保证每人/每次看到的题不同)
if 't1_q' not in st.session_state:
    st.session_state.t1_q = [(random.randint(11, 99), random.randint(11, 99)) for _ in range(3)]
if 't2_q' not in st.session_state:
    st.session_state.t2_q = [(random.randint(11, 99), random.randint(11, 99)) for _ in range(3)]

# 页面跳转路由
def change_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# 页面 1：欢迎与信息录入
# ==========================================
def page_intro():
    st.title("💼 云端工作流平台测试")
    st.info("欢迎参与本平台的任务测试流。您的所有操作都将记录在案，我们将根据您完成的任务质量，发放真实的测试酬劳。\n\n**💵 薪酬换算：** 平台内的计价单位为“代币”，测试结束后将按照 **1代币 = 0.5元人民币** 结算至您的账户。")
    
    st.session_state.data['subject_id'] = st.text_input("请输入您的测试工号/学号：", "001")
    st.session_state.data['gender'] = st.radio("您的性别：", ["男性", "女性"], horizontal=True)
    st.session_state.data['confidence'] = st.slider("请评估您对数据处理和基础算术的自信程度（1-10分）：", 1, 10, 5)
    
    if st.button("签署协议并进入工作台", type="primary"):
        st.session_state.data['is_ai_group'] = st.session_state.is_ai # 记录在后台数据中
        change_page('Task 1')

# ==========================================
# 页面 2：Task 1 计件模式 (常规数据处理)
# ==========================================
def page_task1():
    st.title("📝 模块一：常规数据处理")
    st.write("请完成以下加法核对任务。**每正确处理一条，您将获得 2 代币的基础薪酬**。")
    
    # 巧妙的AI工具展示
    if st.session_state.is_ai == 1:
        st.success("💡 **工作台提示：** 本平台已接入最新的 AI 辅助模型。您可以随时调用下方工具提高处理效率。")
        with st.expander("👉 展开 AI 助手"):
            ai_prompt = st.text_input("向AI提问（如输入：24+19）", key="ai_t1")
            if st.button("发送", key="btn_ai_t1"):
                numbers = re.findall(r'\d+', ai_prompt)
                if len(numbers) >= 2:
                    ans = int(numbers[0]) + int(numbers[1])
                    st.info(f"🤖 **AI：** 运算结果为 **{ans}**。")
                else:
                    st.warning("🤖 **AI：** 请输入需要计算的数字。")
    else:
        st.info("💻 **工作台提示：** 请在规定时间内，确保数据处理的准确率。")

    st.subheader("请作答：")
    ans_list = []
    # 动态渲染题目
    for i, (a, b) in enumerate(st.session_state.t1_q):
        user_ans = st.text_input(f"数据条目 {i+1}： {a} + {b} = ?", key=f"t1_q{i}")
        ans_list.append((a, b, user_ans))
        
    if st.button("提交数据并进入下一模块", type="primary"):
        score = 0
        for a, b, user_ans in ans_list:
            if user_ans.strip() == str(a + b):
                score += 1
        st.session_state.data['task1_score'] = score
        st.session_state.data['task1_tokens'] = score * 2 
        change_page('Task 2')

# ==========================================
# 页面 3：Task 2 锦标赛模式 (速度与准确率双重考核)
# ==========================================
def page_task2():
    st.title("🏆 模块二：竞标直通车")
    st.write("规则：本模块为**极速竞标模式**。您提交的成绩将与平台上随机匹配的**另外 3 名真实接单者**进行比对。**不仅看准确率，也看提交速度！只有第一名可获得 8代币/题**，其余人流标（收益为 0）。")
    
    # 1. 逼真的匹配加载动画
    if not st.session_state.matched:
        with st.spinner('正在全网匹配同期在线被试者，请稍候...'):
            time.sleep(2.5) 
        st.session_state.matched = True
        st.session_state.t2_start_time = time.time() # 记录匹配成功开始做题的时间
        st.rerun()

    st.success("✅ 匹配成功！您已被分配至 4人竞争小组，计时已开始！")
    
    if st.session_state.is_ai == 1:
        st.success("💡 **工作台提示：** AI 助手已激活，合理利用可大幅缩短您的作答时间！")
        with st.expander("👉 展开 AI 助手"):
            ai_prompt = st.text_input("向AI提问", key="ai_t2")
            if st.button("发送", key="btn_ai_t2"):
                numbers = re.findall(r'\d+', ai_prompt)
                if len(numbers) >= 2:
                    ans = int(numbers[0]) + int(numbers[1])
                    st.info(f"🤖 **AI：** 运算结果为 **{ans}**。")

    st.subheader("请快速作答：")
    ans_list = []
    for i, (a, b) in enumerate(st.session_state.t2_q):
        user_ans = st.text_input(f"数据条目 {i+1}： {a} + {b} = ?", key=f"t2_q{i}")
        ans_list.append((a, b, user_ans))
        
    if st.button("提交成绩入库", type="primary"):
        # 计算耗时
        time_spent = time.time() - st.session_state.t2_start_time
        
        score = 0
        for a, b, user_ans in ans_list:
            if user_ans.strip() == str(a + b):
                score += 1
                
        # 核心隐藏逻辑：准确率不能为0，且3道题总用时必须 <= 6秒（即平均单题<=2秒）才算赢
        if score > 0 and time_spent <= 6.0:
            st.session_state.data['task2_tokens'] = score * 8
            st.session_state.data['task2_win'] = 1
        else:
            st.session_state.data['task2_tokens'] = 0
            st.session_state.data['task2_win'] = 0
            
        st.session_state.data['task2_score'] = score
        st.session_state.data['task2_time_spent'] = round(time_spent, 2)
        change_page('Task 3')

# ==========================================
# 页面 4：Task 3 契约偏好
# ==========================================
def page_task3():
    st.title("⚖️ 模块三：契约偏好设置")
    st.write("在未来的任务分发中，平台允许接单者自主选择结算契约类型。")
    choice = st.radio("请为您接下来的工作选择签约模式：", 
                      ["选项 A：稳健计件制（无风险，固定结算基础酬劳）", 
                       "选项 B：高额竞标制（高风险，与同期他人比对速度与准确率，赢家通吃）"])
    if st.button("确认契约类型", type="primary"):
        st.session_state.data['compete_choice'] = 1 if "选项 B" in choice else 0
        change_page('Task 4')

# ==========================================
# 页面 5：Task 4 薪酬谈判博弈 (动态报价版)
# ==========================================
def page_task4():
    st.title("💼 模块四：项目报价与协商")
    st.write("平台目前有 4 个外包项目。发包方给出了【初始报价】。您可以选择直接接单，或者提出您的【期望报价（讨价还价）】。")
    st.warning("⚠️ 注意：发包方在后台设置了严格的【最高预算底线】。如果您填写的要价超过了对方的底线，系统将自动判定流标（收益为0）！")
    
    if st.session_state.is_ai == 1:
        st.success("💡 **工作台提示：** AI 赋能让您具备更高的产出价值，请在报价时酌情考量您的市场竞争力。")

    # 精准设定的规则字典：【初始报价, 最高底线】
    tasks_config = {
        "A. 数据搜集": {"offer": 1.5, "max": 2.0},
        "B. 文案撰写": {"offer": 2.0, "max": 3.0},
        "C. 市场分析": {"offer": 2.5, "max": 4.0},
        "D. 会议提炼": {"offer": 2.0, "max": 3.0}
    }
    
    task4_total_tokens = 0

    # 移除了会导致页面卡死的 st.form，使用标准布局实现动态联动
    for task_name, params in tasks_config.items():
        base_offer = params["offer"]
        max_budget = params["max"]
        
        st.write(f"**{task_name}** | 初始报价：**{base_offer} 代币**")
        
        # 动作选择
        action = st.radio("您的决策：", ["接受初始报价", "我要自己填报价"], key=f"r_{task_name}", horizontal=True)
        
        # 动态联动：如果选择填报价，输入框瞬间出现
        counter_offer = base_offer
        if action == "我要自己填报价":
            counter_offer = st.number_input("请输入您的要价（代币）：", min_value=0.0, value=base_offer + 0.5, step=0.1, key=f"i_{task_name}")
        
        # 记录数据
        st.session_state.data[f'negotiate_{task_name[-2:]}'] = 1 if action == "我要自己填报价" else 0
        st.session_state.data[f'premium_{task_name[-2:]}'] = round(counter_offer - base_offer, 2)
        
        # 判断流标逻辑
        if counter_offer <= max_budget:
            task4_total_tokens += counter_offer
            st.session_state.data[f'success_{task_name[-2:]}'] = 1 # 成功
        else:
            st.session_state.data[f'success_{task_name[-2:]}'] = 0 # 失败流标
            
        st.divider()

    if st.button("签署以上所有项目协议并进行最终结算", type="primary"):
        st.session_state.data['task4_tokens'] = task4_total_tokens
        change_page('Result')

# ==========================================
# 页面 6：实验结束与财务核算
# ==========================================
def page_result():
    st.title("🎉 测试结束与财务核算")
    st.write("感谢您完成本次平台的全部功能测试流程！根据机制，系统已从三大计薪模块中**随机抽取了一个模块**作为您的最终真实收益。")
    st.divider()
    
    # 随机抽取一轮支付
    payoff_round = random.choice(['Task 1 (常规数据处理)', 'Task 2 (竞标直通车)', 'Task 4 (项目报价与协商)'])
    
    if 'Task 1' in payoff_round:
        final_tokens = st.session_state.data.get('task1_tokens', 0)
    elif 'Task 2' in payoff_round:
        final_tokens = st.session_state.data.get('task2_tokens', 0)
    else:
        final_tokens = st.session_state.data.get('task4_tokens', 0)
        
    final_rmb = round(final_tokens * 0.5, 2)

    st.success(f"🎲 **系统随机抽取结果：** 您的 **【{payoff_round}】** 表现被选中进行提现结算。")
    
    if 'Task 2' in payoff_round and final_tokens == 0:
        st.warning("⚠️ 注：您在竞标模块中未能战胜对手（可能是准确率较低，或耗时过长），导致该模块流标收益为0。")
    elif 'Task 4' in payoff_round:
        st.info("💡 注：项目协商中，若您的报价超过了发包方底线，该单笔项目收益将归零计算。")

    # 醒目的收益展示面板
    col1, col2 = st.columns(2)
    col1.metric("💰 最终获得代币", f"{final_tokens} 个")
    col2.metric("💴 兑现人民币 (1:0.5)", f"¥ {final_rmb} 元")

    st.divider()
    with st.expander("🔐 仅研究者可见：微观底层数据看板 (被试者视角通常隐藏)"):
        st.caption("字段说明：is_ai_group(1为有AI), task2_win(1为胜出), success_XX(1为未超预算谈判成功)")
        df = pd.DataFrame([st.session_state.data])
        st.dataframe(df, use_container_width=True)
    
    if st.button("清空本地数据，准备下一次测试"):
        for key in list(st.session_state.keys()): 
            del st.session_state[key]
        st.rerun()

# 路由挂载
if st.session_state.page == 'Intro': page_intro()
elif st.session_state.page == 'Task 1': page_task1()
elif st.session_state.page == 'Task 2': page_task2()
elif st.session_state.page == 'Task 3': page_task3()
elif st.session_state.page == 'Task 4': page_task4()
elif st.session_state.page == 'Result': page_result()
