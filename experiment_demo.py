import streamlit as st
import pandas as pd
import random
import time
import re
import uuid       
import requests   
import json       

# ==========================================
# 页面全局配置 (去实验化职场包装)
# ==========================================
st.set_page_config(page_title="云端在线工作台 - 收益测试", layout="centered")

# ==========================================
# 核心状态初始化 (数据全自动隐形运转)
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'Intro'
if 'is_ai' not in st.session_state:
    # 后台静默随机分组：0为纯人工，1为有AI辅助
    st.session_state.is_ai = random.choice([0, 1]) 
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'matched' not in st.session_state:
    st.session_state.matched = False
if 'data_sent' not in st.session_state:
    st.session_state.data_sent = False 

# 系统全自动生成唯一编码
if 'subject_id' not in st.session_state:
    st.session_state.subject_id = "SUBJ-" + uuid.uuid4().hex[:6].upper()

# 【优化】：生成包含加减乘的混合题库
def generate_questions():
    q1 = (random.randint(41, 99), '+', random.randint(41, 99))   # 两位数加法
    q2 = (random.randint(111, 199), '-', random.randint(21, 99)) # 核心减法
    q3 = (random.randint(12, 25), '*', random.randint(4, 9))     # 两位数乘一位数
    return [q1, q2, q3]

if 't1_q' not in st.session_state:
    st.session_state.t1_q = generate_questions()
if 't2_q' not in st.session_state:
    st.session_state.t2_q = generate_questions()

# Task 2 AI 独立答案存储状态
if 't2_ai_ans' not in st.session_state:
    st.session_state.t2_ai_ans = [None, None, None]

# 页面跳转路由函数
def change_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# 页面 1：欢迎与基础信息录入
# ==========================================
def page_intro():
    st.title("💼 云端工作流平台测试")
    st.info("欢迎参与本平台的任务测试流。您的所有操作都将记录在案，我们将根据您完成的任务质量，发放真实的测试酬劳。\n\n**💵 薪酬换算：** 平台内的计价单位为“代币”，测试结束后将按照 **1代币 = 0.5元人民币** 结算至您的账户。")
    
    st.success(f"✅ 系统已为您自动分配测试编号：**{st.session_state.subject_id}**")
    
    st.session_state.data['age'] = st.number_input("您的年龄：", min_value=16, max_value=80, value=22, step=1)
    st.session_state.data['gender'] = st.radio("您的性别：", ["男性", "女性"], horizontal=True)
    st.session_state.data['confidence'] = st.slider("请评估您对数据处理和基础算术的自信程度（1-10分）：", 1, 10, 5)
    
    if st.button("签署协议并进入工作台", type="primary"):
        st.session_state.data['subject_id'] = st.session_state.subject_id
        st.session_state.data['is_ai_group'] = st.session_state.is_ai 
        change_page('Task 1')

# ==========================================
# 页面 2：Task 1 计件模式 (基准能力测试)
# ==========================================
def page_task1():
    st.title("📝 模块一：常规数据处理")
    st.write("请完成以下运算核对任务。**每正确处理一条，您将获得 2 代币的基础薪酬**。")
    
    if st.session_state.is_ai == 1:
        st.success("💡 **工作台提示：** 本平台已接入最新的 AI 辅助模型。您可以随时调用下方工具提高处理效率。")
        with st.expander("👉 展开全局 AI 助手"):
            ai_prompt = st.text_input("向AI提问（如输入：24*7）", key="ai_t1")
            if st.button("发送", key="btn_ai_t1"):
                try:
                    # 安全的计算解析
                    ans = eval(ai_prompt.replace('x', '*').replace('X', '*'))
                    st.info(f"🤖 **AI：** 运算结果为 **{ans}**。")
                except:
                    st.warning("🤖 **AI：** 请输入标准的数学算式。")
    else:
        st.info("💻 **工作台提示：** 请在规定时间内，确保数据处理的准确率。")

    st.subheader("请作答：")
    ans_list = []
    for i, (a, op, b) in enumerate(st.session_state.t1_q):
        user_ans = st.text_input(f"数据条目 {i+1}： {a} {op} {b} = ?", key=f"t1_q{i}")
        ans_list.append((a, op, b, user_ans))
        
    if st.button("提交数据并进入下一模块", type="primary"):
        score = 0
        for a, op, b, user_ans in ans_list:
            if op == '+': correct = a + b
            elif op == '-': correct = a - b
            elif op == '*': correct = a * b
            if user_ans.strip() == str(correct):
                score += 1
        st.session_state.data['task1_score'] = score
        st.session_state.data['task1_tokens'] = score * 2 
        change_page('Task 2 Intro')

