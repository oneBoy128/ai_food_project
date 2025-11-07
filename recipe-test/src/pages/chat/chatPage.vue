<!-- 开始聊天 -->
<template>
  <div id="conter">
    <div id="chat_conter">
      <!--上面聊天框的容器-->
      <div id="chat_top" style="overflow: auto">
        <!-- 循环渲染动态消息（修复 key 和参数顺序） -->
        <div
          v-for="(obj, index) in messages"
          :key="index + obj.type"
          :class="
            obj.type === 'oneboy'
              ? 'myuser animate__animated animate__fadeInRight '
              : 'xiaokui  animate__animated animate__fadeInLeft '
          "
        >
          <div v-if="obj.type === 'oneboy'" style="display: flex">
            <!--用户的聊天-->
            <div class="user_liao">{{ obj.mess }}</div>
            <!---用户头像-->
            <div class="user_touxiang"></div>
          </div>

          <div v-else-if="obj.type === 'xiaokui'" style="display: flex">
            <!--小葵头像-->
            <div class="xiaokui_touxiang"></div>
            <!--小葵聊天-->
            <div class="xiaokui_liao">{{ obj.mess }}</div>
          </div>

          <!---卡片测试-->
          <div
            v-else-if="obj.type === 'recommand'"
            v-for="(card, cardIndex) in obj.mess"
            :key="cardIndex"
          >
            <!--卡片循环测试-->
            <div
              class="card_conter"
              @click="!isCardDisabled && getInform(card)"
            >
              <div
                class="box_card animate__animated animate__bounce"
                v-loading="loading"
                :class="{ disabled: isCardDisabled }"
              >
                <div class="card_p">
                  <div class="card_p_left">Name:</div>
                  <div class="card_p_right">{{ card.Name }}</div>
                </div>
                <div class="card_p">
                  <div class="card_p_left">Calories:</div>
                  <div class="card_p_right">{{ card.Calories }}</div>
                </div>
                <div class="card_p">
                  <div class="card_p_left">Total Time:</div>
                  <div class="card_p_right">{{ card["Total Time"] }}</div>
                </div>
                <div class="card_p">
                  <div class="card_p_left">Reason:</div>
                  <div class="card_p_right">
                    {{ card["Reason"] }}
                  </div>
                </div>
                <div class="card_p">
                  <div class="card_p_left">taste:</div>
                  <div class="card_p_right">{{ card.taste }}</div>
                </div>
              </div>
            </div>
          </div>

          <!--小葵的美食回答-->
          <div v-else-if="obj.type === 'answer'" style="display: flex">
            <!--小葵头像-->
            <div class="xiaokui_touxiang"></div>
            <!--小葵聊天-->
            <div class="xiaokui_liao answer">
              <div class="answer_p">
                <!--最特殊的一行————名字-->
                <div id="food_name" class="answer_p_right">
                  <b>{{ obj.mess.meta.Name }}</b>
                </div>
              </div>
              <div class="answer_p">
                <div class="answer_p_left"><b>RecipeCategory:</b></div>
                <div class="answer_p_right">
                  {{ obj.mess.meta.RecipeCategory }}
                </div>
              </div>
              <div class="answer_p">
                <div class="answer_p_left"><b>RecipeServings:</b></div>
                <div class="answer_p_right">
                  {{ obj.mess.meta.RecipeServings }}
                </div>
              </div>
              <div class="answer_p">
                <div class="answer_p_left"><b>TotalTime:</b></div>
                <div class="answer_p_right">
                  {{ times(obj.mess.meta.TotalTime) }} minute
                </div>
              </div>
              <!---食谱成分-->
              <div class="answer_p" style="display: block">
                <div class="answer_p_left">
                  <B>Ingredients and Quantities:</B>
                </div>
                <br />
                <div class="answer_p_right ingredients">
                  {{ obj.mess.ingredients }}
                </div>
              </div>
              <div class="answer_p">
                <div class="answer_p_left"><b>step:</b></div>
                <div class="answer_p_right">{{ obj.mess.cookingSteps }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!---下面输入框的容器-->
      <div id="bottom_conter">
        <el-input
          type="textarea"
          :rows="5"
          style="padding: 10px"
          placeholder="请输入内容"
          v-model="textarea"
          v-loading="loading"
        >
        </el-input>
        <el-button
          class="bottom_btn"
          type="primary"
          round
          @click="sendMessage"
          :loading="loading"
          >发送</el-button
        >
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "chatPage",
  data() {
    return {
      textarea: "", //用户发送的消息
      loading: false,
      isCardDisabled: false, // 控制所有卡片是否可点击
      xiaokui_list: [], //小葵的聊天记录
      user_list: [], //用户的聊天记录
      rag_list: [], // rag检索记录

      messages: [
        {
          type: "xiaokui",
          mess: "hello my name is Chen Xiao Kui how can i help you ?",
        },
        //{ type: "oneboy", mess: "hello my name is oneBoy" },
        //{type: "recommand",mess: [{Name: "The Best Apple Pie",Calories: 568.0,Total Time": 85.0,Reason:"If you're looking for a rich and flavorful apple pie you ajsiodjqioqwueioqw",taste: "sweet"}]},
        //{type: "answer",mess: {doc_id: "1111",meta: {Calories: 123,Name: "KungPaoChicken",RecipeCategory: 123,RecipeId: 12231,RecipeServings: 2,TotalTime: 9999,},text: "这是一个测试",},},
      ], // 聊天记录，用来生成对话
    };
  },
  methods: {
    //测试函数
    test(num1) {
      console.log("测试函数调用成功", num1);
    },

    //去重的塞入我的rag_list里
    isGet(rags_arr) {
      let existingDocIds = new Set(this.rag_list.map((item) => item.doc_id));

      rags_arr.forEach((newItem) => {
        if (newItem.doc_id && !existingDocIds.has(newItem.doc_id)) {
          this.rag_list.push(newItem);
          existingDocIds.add(newItem.doc_id);
        }
      });
    },

    // 修复：精准解析食谱文本（适配空格、换行等格式）
    parseRecipeText(text) {
      const result = { ingredients: "", cookingSteps: "" };
      if (!text) return result; // 防止text为空报错

      // 1. 提取 Ingredients and Quantities（适配冒号后可能的空格/换行）
      const ingredientsRegex =
        /Ingredients and Quantities:\s*(.*?)(?=\s*Cooking steps:|$)/s;
      const ingredientsMatch = text.match(ingredientsRegex);
      if (ingredientsMatch) {
        result.ingredients = ingredientsMatch[1].trim();
      }

      // 2. 提取 Cooking steps（适配冒号后可能的空格/换行，匹配到文本结束）
      const stepsRegex = /Cooking steps:\s*(.*?)$/s;
      const stepsMatch = text.match(stepsRegex);
      if (stepsMatch) {
        // 格式化步骤（兼容原始步骤的序号格式）
        result.cookingSteps = stepsMatch[1]
          .trim()
          .split(/\d+\.\s*/) // 按“数字. 空格”分割
          .filter((step) => step.trim()) // 过滤空内容
          .map((step, idx) => `${idx + 1}. ${step.trim()}`) // 重新加序号
          .join("\n");
      }

      return result;
    },

    //点击获取推荐卡片信息
    getInform(card) {
      let tests = this.rag_list.find(
        (item) => item["doc_id"] == card["doc_id"]
      );
      this.isCardDisabled = true;
      if (!tests) {
        console.log("请稍等，还在更新");
      } else {
        this.loading = true;
        setTimeout(() => {
          const choice_obj = tests;
          const parsedData = this.parseRecipeText(choice_obj.text);
          choice_obj.ingredients = parsedData.ingredients; // 新增食材属性
          choice_obj.cookingSteps = parsedData.cookingSteps; // 新增步骤属性
          console.log(choice_obj);
          this.messages.push({
            type: "answer",
            mess: choice_obj,
          });
          // 消息发送后，滚动到最底部
          this.$nextTick(() => {
            const chatTop = document.getElementById("chat_top");
            chatTop.scrollTop = chatTop.scrollHeight;
          });
          this.loading = false;
          this.isCardDisabled = false;
        }, 1500);
      }
    },

    //发送消息的函数
    sendMessage() {
      if (!this.textarea.trim()) return; // 空消息不发送

      // 1. 添加用户消息到数组
      this.messages.push({
        type: "oneboy",
        mess: this.textarea,
      });
      // 消息发送后，滚动到最底部
      this.$nextTick(() => {
        const chatTop = document.getElementById("chat_top");
        chatTop.scrollTop = chatTop.scrollHeight;
      });

      // 小葵回复：“请等待”
      setTimeout(() => {
        this.messages.push({
          type: "xiaokui",
          mess: "ok, please wait a minute ",
        });
        // 消息发送后，滚动到最底部
        this.$nextTick(() => {
          const chatTop = document.getElementById("chat_top");
          chatTop.scrollTop = chatTop.scrollHeight;
        });
      }, 200);

      this.loading = true;

      axios({
        method: "post",
        url: "http://localhost:8081/send_query",
        data: JSON.stringify({ query: this.textarea }),
        headers: {
          "Content-Type": "application/json;charset=UTF-8",
        },
      })
        .then((resp) => {
          setTimeout(() => {
            // 消息发送后，滚动到最底部
            this.$nextTick(() => {
              const chatTop = document.getElementById("chat_top");
              chatTop.scrollTop = chatTop.scrollHeight;
            });
          }, 200);
          console.log(resp);
          this.loading = false;
          if (resp.data.code == 200) {
            this.messages.push({
              type: "xiaokui",
              mess: "ok, i recommand some foods to you: ",
            });
            // 消息发送后，滚动到最底部
            this.$nextTick(() => {
              const chatTop = document.getElementById("chat_top");
              chatTop.scrollTop = chatTop.scrollHeight;
            });
            setTimeout(() => {
              const currentCards = resp.data.data["final_answer"];
              // 遍历食谱数组，逐个添加（每隔1秒）
              currentCards.forEach((card, index) => {
                // 第i个元素延迟 i*1000ms 出现（0、1000、2000...毫秒）
                setTimeout(() => {
                  this.messages.push({
                    type: "recommand",
                    mess: [card], // 每次只放一个卡片（保持数组格式，方便前端循环）
                  });
                  // 每次添加后滚动到底部
                  this.$nextTick(() => {
                    const chatTop = document.getElementById("chat_top");
                    chatTop.scrollTop = chatTop.scrollHeight;
                  });
                }, index * 1000); // 延迟时间递增
              });
            }, 1500);
            // 消息发送后，滚动到最底部
            this.$nextTick(() => {
              const chatTop = document.getElementById("chat_top");
              chatTop.scrollTop = chatTop.scrollHeight;
            });

            //塞入rag_list里
            this.isGet(resp.data.data["rag_lists"].slice(-3));
          } else if (resp.data.code == 400) {
            setTimeout(() => {
              this.messages.push({
                type: "xiaokui",
                mess: resp.data.message,
              });
              this.$nextTick(() => {
                const chatTop = document.getElementById("chat_top");
                chatTop.scrollTop = chatTop.scrollHeight;
              });
            }, 1000);
          } else {
            this.messages.push({
              type: "xiaokui",
              mess: "大模型又出问题了，请重新尝试",
            });
            this.$notify({
              title: "消息",
              message: resp.data.message,
              position: "bottom-right",
            });
          }
        })
        .catch((err) => {
          setTimeout(() => {
            // 消息发送后，滚动到最底部
            this.$nextTick(() => {
              const chatTop = document.getElementById("chat_top");
              chatTop.scrollTop = chatTop.scrollHeight;
            });
          }, 500);
          this.loading = false;
          this.messages.push({
            type: "xiaokui",
            mess: "大模型的输出格式又出问题了，请重新尝试",
          });
          this.$notify({
            title: "消息",
            message: "模型问题",
            position: "bottom-right",
          });
          console.log("失败：", err);
        });

      // 2. 清空输入框
      this.textarea = "";
    },
  },
  mounted() {
    this.$wow.init();
    this.$nextTick(() => {
      const chatTop = document.getElementById("chat_top");
      chatTop.scrollTop = chatTop.scrollHeight;
    });
  },
  computed: {
    times() {
      return (TotalTime) => {
        return TotalTime.toFixed(1);
      };
    },
  },
};
</script>

