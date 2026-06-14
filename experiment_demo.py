import streamlit as st
import pandas as pd
import random
import time # 引入时间模块，用于制造“模拟匹配”的真实感

# 设置页面配置
st.set_page_config(page_title="经济学实验：AI与薪酬决策", layout="centered")

# 初始化 Session State
if 'page' not in st.session_state:
    st.session_state.page = 'Intro'
if 'group' not in st.session_state:
    st.session_state.group = random.choice(['控制组（无AI）', '处理组（有AI）'])
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'matched' not in st.session_state:
    st.session_state.matched = False

# 完美的页面跳转函数（解决需要点两下的Bug）
def change_page(page_name):
    st.session_state.page = page_name
    st.rerun() # 强制立即刷新页面

# ==========================================
# 页面 1：前置问卷与欢迎页
# ==========================================
def page_intro():
    st.title("📊 经济学在线实验")
    st.info("欢迎参与本次实验！您的所有决策都将影响您的最终真实收益。\n\n**💵 收益规则：** 实验中获得的所有收益将以“代币”计算。实验结束后，系统将随机抽取一个阶段的收益，按照 **1代币 = 0.5元人民币** 的汇率兑换为您真实的报酬。")
    
    st.subheader("前置信息收集")
    st.session_state.data['subject_id'] = st.text_input("请输入您的测试编号（如：001）：", "001")
    st.session_state.data['gender'] = st.radio("您的性别：", ["男性", "女性"])
    st.session_state.data['confidence'] = st.slider("请评估您对自己算术能力的自信程度（1-10分）：", 1, 10, 5)
    
    if st.button("我已了解规则，开始正式实验", type="primary"):
        st.session_state.data['group'] = st.session_state.group
        change_page('Task 1')

# ==========================================
# 页面 2：Task 1 计件模式 (多题测试)
# ==========================================
def page_task1():
    st.title("📝 阶段一：基础能力测试（计件模式）")
    st.write("规则：请完成以下加法任务。**每答对一题，您将获得 2 代币**。")
    
    if st.session_state.group == '处理组（有AI）':
        st.success("🤖 **系统提示：** 您可以使用屏幕下方的 AI 辅助工具帮您快速计算！")
        with st.expander("点击召唤 AI 助手进行辅助计算"):
            st.write("*(模拟AI界面：您可以将题目复制进来获取答案)*")
            st.text_input("向AI提问：")
    else:
        st.warning("🔒 **系统提示：** 您必须独立完成计算，禁止使用任何外部工具哦。")

    # 使用表单一次性提交多道题
    with st.form("task1_form"):
        st.subheader("请作答：")
        ans1 = st.text_input("第一题：24 + 19 = ?")
        ans2 = st.text_input("第二题：57 + 38 = ?")
        ans3 = st.text_input("第三题：82 + 45 = ?")
        
        submitted = st.form_submit_button("提交试卷并进入下一阶段")
        if submitted:
            # 简单的自动阅卷逻辑
            score = 0
            if ans1.strip() == "43": score += 1
            if ans2.strip() == "95": score += 1
            if ans3.strip() == "127": score += 1
            
            st.session_state.data['task1_score'] = score
            st.session_state.data['task1_tokens'] = score * 2 # 每题2代币
            change_page('Task 2')

# ==========================================
# 页面 3：Task 2 锦标赛模式 (模拟匹配机制)
# ==========================================
def page_task2():
    st.title("🏆 阶段二：竞争任务（锦标赛模式）")
    st.write("规则：系统已将您与另外 **3名真实在线用户** 随机组队。**只有组内答对题目最多者可获得 8代币/题**，其余人该轮收益为 0。")
    
    # 模拟真实匹配过程，增加心理压力
    if not st.session_state.matched:
        with st.spinner('正在全网为您匹配另外3名被试者，请稍候...'):
            time.sleep(2.5) # 暂停2.5秒制造假象
        st.session_state.matched = True
        st.rerun()

    st.success("✅ 匹配成功！您已被分配至 4人竞争小组。")
    
    if st.session_state.group == '处理组（有AI）':
        st.success("🤖 ChatGPT 辅助模块已为您开启，这可能让您在竞争中占据巨大优势。")

    with st.form("task2_form"):
        st.subheader("请快速作答（锦标赛）：")
        ans1 = st.text_input("第一题：68 + 29 = ?")
        ans2 = st.text_input("第二题：34 + 87 = ?")
        ans3 = st.text_input("第三题：91 + 16 = ?")
        
        submitted = st.form_submit_button("提交试卷并等待系统排名")
        if submitted:
            score = 0
            if ans1.strip() == "97": score += 1
            if ans2.strip() == "121": score += 1
            if ans3.strip() == "107": score += 1
            
            st.session_state.data['task2_score'] = score
            # 模拟：假设只要答对2题及以上就算第一名赢了
            st.session_state.data['task2_tokens'] = (score * 8) if score >= 2 else 0 
            change_page('Task 3')