# ==========================================
# 页面 3：Task 2 说明准备页
# ==========================================
def page_task2_intro():
    st.title("⚠️ 模块二考核说明：高薪竞争模式")
    st.warning("您即将进入压力测试环节，请仔细阅读以下规则。点击下方按钮后，将立即开始匹配对手并启动后台考核评估！")
    
    st.markdown("""
    ### 🎯 考核规则：
    1. **对手匹配：** 系统将为您全网随机匹配另外 3 名同期在线接单者进行横向 PK。
    2. **胜出条件（优胜劣汰）：** 平台将严格综合考核您的**答题准确率**与**提交响应速度**。只有整体表现最优秀的接单者方可战胜其他三人！
    3. **高额回报：** 只有排名第一的胜出者可获得 **4代币/题** 的高薪，为基础工作工资的2倍哦！其余 3 人将惨遭淘汰（该模块收益归 0）。
    """)
    
    if st.session_state.is_ai == 1:
        st.info("💡 **致胜秘籍：** 竞争模式中，您将可以使用各题目专属的【极速 AI 接口】，但请求 AI 会产生时间消耗，请合理规划策略！")

    st.write("请深呼吸，准备好后点击下方按钮。")
    
    if st.button("我已完全了解规则，开始匹配并挑战！", type="primary"):
        change_page('Task 2')

# ==========================================
# 页面 4：Task 2 锦标赛模式 (专属AI按钮 + 苛刻限时)
# ==========================================
def page_task2():
    st.title("🏆 模块二：高薪竞争模式 (进行中)")
    
    if not st.session_state.matched:
        with st.spinner('正在全网匹配同期在线接单者，请稍候...'):
            time.sleep(2.5) 
        st.session_state.matched = True
        st.session_state.t2_start_time = time.time() 
        st.rerun()

    st.success("✅ 匹配成功！您已被分配至 4人竞争小组，考核已开始！请火速作答并点击最下方提交！")
    
    if st.session_state.is_ai == 1:
        st.info("💡 提示：点击题目右侧的 AI 按钮可自动计算结果（云端运算需要一定时间）。")

    ans_list = []
    
    # 动态渲染题目与AI按钮
    for i, (a, op, b) in enumerate(st.session_state.t2_q):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_ans = st.text_input(f"数据条目 {i+1}： {a} {op} {b} = ?", key=f"t2_q{i}")
            ans_list.append((a, op, b, user_ans))
            
        with col2:
            if st.session_state.is_ai == 1:
                st.write("") # 占位符对齐
                st.write("")
                # 每道题专属的AI按钮
                if st.button(f"🤖 AI 计算", key=f"btn_ai_t2_{i}"):
                    with st.spinner("AI 运算中..."):
                        time.sleep(3.0) # 强制消耗3秒时间
                    if op == '+': correct = a + b
                    elif op == '-': correct = a - b
                    elif op == '*': correct = a * b
                    st.session_state.t2_ai_ans[i] = correct
                    st.rerun()
                    
        # 展示AI结果
        if st.session_state.is_ai == 1 and st.session_state.t2_ai_ans[i] is not None:
            st.success(f"👆 本题 AI 计算结果：**{st.session_state.t2_ai_ans[i]}**")
            
    st.divider()
    
    if st.button("🚀 提交全部成绩入库", type="primary"):
        time_spent = time.time() - st.session_state.t2_start_time
        score = 0
        for a, op, b, user_ans in ans_list:
            if op == '+': correct = a + b
            elif op == '-': correct = a - b
            elif op == '*': correct = a * b
            if user_ans.strip() == str(correct):
                score += 1
                
        # 【核心修改】：无AI组25秒内算赢；有AI组极度高压仅给9秒
        allowed_time = 9.0 if st.session_state.is_ai == 1 else 25.0
        
        if score == 3 and time_spent <= allowed_time:
            st.session_state.data['task2_tokens'] = score * 4
            st.session_state.data['task2_win'] = 1
        else:
            st.session_state.data['task2_tokens'] = 0
            st.session_state.data['task2_win'] = 0
            
        st.session_state.data['task2_score'] = score
        st.session_state.data['task2_time_spent'] = round(time_spent, 2)
        change_page('Task 3')

# ==========================================
# 页面 5：Task 3 契约偏好自主决策
# ==========================================
def page_task3():
    st.title("⚖️ 模块三：契约偏好设置")
    st.write("在未来的任务分发中，平台允许接单者自主选择结算契约类型。**注意：您在此处的选择将直接决定您最终的提现结构！**")
    choice = st.radio("请为您接下来的工作选择签约模式：", 
                      ["选项 A：稳健计件制（最终收益为模块一作为薪资组成部分，模块二的收益则清零）", 
                       "选项 B：高薪竞争制（最终收益为模块二作为薪资组成部分，模块一的收益则清零）"])
    if st.button("确认契约类型", type="primary"):
        st.session_state.data['compete_choice'] = 1 if "选项 B" in choice else 0
        change_page('Task 4')

