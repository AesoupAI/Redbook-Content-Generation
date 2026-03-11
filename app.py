import os
import sys

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
import streamlit as st
import requests
import json
import re
import pandas as pd
from io import BytesIO

# 页面配置 - 小红书风格
st.set_page_config(
    page_title="AI小红书文案生成工具",
    page_icon="✨",
    layout="centered"
)

# 自定义CSS - 小红书风格
st.markdown("""
<style>
    /* 主色调 - 小红书粉色 */
    :root {
        --primary-color: #ff2442;
        --secondary-color: #ff85a2;
        --light-color: #fff0f3;
        --text-color: #333333;
        --border-color: #ffd6e0;
    }
    
    /* 页面背景 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 标题样式 */
    h1 {
        color: var(--primary-color) !important;
        font-weight: bold !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 副标题样式 */
    h2 {
        color: var(--text-color) !important;
        font-weight: 600 !important;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 36, 66, 0.3) !important;
    }
    
    /* 输入框样式 */
    .stTextArea > div > div > textarea {
        border: 2px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
    }
    
    /* 选择框样式 */
    .stSelectbox > div > div > select {
        border: 2px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background-color: var(--light-color) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    /* 卡片样式 */
    .card {
        background-color: white !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* 提示信息 */
    .info-text {
        color: #666666 !important;
        font-size: 0.9rem !important;
        text-align: center !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* 结果卡片 */
    .result-card {
        background-color: var(--light-color) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-top: 1.5rem !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* 过滤信息样式 */
    .filter-info {
        background-color: #e8f4f8 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        border-left: 4px solid #1976d2 !important;
    }
    
    /* 微调输入框 */
    .tweak-input {
        border: 2px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
    }
    
    /* 加载提示 */
    .loading-info {
        background-color: #e8f5e8 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        border-left: 4px solid #388e3c !important;
    }
</style>
""", unsafe_allow_html=True)

# 主标题和说明
st.title("✨ AI小红书文案生成工具")
st.markdown("<p class='info-text'>AI批量小红书文案生成工具，一键生成可直接发布</p>", unsafe_allow_html=True)
st.markdown("---")

# API配置部分
st.sidebar.header("API配置")

# API选择
api_choice = st.sidebar.selectbox(
    "选择API",
    ["Qwen", "DeepSeek", "Doubao"]
)

# API密钥输入

if api_choice == "Qwen":
    api_key = st.sidebar.text_input("Qwen API密钥", type="password")
    api_base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    st.sidebar.markdown("[获取Qwen API密钥](https://dashscope.console.aliyun.com/apiKey)")

elif api_choice == "DeepSeek":
    api_key = st.sidebar.text_input("sk-133886a2296d4464a182432191c5b207", type="password")
    api_base_url = "https://api.deepseek.com/v1/chat/completions"
    st.sidebar.markdown("[获取DeepSeek API密钥](https://platform.deepseek.com/api_keys)")

elif api_choice == "Doubao":
    api_key = st.sidebar.text_input("Doubao API密钥", type="password")
    api_base_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    st.sidebar.markdown("[获取Doubao API密钥](https://console.volcengine.com/ark/overview)")

st.sidebar.markdown("---")

# 文案参数配置
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.header("📝 文案配置")

# 手动输入文案需求
prompt = st.text_area(
    "输入文案需求（每行一个）",
    placeholder="例如：\n分享一款好用的保湿面霜，适合干皮\n推荐夏季清爽型防晒霜\n介绍平价好用的粉底液",
    height=150
)

# Excel导入功能
st.subheader("📊 Excel导入")

# 上传Excel文件
uploaded_file = st.file_uploader("上传Excel文件（.xlsx格式）", type="xlsx")

# 提供Excel模板下载
def create_excel_template():
    # 创建一个包含"内容主题"列的Excel文件
    df = pd.DataFrame({"内容主题": ["分享一款好用的保湿面霜，适合干皮", "推荐夏季清爽型防晒霜"]})
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output

