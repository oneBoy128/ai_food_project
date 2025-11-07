from code_rag.is_food_query_final_solution import extract_core_pair
import torch

# 若检索不出用户提到的菜名，则让模型自己检索
def is_food_teach(query, qwen_model, qwen_tokenizer):
    """
    基于 QWen-7B 模型，用QWEN-7B自己来给RAG检索之外的答案
    :param query: 用户查询（字符串）
    :param qwen_model: 加载好的 QWen-7B 模型
    :param qwen_tokenizer: 加载好的 QWen 分词器
    :return:
    """
    core_query = extract_core_pair(query)
    # 1. 构造提示词模板（替换 {{query}} 为实际用户查询）
    prompt_template = f"""###任务：基于用户的询问，返回食谱信息
    用户查询（query）：{core_query}

    ###输出要求：
    1. 若需要的是你推荐美食，则输出YES
    2. 若需要的是你提供这道菜的食谱，则返回相应的做法
    3. 用英文回答
    """

    # 填充用户查询到提示词中
    #prompt = prompt_template.format(query=query)

    # 2. 用 QWen 分词器处理提示词（适配 QWen 聊天格式）
    inputs = qwen_tokenizer.apply_chat_template(
        [
            {'role':"system", "content": '你是一个专业的美食顾问，你需要根据用户询问，判定他是需要你推荐美食还是提供这道菜的食谱'},
            {"role": "user", "content": prompt_template}
        ],  # 按 QWen 要求的聊天格式组织
        add_generation_prompt=True,  # 自动添加模型回复的前缀
        return_tensors="pt"  # 返回 PyTorch 张量
    ).to(qwen_model.device)  # 移到模型所在设备（GPU/CPU）

    # 3. 模型生成结果（控制输出长度，避免冗余）
    with torch.no_grad():  # 禁用梯度计算，节省内存
        outputs = qwen_model.generate(
            inputs,
            max_new_tokens=4000,  # 食物列表长度有限，50个token足够
            temperature=0.1,  # 降低随机性，确保输出格式稳定
            top_p=0.9,
            do_sample=False,  # 确定性生成，避免重复结果
            eos_token_id=qwen_tokenizer.eod_id  # 遇到结束符停止生成
        )

    # 4. 解码输出并提取食物列表
    # 提取模型生成的部分（排除输入提示词）
    generated_ids = outputs[:, inputs.shape[1]:]
    raw_output = qwen_tokenizer.decode(generated_ids[0], skip_special_tokens=True).strip()


    return raw_output