<style scoped>
/**整体css容器 */
#conter {
  position: absolute;
  margin-top: 20px;
  width: 100%;
  height: 90vh;
  padding-bottom: 30px;
}

/**整个聊天容器 */
#chat_conter {
  position: relative;
  width: 85%;
  height: 90vh;
  left: 0;
  right: 0;
  padding: 20px;
  margin: 0 auto;
}

/**上面聊天容器 */
#chat_top {
  display: flex;
  flex-direction: column;
  height: 70vh;
  padding: 10px;
  background-image: url("../../../public/imgs/sister_background.jpg");
  background-size: 100% 100%;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: rgba(
    176,
    141,
    52,
    0.537
  ); /* 最后一位是透明度，0.1-1 调整 */
  background-blend-mode: overlay; /* 背景图与背景色叠加，增强透明效果 */
}

/**小葵的聊天框 */
.xiaokui {
  width: 48%;
  padding: 8px 12px;
  margin: 4px 0;
}

/**用户的聊天框 */
.myuser {
  align-self: flex-end; /* 单个子元素靠右对齐 */
  color: rgb(63, 58, 58);
  padding: 8px 12px;
  width: 43%;
  margin: 4px 0;
  align-items: flex-start;
  margin: 4px 0;
}

/**用户头像 */
.user_touxiang {
  right: 0;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: aliceblue;
  background-image: url("../../../public/imgs/touxiang.jpg");
  background-size: 100%;
}

