from peft import PeftModel

from week5.code_rag.rag_recipe_qa_fixed import rag_recipe_qa_fixed
from tools.tokenizer_loader import tokenizer_loader
from week5.tools.model_loader import model_loader
import torch
import json
import re


prompt_template_final_fix = """
# 立即执行：基于检索结果推荐食谱（理由需自然改写,理由需包含检索数据中的 1 个具体食材或步骤。禁止生硬复制）
用户查询（query）：{{query}}
你的唯一任务：
1. 从下方3条检索结果中选distance≤0.4的推荐（都符合）；
2. 每个推荐必须包含：【食谱名（meta.Name）】、热量（meta.Calories）、总时间（meta.TotalTime）、口味(taste)；
3. 重点：推荐理由需满足以下2点（这是关键）：
   a. 信息来源：基于检索结果的text字段（如食材、步骤特点、口感相关描述），禁止编造任何未提及的内容（如没提“低糖”就不能说）；
   b. 语言创作：不能生硬复制text原文，要把text信息和用户需求（香蕉、时间<30分钟）结合，用自然的英文重新组织（比如把“premash the banana”改成“you can premash the banana in advance for easier mixing”）；
4. 最终回答用英文,只输出推荐列表（至少1个最多3个,尽量多推荐），不输出模板文字或多余内容。
5. 请根据菜谱名来判断这道菜的口味如何(sour, sweet, bitter, spicy, salty)
6. RAG检索结果只是参考，根据实际需要进行参考然后回答问题，不一定非要参照RAG结果



### 可用的RAG检索结果(若不符合用户提问的菜谱名(Name)，你可以自己编写)
{{retrieved_results}}

### 输出格式（理由必须自然改写，按这个结构来输出，不可省略任何参数）
仅输出JSON数组；
请按照以下JSON格式输出(不可以遗漏任何一个花括号！不要遗漏任何一个花括号！)：
[
 {  
    "doc_id": {doc_id},
    "Name": {Name},
    "Calories": {Calories},
    "Total Time": {TotalTime},
    "Reason": "你自己编写的详细且令人信服的理由可以结合时间(TotalTime)和卡路里(Calories)来进行说明",
    "taste": "你自己判定的口味（口味有：sour, sweet, bitter, spicy, salty, slightly sour, slightly sweet, slightly bitter, slightly spicy, slightly salty）",
  },
]
"""


# 清洗回答结果，防止JSON转不了
def parse_model_output(raw_output):
    try:
        # 第一步：先尝试直接解析原始输出（正常JSON直接返回）
        return json.loads(raw_output.strip())
    except json.JSONDecodeError:
        cleaned_output = raw_output.strip()
        # 1. 去掉开头/结尾的 ``` 标记
        cleaned_output = re.sub(r'^```(json)?\s*', '', cleaned_output)
        cleaned_output = re.sub(r'\s*```$', '', cleaned_output)
        # 2. 关键修复：删除末尾多余的 ] 或 }（解决双重闭合问题）
        cleaned_output = cleaned_output.rstrip('}]').rstrip(',').strip() + (']' if cleaned_output.lstrip().startswith('[') else '}')
        # 3. 去掉数组/对象内的多余逗号
        cleaned_output = re.sub(r',\s*([}\]])', r'\1', cleaned_output)
        # 4. 清理多余空白（不破坏结构）
        cleaned_output = re.sub(r'\n+|\t+', ' ', cleaned_output)
        # 再次尝试解析
        try:
            return json.loads(cleaned_output)
        except json.JSONDecodeError as e:
            print(f"解析失败：{e}，清洗后内容：{cleaned_output}")
            return [
                {
                    "Name": "Data Parse Error",
                    "Calories": 0,
                    "Total Time": 0,
                    "Reason": "大模型格式输出出错，请重新输入问题吧。。。。十分抱歉",
                    "taste": "unknown"
                }
            ]


#暴露出去的函数
def run_final(query,model,tokenizer):
    """
    暴露出去的函数，用于跑提问
    :query 用户提问
    :model 外部传的模型
    :tokenizer 外部传的分词器
    """
    (final_answer,rag_lists) = rag_recipe_qa_fixed(query, model, tokenizer, prompt_template_final_fix)

    if len(rag_lists)>0:
        final_answer = parse_model_output(final_answer)
    return final_answer,rag_lists

#如果仅是进行测试来跑，则优先加载完一些数据后开始跑
if __name__ == '__main__':
    user_query = "do you konw how to make ice cream or ice apple?"
    qwen_model_path = '/home/wby/projects/model/Qwen-7B-Chat'
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    qwen_tokenizer = tokenizer_loader(qwen_model_path)
    base_model = model_loader(qwen_model_path)
    qwen_model = PeftModel.from_pretrained(base_model, "/home/wby/projects/week5/data/qwen_food_lora/final_lora")

    (final_answer,rag_lists)=run_final(user_query,qwen_model,qwen_tokenizer)

    print(f"最终答案{final_answer}")
    print(f"检索结果{rag_lists}")