# 下载模板按钮
template_file = create_excel_template()
st.download_button(
    label="📥 下载Excel模板",
    data=template_file,
    file_name="小红书文案需求模板.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 选择文案长度
length_choice = st.selectbox(
    "文案长度",
    ["短款 (30-50字)", "中款 (80-120字)", "长款 (150-200字)"]
)

# 选择语气
tone_choice = st.selectbox(
    "语气风格",
    ["温柔种草", "活泼吸睛"]
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# 无效需求过滤函数
def filter_invalid_prompts(prompts):
    valid_prompts = []
    invalid_count = 0
    
    for prompt in prompts:
        # 移除空白字符
        trimmed_prompt = prompt.strip()
        
        # 过滤空白行
        if not trimmed_prompt:
            invalid_count += 1
            continue
        
        # 过滤过短需求（少于5个字）
        if len(trimmed_prompt) < 5:
            invalid_count += 1
            continue
        
        # 过滤无意义文字（纯数字、纯字母或纯符号）
        if re.fullmatch(r'\d+', trimmed_prompt) or re.fullmatch(r'[a-zA-Z]+', trimmed_prompt) or re.fullmatch(r'\s+', trimmed_prompt):
            invalid_count += 1
            continue
        
        # 有效需求
        valid_prompts.append(trimmed_prompt)
    
    return valid_prompts, invalid_count

# 生成按钮
if st.button("🚀 生成文案", use_container_width=True):
    # 验证输入
    if not prompt and not uploaded_file:
        st.error("请输入文案需求或上传Excel文件")
    elif not api_key:
        st.error("请填写API密钥")
    else:
        try:
            # 收集所有需求
            all_prompts = []
            
            # 处理手动输入的需求
            if prompt:
                manual_prompts = prompt.split('\n')
                all_prompts.extend(manual_prompts)
            
            # 处理Excel导入的需求
            if uploaded_file:
                df = pd.read_excel(uploaded_file)
                if "内容主题" in df.columns:
                    excel_prompts = df["内容主题"].dropna().tolist()
                    all_prompts.extend(excel_prompts)
                    st.success(f"已导入 {len(excel_prompts)} 个需求")
                else:
                    st.warning("Excel文件中未找到'内容主题'列")
            
            # 过滤无效需求
            valid_prompts, invalid_count = filter_invalid_prompts(all_prompts)
            
            # 显示过滤信息
            if invalid_count > 0:
                st.markdown(f"<div class='filter-info'>已过滤 {invalid_count} 个无效需求，当前有效需求 {len(valid_prompts)} 个</div>", unsafe_allow_html=True)
            
            # 检查是否有有效需求
            if not valid_prompts:
                st.error("没有有效需求，请重新输入")
            else:
                # 根据选择的长度设置字数范围
                if length_choice == "短款 (30-50字)":
                    word_count = "30-50字"
                elif length_choice == "中款 (80-120字)":
                    word_count = "80-120字"
                else:
                    word_count = "150-200字"

                # 构建优化的系统提示词
                system_prompt = f"你是一个专业的小红书文案生成器，精通小红书爆款内容创作。请根据用户需求，生成一篇符合以下要求的小红书文案：\n" \
                              f"1. 标题要求：\n" \
                              f"   - 长度控制在15-20字，简洁有力\n" \
                              f"   - 增加吸睛emoji，贴合内容主题\n" \
                              f"   - 添加关键词，突出核心卖点\n" \
                              f"   - 采用小红书爆款标题风格，比如'谁懂啊！平价粉底液焊在脸上不脱妆✨'\n" \
                              f"   - 语气符合{tone_choice}风格\n" \
                              f"2. 正文要求：\n" \
                              f"   - 长度：{word_count}\n" \
                              f"   - 增加口语化表达，使用小红书常见语气词（比如'谁懂啊'、'绝了'、'家人们'等）\n" \
                              f"   - 强化种草感话术，突出产品优势和使用体验\n" \
                              f"   - 分段清晰，每段1-2句话，避免大段文字\n" \
                              f"   - 结尾添加互动话术，鼓励用户评论或点赞\n" \
                              f"3. 话题标签要求：\n" \
                              f"   - 精准匹配需求内容\n" \
                              f"   - 添加1-2个热门标签（如#小红书爆款 #种草）\n" \
                              f"   - 添加3-4个精准标签，与内容直接相关\n" \
                              f"   - 避免使用无关标签\n" \
                              f"4. 整体风格：\n" \
                              f"   - 符合小红书平台特点，吸引用户点击\n" \
                              f"   - 语气风格：{tone_choice}\n" \
                              f"   - 格式：标题（带emoji）+ 正文（分段）+ 话题标签"

                # 批量生成文案
                all_results = []
                for i, current_prompt in enumerate(valid_prompts, 1):
                    # 构建请求数据
                    payload = {
                        "model": "qwen-turbo" if api_choice == "Qwen" else "doubao-pro-1-5" if api_choice == "Doubao" else "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": current_prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }

                    # 发送请求
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    }

                    response = requests.post(api_base_url, headers=headers, json=payload, timeout=30)
                    response.raise_for_status()  # 检查HTTP错误

                    # 解析响应
                    result = response.json()
                    generated_content = result['choices'][0]['message']['content']
                    all_results.append(generated_content)

                # 保存结果到session state，用于后续操作
                st.session_state['valid_prompts'] = valid_prompts
                st.session_state['all_results'] = all_results
                st.session_state['system_prompt'] = system_prompt
                st.session_state['api_choice'] = api_choice
                st.session_state['api_key'] = api_key
                st.session_state['api_base_url'] = api_base_url

                # 显示生成的文案
                for i, result in enumerate(all_results, 1):
                    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                    st.subheader(f"🎯 生成结果 {i}")
                    st.markdown(result)
                    
                    # 文案微调功能
                    st.subheader("✏️ 文案微调")
                    tweak_input = st.text_area(
                        f"微调文案 {i}",
                        value=result,
                        height=200,
                        key=f"tweak_{i}"
                    )
                    
                    # 保存微调按钮
                    if st.button(f"💾 保存微调", key=f"save_tweak_{i}"):
                        st.session_state['all_results'][i-1] = tweak_input
                        st.success(f"文案 {i} 已更新")
                    
                    # 二次生成功能
                    if st.button(f"🔄 重新生成", key=f"regenerate_{i}"):
                        # 显示加载提示
                        with st.spinner("正在重新生成，请稍候..."):
                            # 构建请求数据
                            payload = {
                                "model": "qwen-turbo" if api_choice == "Qwen" else "doubao-pro-1-5" if api_choice == "Doubao" else "deepseek-chat",
                                "messages": [
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": valid_prompts[i-1]}
                                ],
                                "temperature": 0.7,
                                "max_tokens": 1000
                            }

                            # 发送请求
                            headers = {
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {api_key}"
                            }

                            response = requests.post(api_base_url, headers=headers, json=payload, timeout=30)
                            response.raise_for_status()

                            # 解析响应
                            result = response.json()
                            new_content = result['choices'][0]['message']['content']
                            
                            # 更新结果
                            st.session_state['all_results'][i-1] = new_content
                            st.success(f"文案 {i} 已重新生成")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # 复制按钮
                if all_results:
                    if st.button("📋 复制所有文案", key="copy_button", use_container_width=True):
                        st.success("文案已复制到剪贴板")

        except requests.exceptions.RequestException as e:
            st.error(f"网络异常：{str(e)}")
        except Exception as e:
            st.error(f"生成失败：{str(e)}")

# 页脚信息
st.markdown("---")
st.markdown("<p class='info-text'>💡 提示：请确保填写正确的API密钥，不同API需要对应不同的密钥</p>", unsafe_allow_html=True)