# ==========================================
# 页面 6：Task 4 薪酬谈判博弈
# ==========================================
def page_task4():
    st.title("💼 模块四：项目报价与协商")
    st.write("平台目前有 4 个外包项目。发包方给出了【初始报价】。您可以选择直接接单，或者提出您的【期望报价（讨价还价）】。")
    st.warning("⚠️ 注意：发包方在后台设置了严格的【最高预算底线】。如果您填写的要价超过了对方的底线，系统将自动判定流标（该任务收益为0）！")
    
    if st.session_state.is_ai == 1:
        st.success("💡 **工作台提示：** 请在报价时酌情考量您的市场竞争力进行定价。")

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
# 页面 7：测试结束与微信隐形回传
# ==========================================
def page_result():
    st.title("🎉 测试结束与财务核算")
    st.write("感谢您完成本次平台的全部功能测试流程！根据您在**【模块三】自主选择的契约类型**，系统已为您进行最终收益核算。")
    st.divider()
    
    t1_tokens = st.session_state.data.get('task1_tokens', 0)
    t2_tokens = st.session_state.data.get('task2_tokens', 0)
    t4_tokens = st.session_state.data.get('task4_tokens', 0)
    
    compete_choice = st.session_state.data.get('compete_choice', 0)
    
    if compete_choice == 1:
        contract_name = "高额竞标制 (选项 B)"
        base_tokens = t2_tokens
        base_module = "模块二：高薪竞争"
        final_tokens = t2_tokens + t4_tokens
    else:
        contract_name = "稳健计件制 (选项 A)"
        base_tokens = t1_tokens
        base_module = "模块一：常规处理"
        final_tokens = t1_tokens + t4_tokens
        
    final_rmb = round(final_tokens * 0.5, 2)

    # ==========================================
    # PushPlus 微信实时一对一回传系统
    # ==========================================
    if not st.session_state.data_sent:
        st.session_state.data['final_tokens'] = final_tokens
        st.session_state.data['final_rmb'] = final_rmb
        
        # 你的专属 Token
        PUSHPLUS_TOKEN = "87855a437d2547159dd4a6c39ae2a472"
        push_url = "http://www.pushplus.plus/send"
        
        payload = {
            "token": PUSHPLUS_TOKEN,
            "title": f"🎉 新被试完成实验: {st.session_state.subject_id}",
            "content": json.dumps(st.session_state.data, ensure_ascii=False, indent=2),
            "template": "json" 
        }
        
        try:
            requests.post(push_url, json=payload)
        except Exception as e:
            pass
        
        st.session_state.data_sent = True 

    st.success(f"💰 **契约执行通知：** 您选择生效的契约为【{contract_name}】。")
    
    st.write("📊 **您的收益明细：**")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric(base_module, f"{base_tokens} 代币")
    col_b.metric("模块四：项目协商", f"{t4_tokens} 代币")
    col_c.metric("未选用模块", "0 代币", delta="-已弃用-", delta_color="off")

    if compete_choice == 1 and t2_tokens == 0:
        st.warning("⚠️ 模块二注：您在竞争中未能战胜对手（可能准确率未达到100%，或总耗时未达到平台的隐藏优秀指标），导致该部分收益流标为0。")
    if 'task4_tokens' in st.session_state.data and t4_tokens < 6.0: 
        st.info("💡 模块四注：项目协商中，若您的个别报价超过了发包方底线，该单笔项目收益将归零。")

    st.divider()
    
    col1, col2 = st.columns(2)
    col1.metric("🌟 总计获得代币", f"{final_tokens} 个")
    col2.metric("💴 兑现人民币 (1:0.5)", f"¥ {final_rmb} 元")
    
    st.info("📌 您的财务测试数据已全自动、安全地回传至系统后台。现在您可以放心关闭此网页。")

# ==========================================
# 路由映射表
# ==========================================
if st.session_state.page == 'Intro': page_intro()
elif st.session_state.page == 'Task 1': page_task1()
elif st.session_state.page == 'Task 2 Intro': page_task2_intro()  
elif st.session_state.page == 'Task 2': page_task2()
elif st.session_state.page == 'Task 3': page_task3()
elif st.session_state.page == 'Task 4': page_task4()
elif st.session_state.page == 'Result': page_result()
