import re
import torch
# 1. 核心搭配提取（不变，处理带动作的query）
# 1. 核心搭配提取（不变，处理带动作的query）
def extract_core_pair(query):
    food_actions = ["eat", "cook","cooking", "make", "bake", "fry", "prepare", "taste"]
    # 1. 先清理特殊符号（问号、小于号等）
    query_clean = re.sub(r'[?.,!;<>≤≥]', '', query).strip().lower()
    # 2. 过滤“时间/热量”等非食物条件词（关键新增）
    condition_words = ["time", "min", "minute", "hour", "calorie", "kcal", "cal"]
    for word in condition_words:
        query_clean = re.sub(rf'\b{word}\b\s*[0-9]*', '', query_clean).strip()

    # 3. 提取“动作+食物”核心搭配
    for action in food_actions:
        pattern = rf'\b{action}\b\s*(.*)'
        match = re.search(pattern, query_clean)
        if match:
            core_object = match.group(1).strip()
            stop_words = ["some", "the", "a", "an", "my", "your"]
            for stop in stop_words:
                core_object = re.sub(rf'\b{stop}\b', '', core_object).strip()
            if core_object:
                core_pair = f"{action} {core_object}"
                print(f"🎯 提取核心搭配：[{query}] → [{core_pair}]")
                return core_pair
    return query_clean

# 2. 单字词补全（不变）
def complete_single_word_query(query):
    if len(query.strip().split()) == 1:
        completed_query = f"eat {query.strip()}"
        return completed_query
    if len(query.strip().split()) == 2:
        completed_query = f"how to make {query.strip()}"
        return completed_query
    return query

# 3. 最终判断函数（新增“纯食物名词”规则）
def is_food_query_final_solution(query, model, tokenizer):
    core_query = extract_core_pair(query)
    completed_query = complete_single_word_query(core_query)

    # 关键新增：规则同时包含“动作+食材”和“纯食物名词组合”
    judge_prompt = f"""
        用户类型： 那些讨论美食相关话题的用户
        规则：1. 满足以下任一条件→YES，否则NO，仅输出YES/NO。
             2. 判定用户话题如果是与食物相关的->YES, 否则NO, 仅输出YES/NO
        1. 含eat/cook/cooking/make/bake/fry/about+食材（如make banana dessert→YES）；
        2. 纯食物名词组合.
        示例1：eat apple→YES；示例2：banana dessert→YES；示例3：use phone→NO。
        现在判断：{completed_query}→
        """

    with torch.no_grad():
        inputs = tokenizer.apply_chat_template(
            [
                {'role': "system", "content": '你是一个专业的吃货，只需判读这段对话是不是在讨论与美食相关的话题'},
                {"role": "user", "content": judge_prompt},
            ],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)

        outputs = model.generate(
            inputs,
            max_new_tokens=3,
            temperature=0.0,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            attention_mask=torch.ones_like(inputs)
        )

    raw_output = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True).strip()
    clean_output = re.sub(r'[。.\s]', '', raw_output).upper()
    print(f"🔍 核心搭配判断：[{completed_query}] → 输出：[{raw_output}]")
    return clean_output