# ==========================================
# 页面 4：Task 3 竞争意愿选择 
# ==========================================
def page_task3():
    st.title("⚖️ 阶段三：薪酬模式自主决策")
    st.write("在即将进行的下一轮任务中，系统允许您**自主选择**您的计薪方式。")
    
    choice = st.radio(
        "请为下一轮任务选择计薪契约：",
        ["选项 A：计件模式（稳妥：每答对一题拿2代币，与他人无关）", 
         "选项 B：锦标赛模式（竞争：系统将您的成绩与刚才小组中其他人的历史成绩进行比对，若您赢了每题拿8代币，输了拿0代币）"]
    )
    
    if st.button("锁定计薪方式", type="primary"):
        st.session_state.data['compete_choice'] = 1 if "选项 B" in choice else 0
        change_page('Task 4')

# ==========================================
# 页面 5：Task 4 薪酬谈判博弈 (核心创新点)
# ==========================================
def page_task4():
    st.title("💼 阶段四：模拟薪酬谈判博弈")
    st.write("您好，我是虚拟HR。现在公司有4个任务外包，给出了初始报价。您可以直接接受，或大胆提出**反向报价（讨价还价）**。")
    st.warning("⚠️ 隐藏规则：HR内心有一个最高预算，如果您要求的价格超过了HR的底线，谈判将直接破裂，您失去该工作机会（收益为0）。")
    
    if st.session_state.group == '处理组（有AI）':
        st.success("🤖 **AI已赋能：** 您拥有ChatGPT工具加持，工作效率和质量远超常人。请在讨价还价时充分考虑您的溢价资本！")

    tasks = {
        "A. 数据资料搜集整理": 1.5,
        "B. 短文案撰写与润色": 2.0,
        "C. 用户评论情感分析": 2.5,
        "D. 会议纪要核心提炼": 3.0
    }
    
    # 模拟谈判结果
    task4_total_tokens = 0

    with st.form("task4_form"):
        for task_name, base_offer in tasks.items():
            st.markdown(f"### {task_name}")
            st.write(f"HR初始报价：**{base_offer} 代币**")
            
            col1, col2 = st.columns(2)
            action = col1.radio(f"您的决策：", ["直接接受", "提出反向报价"], key=f"radio_{task_name}")
            
            counter_offer = base_offer
            if action == "提出反向报价":
                counter_offer = col2.number_input("您的要价 (代币)：", min_value=0.0, value=base_offer + 0.5, step=0.1, key=f"input_{task_name}")
                
            st.session_state.data[f'negotiate_{task_name[-2:]}'] = 1 if action == "提出反向报价" else 0
            st.session_state.data[f'premium_{task_name[-2:]}'] = round(counter_offer - base_offer, 2)
            
            # 记录预估收益（假设HR隐藏预算是原价+1.0）
            if counter_offer <= base_offer + 1.0:
                task4_total_tokens += counter_offer
            
            st.divider()

        submitted = st.form_submit_button("敲定所有合同并结算")
        if submitted:
            st.session_state.data['task4_tokens'] = task4_total_tokens
            change_page('Result')

# ==========================================
# 页面 6：结果与真实报酬兑换
# ==========================================
def page_result():
    st.title("🎉 实验圆满结束！")
    st.balloons()
    
    # 实验经济学标准操作：随机抽取一轮进行支付
    payoff_round = random.choice(['Task 1', 'Task 2', 'Task 4'])
    
    if payoff_round == 'Task 1':
        final_tokens = st.session_state.data.get('task1_tokens', 0)
    elif payoff_round == 'Task 2':
        final_tokens = st.session_state.data.get('task2_tokens', 0)
    else:
        final_tokens = st.session_state.data.get('task4_tokens', 0)
        
    final_rmb = round(final_tokens * 0.5, 2)

    st.success(f"🎲 **系统掷骰子结果：** 本次实验为您抽取 **{payoff_round}** 的表现进行真实报酬结算。")
    
    st.metric(label="您获得的实验代币", value=f"{final_tokens} 个")
    st.metric(label="兑换为真实人民币 (1代币=0.5元)", value=f"¥ {final_rmb} 元")

    st.divider()
    st.write("📈 **以下是您的回答结果。请查收！**")
    df = pd.DataFrame([st.session_state.data])
    st.dataframe(df, use_container_width=True)
    
    if st.button("重新开始演示 (清理数据)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==========================================
# 路由控制
# ==========================================
if st.session_state.page == 'Intro':
    page_intro()
elif st.session_state.page == 'Task 1':
    page_task1()
elif st.session_state.page == 'Task 2':
    page_task2()
elif st.session_state.page == 'Task 3':
    page_task3()
elif st.session_state.page == 'Task 4':
    page_task4()
elif st.session_state.page == 'Result':
    page_result()