/**小葵头像 */
.xiaokui_touxiang {
  right: 0;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: aliceblue;
  background-image: url("../../../public/imgs/ai_helper.png");
  background-size: 100%;
}

/**用户聊天 */
.user_liao {
  padding: 20px;
  margin-right: 15px;
  border-radius: 8px;
  background-color: #aba5a5;
  color: #252525;
  word-wrap: break-word;
  word-break: break-all;
  max-width: 70%;
  min-width: 120px;
  margin-left: auto; /* 用户消息居右 */
}

/**小葵聊天 */
.xiaokui_liao {
  padding: 20px;
  margin-left: 15px;
  border-radius: 8px;
  background-color: pink;
  width: auto; /* 改为自动宽度 */
  min-width: 120px; /* 短消息时的最小宽度 */
  max-width: 70%; /* 长消息时的最大宽度 */
}

/**输入容器 */
#bottom_conter {
  display: flex;
  flex-direction: column;
  padding-top: 20px;
  padding-bottom: 100px;
}

/**底部按钮 */
.bottom_btn {
  position: relative;
  align-self: flex-end;
}

/**陈小葵的推荐卡片 */
.card {
  display: block;
  width: 48%;
  padding: 8px 12px;
  margin: 4px 0;
  margin-left: 75px;
  width: 25%;
}

