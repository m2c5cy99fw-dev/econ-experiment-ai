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
    st.session_state.is_ai = random.choice([0, 1]) 
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'matched' not in st.session_state:
    st.session_state.matched = False

# 随机题库生成
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
        st.session_state.data['is_ai_group'] = st.session_state.is_ai 
        change_page('Task 1')

# ==========================================
# 页面 2：Task 1 计件模式 (常规数据处理)
# ==========================================
def page_task1():
    st.title("📝 模块一：常规数据处理")
    st.write("请完成以下加法核对任务。**每正确处理一条，您将获得 2 代币的基础薪酬**。")
    
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
# 页面 3：Task 2 锦标赛模式 (高压时间限制: 4秒)
# ==========================================
def page_task2():
    st.title("🏆 模块二：竞标直通车")
    st.write("规则：本模块为**极速竞标模式**。您提交的成绩将与平台上随机匹配的**另外 3 名真实接单者**进行比对。**不仅看准确率，也看提交速度！只有第一名可获得 8代币/题**，其余人流标（收益为 0）。")
    
    if not st.session_state.matched:
        with st.spinner('正在全网匹配同期在线被试者，请稍候...'):
            time.sleep(2.5) 
        st.session_state.matched = True
        st.session_state.t2_start_time = time.time() 
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
        time_spent = time.time() - st.session_state.t2_start_time
        score = 0
        for a, b, user_ans in ans_list:
            if user_ans.strip() == str(a + b):
                score += 1
                
        # 【修改点 1】：判定时间缩短为 4.0 秒
        if score > 0 and time_spent <= 4.0:
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
    st.write("在未来的任务分发中，平台允许接单者自主选择结算契约类型。**注意：您在此处的选择将直接决定您最终的提现结构！**")
    choice = st.radio("请为您接下来的工作选择签约模式：", 
                      ["选项 A：稳健计件制（最终收益 = 模块一常规处理 + 模块四协商）", 
                       "选项 B：高额竞标制（最终收益 = 模块二极速竞标 + 模块四协商）"])
    if st.button("确认契约类型", type="primary"):
        st.session_state.data['compete_choice'] = 1 if "选项 B" in choice else 0
        change_page('Task 4')

# ==========================================
# 页面 5：Task 4 薪酬谈判博弈 
# ==========================================
def page_task4():
    st.title("💼 模块四：项目报价与协商")
    st.write("平台目前有 4 个外包项目。发包方给出了【初始报价】。您可以选择直接接单，或者提出您的【期望报价（讨价还价）】。")
    st.warning("⚠️ 注意：发包方在后台设置了严格的【最高预算底线】。如果您填写的要价超过了对方的底线，系统将自动判定流标（收益为0）！")
    
    if st.session_state.is_ai == 1:
        st.success("💡 **工作台提示：** AI 赋能让您具备更高的产出价值，请在报价时酌情考量您的市场竞争力。")

    tasks_config = {
        "A. 数据搜集": {"offer": 1.5, "max": 2.0},
        "B. 文案撰写": {"offer": 2.0, "max": 3.0},
        "C. 市场分析": {"offer": 2.5, "max": 4.0},
        "D. 会议提炼": {"offer": 2.0, "max": 3.0}
    }
    
    task4_total_tokens = 0

    for task_name, params in tasks_config.items():
        base_offer = params["offer"]
        max_budget = params["max"]
        
        st.write(f"**{task_name}** | 初始报价：**{base_offer} 代币**")
        action = st.radio("您的决策：", ["接受初始报价", "我要自己填报价"], key=f"r_{task_name}", horizontal=True)
        
        counter_offer = base_offer
        if action == "我要自己填报价":
            counter_offer = st.number_input("请输入您的要价（代币）：", min_value=0.0, value=base_offer + 0.5, step=0.1, key=f"i_{task_name}")
        
        st.session_state.data[f'negotiate_{task_name[-2:]}'] = 1 if action == "我要自己填报价" else 0
        st.session_state.data[f'premium_{task_name[-2:]}'] = round(counter_offer - base_offer, 2)
        
        if counter_offer <= max_budget:
            task4_total_tokens += counter_offer
            st.session_state.data[f'success_{task_name[-2:]}'] = 1 
        else:
            st.session_state.data[f'success_{task_name[-2:]}'] = 0 
            
        st.divider()

    if st.button("签署以上所有项目协议并进行最终结算", type="primary"):
        st.session_state.data['task4_tokens'] = task4_total_tokens
        change_page('Result')

# ==========================================
# 页面 6：实验结束与财务核算 (契约选择绑定版)
# ==========================================
def page_result():
    st.title("🎉 测试结束与财务核算")
    st.write("感谢您完成本次平台的全部功能测试流程！根据您在**【模块三】自主选择的契约类型**，系统已为您进行最终收益核算。")
    st.divider()
    
    t1_tokens = st.session_state.data.get('task1_tokens', 0)
    t2_tokens = st.session_state.data.get('task2_tokens', 0)
    t4_tokens = st.session_state.data.get('task4_tokens', 0)
    
    # 提取被试在 Task 3 中的选择 (1为竞标，0为计件)
    compete_choice = st.session_state.data.get('compete_choice', 0)
    
    # 【修改点 2】：根据选择动态展示不同的组合收益
    if compete_choice == 1:
        contract_name = "高额竞标制 (选项 B)"
        base_tokens = t2_tokens
        base_module = "模块二：极速竞标"
        final_tokens = t2_tokens + t4_tokens
    else:
        contract_name = "稳健计件制 (选项 A)"
        base_tokens = t1_tokens
        base_module = "模块一：常规数据处理"
        final_tokens = t1_tokens + t4_tokens
        
    final_rmb = round(final_tokens * 0.5, 2)

    st.success(f"💰 **契约执行通知：** 您选择生效的契约为【{contract_name}】。")
    
    st.write("📊 **您的收益明细：**")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric(base_module, f"{base_tokens} 代币")
    col_b.metric("模块四：项目协商", f"{t4_tokens} 代币")
    col_c.metric("未选用模块", "0 代币", delta="-已弃用-", delta_color="off")

    # 失败提醒逻辑更新
    if compete_choice == 1 and t2_tokens == 0:
        st.warning("⚠️ 模块二注：您在竞标中未能战胜对手（可能是准确率未全对，或总耗时超过了 4 秒），导致该部分收益流标为0。")
    if 'task4_tokens' in st.session_state.data and t4_tokens < 6.0: 
        st.info("💡 模块四注：项目协商中，若您的个别报价超过了发包方底线，该单笔项目收益将归零。")

    st.divider()
    
    col1, col2 = st.columns(2)
    col1.metric("🌟 总计获得代币", f"{final_tokens} 个")
    col2.metric("💴 兑现人民币 (1:0.5)", f"¥ {final_rmb} 元")

    st.divider()
    with st.expander("🔐 仅研究者可见：微观底层数据看板 (被试者视角通常隐藏)"):
        st.caption("字段说明：compete_choice(1为竞标), is_ai_group(1为AI组), task2_win(1为胜出)")
        df = pd.DataFrame([st.session_state.data])
        st.dataframe(df, use_container_width=True)
    
    if st.button("清空本地数据，准备下一次测试", type="primary"):
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
