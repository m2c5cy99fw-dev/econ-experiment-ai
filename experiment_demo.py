import streamlit as st
import pandas as pd
import random

# 设置页面配置
st.set_page_config(page_title="经济学实验：AI与薪酬决策", layout="centered")

# 初始化 Session State（用于在不同页面间保存数据）
if 'page' not in st.session_state:
    st.session_state.page = 'Intro'
if 'group' not in st.session_state:
    st.session_state.group = random.choice(['控制组（无AI）', '处理组（有AI）'])
if 'data' not in st.session_state:
    st.session_state.data = {}

def change_page(page_name):
    st.session_state.page = page_name

# ==========================================
# 页面 1：前置问卷与欢迎页
# ==========================================
def page_intro():
    st.title("📊 经济学在线实验")
    st.info("欢迎参与本次实验。")
    
    st.subheader("前置信息收集")
    st.session_state.data['subject_id'] = st.text_input("请输入您的测试编号（如：001）：", "001")
    st.session_state.data['gender'] = st.radio("您的性别：", ["男性", "女性"])
    
    st.session_state.data['confidence'] = st.slider("请评估您对自己算术能力的自信程度（1-10分）：", 1, 10, 5)
    
    if st.button("开始正式实验", type="primary"):
        st.session_state.data['group'] = st.session_state.group
        change_page('Task 1')

# ==========================================
# 页面 2：Task 1 计件模式
# ==========================================
def page_task1():
    st.title("📝 阶段一：基础加法任务（计件模式）")
    st.write("规则：请在倒计时结束前完成尽可能多的两位数加法。每答对一题获得 **2代币**。")
    
    if st.session_state.group == '处理组（有AI）':
        st.success("🤖 **系统提示：** 您属于处理组。您可以使用屏幕下方的 ChatGPT 辅助工具帮您快速计算！")
        with st.expander("点击召唤 ChatGPT 辅助计算"):
            st.write("*(模拟AI界面：您可以将题目复制进来获取答案)*")
            st.text_input("向AI提问：")
    else:
        st.warning("🔒 **系统提示：** 您属于控制组。您必须独立完成计算，禁止使用任何外部工具。")

    st.subheader("当前题目：24 + 19 = ?")
    ans1 = st.text_input("请输入答案：", key="t1_q1")
    
    if st.button("提交并进入下一阶段"):
        st.session_state.data['task1_score'] = 10 if ans1 == "43" else random.randint(5, 9)
        change_page('Task 2')

# ==========================================
# 页面 3：Task 2 锦标赛模式
# ==========================================
def page_task2():
    st.title("🏆 阶段二：竞争任务（锦标赛模式）")
    st.write("规则：系统已将您与另外3名匿名用户匹配。仅答题数量**排名第一**者可获得 **8代币/题**，其余人收益为0。")
    
    if st.session_state.group == '处理组（有AI）':
        st.success("🤖 ChatGPT 辅助模块已开启。")

    st.subheader("当前题目：57 + 38 = ?")
    ans2 = st.text_input("请输入答案：", key="t2_q1")
    
    if st.button("提交并进入下一阶段"):
        st.session_state.data['task2_score'] = 12 if ans2 == "95" else random.randint(6, 11)
        change_page('Task 3')

# ==========================================
# 页面 4：Task 3 竞争意愿选择 (核心因变量 1)
# ==========================================
def page_task3():
    st.title("⚖️ 阶段三：薪酬模式决策")
    st.write("在下一轮的任务中，您可以自主选择您的计薪方式。这决定了您的风险与潜在收益。")
    
    choice = st.radio(
        "请选择：",
        ["选项 A：计件模式（每题2代币，无风险）", "选项 B：锦标赛模式（与小组竞争，赢家每题8代币，输家0代币）"]
    )
    
    if st.button("确认选择"):
        st.session_state.data['compete_choice'] = 1 if "选项 B" in choice else 0
        change_page('Task 4')

# ==========================================
# 页面 5：Task 4 薪酬谈判博弈 (核心创新点)
# ==========================================
def page_task4():
    st.title("💼 阶段四：模拟薪酬谈判博弈")
    st.write("系统（雇主）现在向您发布4个兼职任务，并给出了初始报价。您可以直接接受，或提出反向报价。")
    st.info("注意：如果您提出的价格超过了雇主隐藏的最高预算，您将失去该工作！")
    
    if st.session_state.group == '处理组（有AI）':
        st.success("🤖 **AI已就绪：** 强大的AI辅助将大幅提升您的工作效率，请在报价时考虑您的技术溢价！")

    tasks = {
        "A. 数据资料搜集整理": 1.5,
        "B. 短文案撰写与润色": 2.0,
        "C. 用户评论情感分析": 2.5,
        "D. 会议纪要核心提炼": 3.0
    }
    
    for task_name, base_offer in tasks.items():
        st.markdown(f"### {task_name}")
        st.write(f"雇主初始报价：**{base_offer} 代币**")
        
        col1, col2 = st.columns(2)
        action = col1.radio(f"您的决策 ({task_name})：", ["直接接受", "提出反向报价"], key=f"radio_{task_name}")
        
        counter_offer = base_offer
        if action == "提出反向报价":
            counter_offer = col2.number_input("请输入您的期望代币数：", min_value=0.0, value=base_offer + 0.5, step=0.1, key=f"input_{task_name}")
            
        st.session_state.data[f'negotiate_{task_name[-2:]}'] = 1 if action == "提出反向报价" else 0
        st.session_state.data[f'premium_{task_name[-2:]}'] = round(counter_offer - base_offer, 2)
        st.divider()

    if st.button("提交谈判决策", type="primary"):
        change_page('Result')

# ==========================================
# 页面 6：结果与数据后台展示
# ==========================================
def page_result():
    st.title("🎉 实验结束")
    st.balloons()
    st.write("感谢您的参与！。")
    
    df = pd.DataFrame([st.session_state.data])
    st.dataframe(df, use_container_width=True)
    
    st.success("✨恭喜！")
    
    if st.button("重新开始演示"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==========================================
# 路由控制 (核心：千万别漏掉这部分！)
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