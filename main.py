# 导入需要的库（在文件最顶部补充）
import tkinter as tk
from tkinter import messagebox, ttk  # 新增ttk（美化按钮）
import random  # 用于随机分配卡片初始位置，避免重叠


# 定义主程序类
class IdealDesktop:
    def __init__(self, root):
        # 原有的初始化代码（不变）
        self.root = root
        self.root.title("理想桌面大师复刻版")
        self.root.geometry("1200x800")

        # 新增：存储所有卡片的列表（后续管理卡片用）
        self.cards = []

        # 1. 顶部输入区（原代码不变）
        input_frame = tk.Frame(root, padx=10, pady=10)
        input_frame.pack(fill=tk.X)

        self.input_entry = tk.Entry(input_frame, font=("黑体", 12), width=60)
        self.input_entry.pack(side=tk.LEFT, padx=5)

        generate_btn = tk.Button(input_frame, text="生成卡片", font=("黑体", 12),
                                 command=self.generate_card)
        generate_btn.pack(side=tk.LEFT, padx=5)

        # 2. 右侧桌面区（原代码不变）
        self.desktop_frame = tk.Canvas(root, bg="#f5f5f5")
        self.desktop_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # ========== 新增：创建静态卡片的函数 ==========
    def create_static_card(self, card_title):
        """
        创建静态卡片
        :param card_title: 卡片标题（来自输入框的需求）
        """
        # 1. 卡片尺寸（3档固定，新手易实现）
        size_map = {
            "small": (150, 100),
            "medium": (200, 150),  # 默认中等尺寸
            "large": (300, 200)
        }
        card_width, card_height = size_map["medium"]

        # 2. 卡片初始位置（随机分配，避免重叠）
        # 桌面区的范围：x从200到1000，y从50到600
        card_x = random.randint(200, 1000)
        card_y = random.randint(50, 600)

        # 3. 创建卡片窗口（独立的悬浮窗口）
        card = tk.Toplevel(self.root)  # 基于主窗口创建子窗口
        card.title(card_title)  # 卡片标题=输入的需求
        card.geometry(f"{card_width}x{card_height}+{card_x}+{card_y}")  # 尺寸+位置
        card.resizable(False, False)  # 固定尺寸，不能拉伸
        card.configure(bg="#ffffff")  # 卡片背景色（白色）

        # 4. 添加删除按钮（卡片右上角）
        delete_btn = ttk.Button(card, text="×", command=lambda: self.delete_card(card), width=2)
        delete_btn.pack(side=tk.RIGHT, anchor=tk.N)  # 靠右、靠上

        # 5. 添加卡片标题标签（居中显示）
        title_label = tk.Label(
            card,
            text=card_title,
            font=("黑体", 12),
            bg="#ffffff",
            wraplength=card_width - 20  # 文字换行，避免超出卡片
        )
        title_label.pack(expand=True, pady=20)  # 居中显示

        # 6. 把卡片信息存入列表（后续管理用）
        self.cards.append({
            "obj": card,
            "title": card_title,
            "x": card_x,
            "y": card_y,
            "size": "medium",
            "type": "static"
        })

    # ========== 新增：删除卡片的函数 ==========
    def delete_card(self, card):
        """删除指定卡片"""
        card.destroy()  # 关闭卡片窗口
        # 从卡片列表中移除该卡片（避免残留）
        self.cards = [c for c in self.cards if c["obj"] != card]

    # ========== 修改原有的generate_card函数 ==========
    def generate_card(self):
        # 获取输入框的文字
        prompt = self.input_entry.get().strip()
        if not prompt:
            messagebox.showwarning("提示", "请输入卡片需求！")
            return

        # 替换原来的弹窗，改为创建静态卡片
        self.create_static_card(prompt)

        # 清空输入框
        self.input_entry.delete(0, tk.END)


# 程序入口（原代码不变）
if __name__ == "__main__":
    root = tk.Tk()
    app = IdealDesktop(root)
    root.mainloop()