/**卡片容器 */
.card_conter {
  width: 100%;
}
.card_conter:hover .box_card {
  z-index: 999999;
  position: relative;
  left: 20%;
  animation: infinite;
  transition: 1s;
}

/* 给目标元素（.box_card）直接添加过渡，确保动画生效 */
.card_conter.box_card {
  transition: transform 1s; /* 1秒完成动画（时长越长越慢，比如2s就是2秒） */
}

/**卡片 */
.box_card {
  width: 60%;
  background-color: aliceblue;
  display: flex;
  padding: 40px;
  border-radius: 20px;
  border: solid 2px;
  flex-direction: column;
  margin-top: 50px;
}

/**卡片移动 */
.box_card:hover {
  cursor: pointer;
}

/**卡片的每一段 */
.card_p {
  display: flex;
  padding-top: 8px;
  padding-bottom: 7px;
}

/**卡片的左边 */
.card_p_left {
  margin-right: 20px;
}

/* 禁用状态样式 */
.box_card.disabled {
  cursor: not-allowed; /* 禁用指针（箭头变斜杠） */
  opacity: 0.6; /* 透明度降低，视觉上禁用 */
  pointer-events: none; /* 额外防止点击（双重保险） */
}

/**小葵答案回答框 */
.xiaokui_liao.answer {
  width: 90%;
  display: flex;
  flex-direction: column;
}

/**小葵回答段落 */
.answer_p {
  display: flex;
  padding-top: 8px;
  padding-bottom: 7px;
}

/**小葵回答的左侧 */
.answer_p_left {
  padding-right: 15px;
  font-size: 17px;
}

/**小葵回答的右侧 */
.answer_p_right {
  white-space: pre-line; /* 识别 \n 换行，多余空格会合并 */
  line-height: 1.6; /* 可选：增加行高，更易读 */
}

/**小葵回答的食物问题之名称 */
#food_name {
  position: relative;
  left: 0;
  right: 0;
  margin: 0 auto;
  text-align: center;
  padding-bottom: 20px;
  font-size: 18px;
}

/**小葵回答的食物问题之成分 */
.answer_p_right.ingredients {
  position: relative;
  left: 0;
  right: 0;
  margin: 0 auto;
}
</style>
