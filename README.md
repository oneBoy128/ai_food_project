# 项目文件
recipe-test是前端
week5 是后端，包括大模型配置和fast-api的配置以及数据清洗

# 数据来源
50万份食谱数据。
https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews

# 注意事项
1. 我没有上传chroma数据库，因为4.2g上传不了，请下载好数据来源然后用./code_rag/data_batch_loader.py进行数据清洗+文本embedding+存入chroma数据库一条龙
2. 我没有上传已经配置好的数据库，但是我有数据标注food_task.json，请使用mode_tiao来先生成大模型微调所需要的适配器
3. ./code_rag/run_rag.py是跑大模型的测试函数
4. 所有的大模型都是部署在了实验室服务器里，用的QWEN-7B-Chat.但具体版本未知，这个代码只做于本人学习
