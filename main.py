import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import random
import requests
import json
import time
# 导入配置文件
from config import DOUBAO_API_KEY, DEFAULT_CARD_STYLE, CARD_SIZE_MAP


class IdealDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("理想桌面大师复刻版")
        self.root.geometry("1200x800")

        # 存储所有卡片
        self.cards = []
        # 拖动相关变量
        self.dragging_card = None
        self.drag_start_x = 0
        self.drag_start_y = 0

        # 1. 顶部输入区
        input_frame = tk.Frame(root, padx=10, pady=10)
        input_frame.pack(fill=tk.X)

        self.input_entry = tk.Entry(input_frame, font=("黑体", 12), width=60)
        self.input_entry.pack(side=tk.LEFT, padx=5)

        generate_btn = tk.Button(input_frame, text="生成卡片", font=("黑体", 12),
                                 command=self.generate_card_by_ai)
        generate_btn.pack(side=tk.LEFT, padx=5)

        # 2. 右侧桌面区
        self.desktop_frame = tk.Canvas(root, bg="#f5f5f5")
        self.desktop_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 绑定鼠标拖动事件
        self.root.bind("<ButtonPress-1>", self.on_card_press)
        self.root.bind("<B1-Motion>", self.on_card_drag)
        self.root.bind("<ButtonRelease-1>", self.on_card_release)

    # ========== 核心：AI调用函数 ==========
    def call_doubao_ai(self, prompt):
        """调用豆包API，生成结构化的卡片配置（使用火山引擎ARK认证）"""
        if not DOUBAO_API_KEY:
            messagebox.showerror("错误", "未配置豆包API密钥！\n请在config.py中设置DOUBAO_API_KEY。")
            return None

        # 火山引擎ARK平台的对话接口（无需单独获取Token，直接使用API Key作为Bearer Token）
        chat_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {DOUBAO_API_KEY}",  # 直接使用API Key作为Token
            "Content-Type": "application/json"
        }

        system_prompt = f"""
        你是一个桌面卡片生成助手，仅输出JSON格式的卡片配置，不要任何其他文字！
        配置规则：
        1. type：卡片类型，仅可选static（静态）/dynamic_time（实时时间）/dynamic_weather（实时天气）/todo（待办）；
        2. title：卡片名称（根据用户需求生成，比如“实时时间卡”）；
        3. size：尺寸，仅可选small/medium/large；
        4. style：{{"bg_color": 背景色（#ffffff/#eeeeee/#cceeff）, "font": 字体（黑体/宋体）}}；
        5. content：卡片内容（静态卡片填文字，其他填空字符串）。

        示例：
        用户输入：做一个中等尺寸的实时时间卡片，浅灰色背景
        输出：{{"type":"dynamic_time","title":"实时时间卡","size":"medium","style":{{"bg_color":"#eeeeee","font":"黑体"}},"content":""}}
        """

        chat_data = {
            "model": "doubao-pro-32k-250116",  # 使用ARK平台支持的模型ID
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "stream": False
        }

        try:
            response = requests.post(chat_url, headers=headers, json=chat_data, timeout=15)
            response.raise_for_status()
            result = response.json()
            card_config = json.loads(result["choices"][0]["message"]["content"])
            return card_config
        except json.JSONDecodeError:
            messagebox.showerror("AI返回错误", f"AI返回内容：{response.text}\n请简化需求重试！")
            return None
        except Exception as e:
            messagebox.showerror("AI调用失败",
                                 f"错误：{str(e)}\n响应内容：{response.text if 'response' in locals() else '无响应'}")
            return None

    # ========== 需求澄清逻辑 ==========
    def clarify_prompt(self, prompt):
        """判断需求是否模糊，若模糊则追问用户"""
        # 模糊关键词列表（可根据需要扩展）
        vague_keywords = ["实用的卡片", "做一个卡片", "卡片", "随便", "都行", "什么都行"]
        if any(keyword in prompt for keyword in vague_keywords):
            clarify_text = simpledialog.askstring(
                "需求澄清",
                "你的描述有点模糊～请补充说明：\n比如“实时天气卡”“待办事项卡”“实时时间卡”"
            )
            if clarify_text:
                return f"{prompt} {clarify_text}"  # 补充后的需求
            else:
                return None  # 用户取消澄清
        return prompt  # 需求清晰，直接返回

    # ========== 生成卡片（整合AI+澄清） ==========
    def generate_card_by_ai(self):
        """AI生成卡片的主函数"""
        # 1. 获取输入框需求
        prompt = self.input_entry.get().strip()
        if not prompt:
            messagebox.showwarning("提示", "请输入卡片需求！")
            return

        # 2. 需求澄清
        clarified_prompt = self.clarify_prompt(prompt)
        if not clarified_prompt:
            return  # 用户取消澄清

        # 3. 调用AI生成配置
        card_config = self.call_doubao_ai(clarified_prompt)
        if not card_config:
            return

        # 4. 根据配置生成对应卡片
        self.create_card_by_config(card_config)

        # 5. 清空输入框
        self.input_entry.delete(0, tk.END)

    # ========== 根据AI配置创建卡片 ==========
    def create_card_by_config(self, config):
        """根据AI生成的配置创建不同类型的卡片"""
        # 提取配置（默认值兜底，防止AI返回缺失字段）
        card_type = config.get("type", "static")
        title = config.get("title", "未命名卡片")
        size = config.get("size", "medium")
        style = config.get("style", DEFAULT_CARD_STYLE)
        content = config.get("content", title)

        # 卡片尺寸和初始位置
        card_width, card_height = CARD_SIZE_MAP[size]
        card_x = random.randint(200, 1000)
        card_y = random.randint(50, 600)

        # 创建卡片窗口
        card = tk.Toplevel(self.root)
        card.title(title)
        card.geometry(f"{card_width}x{card_height}+{card_x}+{card_y}")
        card.resizable(False, False)
        card.configure(bg=style["bg_color"])

        # 添加删除按钮
        delete_btn = ttk.Button(card, text="×", command=lambda: self.delete_card(card), width=2)
        delete_btn.pack(side=tk.RIGHT, anchor=tk.N)

        # 添加尺寸切换按钮
        size_frame = ttk.Frame(card)
        size_frame.pack(side=tk.LEFT, anchor=tk.N, padx=5)

        def change_size(new_size):
            w, h = CARD_SIZE_MAP[new_size]
            card.geometry(f"{w}x{h}+{card.winfo_x()}+{card.winfo_y()}")
            # 更新卡片列表中的尺寸
            for c in self.cards:
                if c["obj"] == card:
                    c["size"] = new_size
                    break

        ttk.Button(size_frame, text="小", command=lambda: change_size("small"), width=3).pack(side=tk.LEFT)
        ttk.Button(size_frame, text="中", command=lambda: change_size("medium"), width=3).pack(side=tk.LEFT)
        ttk.Button(size_frame, text="大", command=lambda: change_size("large"), width=3).pack(side=tk.LEFT)

        # 根据卡片类型创建内容
        if card_type == "static":
            # 静态卡片
            content_label = tk.Label(
                card, text=content, font=(style["font"], 12),
                bg=style["bg_color"], wraplength=card_width - 20
            )
            content_label.pack(expand=True, pady=20)
        elif card_type == "dynamic_time":
            # 实时时间卡片（每秒刷新）
            time_label = tk.Label(
                card, font=(style["font"], 20), bg=style["bg_color"]
            )
            time_label.pack(expand=True)

            def update_time():
                current_time = time.strftime("%H:%M:%S")
                current_date = time.strftime("%Y-%m-%d")
                time_label.config(text=f"{current_date}\n{current_time}")
                card.after(1000, update_time)  # 每秒刷新

            update_time()

        # 后续可扩展：dynamic_weather（天气）、todo（待办）

        # 保存卡片信息到列表
        self.cards.append({
            "obj": card,
            "title": title,
            "x": card_x,
            "y": card_y,
            "size": size,
            "type": card_type,
            "style": style
        })

    # ========== 原有功能：删除卡片 + 拖动 ==========
    def delete_card(self, card):
        card.destroy()
        self.cards = [c for c in self.cards if c["obj"] != card]

    def on_card_press(self, event):
        for card_info in self.cards:
            card = card_info["obj"]
            card_x = card.winfo_x()
            card_y = card.winfo_y()
            card_w = card.winfo_width()
            card_h = card.winfo_height()
            if (card_x <= event.x_root <= card_x + card_w) and (card_y <= event.y_root <= card_y + card_h):
                self.dragging_card = card_info
                self.drag_start_x = event.x_root - card_x
                self.drag_start_y = event.y_root - card_y
                card.lift()
                break

    def on_card_drag(self, event):
        if self.dragging_card:
            card = self.dragging_card["obj"]
            new_x = event.x_root - self.drag_start_x
            new_y = event.y_root - self.drag_start_y
            card.geometry(f"+{new_x}+{new_y}")
            self.dragging_card["x"] = new_x
            self.dragging_card["y"] = new_y

    def on_card_release(self, event):
        self.dragging_card = None


# 程序入口
if __name__ == "__main__":
    # 安装依赖（首次运行可取消注释，自动安装）
    # import subprocess
    # subprocess.check_call(["pip", "install", "requests"])
    root = tk.Tk()
    app = IdealDesktop(root)
    root.mainloop()