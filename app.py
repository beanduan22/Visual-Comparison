from flask import Flask, render_template, request, redirect, send_from_directory
import os
import csv
import random

app = Flask(__name__)

# 📌 设置图片路径
BASE_DIR = "vc"  # 存放所有图片
MNIST_DIR = os.path.join(BASE_DIR, "mnist")
CIFAR_DIR = os.path.join(BASE_DIR, "cifar")
RESULTS_FILE = "results.csv"
EMAILS_FILE = "emails.txt"  # 存储已提交的邮箱，防止重复提交


# 📌 读取所有图片（原始 + 对抗）
def load_images(dataset_dir):
    original = sorted(os.listdir(os.path.join(dataset_dir, "original")))  # 0-9 原始图片
    adversarial_methods = [d for d in os.listdir(dataset_dir) if d != "original"]

    images = []
    for label in original:  # 遍历 0-9
        adversarial_images = []
        for method in adversarial_methods:
            path = os.path.join(dataset_dir, method, label)
            if os.path.exists(path):
                adversarial_images.append((method, path))

        random.shuffle(adversarial_images)  # 🔀 打乱不同方法的对抗样本顺序
        images.append({
            "original": os.path.join(dataset_dir, "original", label),  # 显示名称
            "adversarial": adversarial_images  # 只存路径，不显示名称
        })

    return images


# 📌 载入 MNIST 和 CIFAR 图片
mnist_images = load_images(MNIST_DIR)
cifar_images = load_images(CIFAR_DIR)


# 📌 让 Flask 提供 `vc/mnist/` 和 `vc/cifar/` 里的图片
@app.route("/vc/<dataset>/<method>/<filename>")
def serve_image(dataset, method, filename):
    folder_path = os.path.join(BASE_DIR, dataset, method)
    return send_from_directory(folder_path, filename)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 📌 获取邮箱
        email = request.form.get("email").strip()
        if not email:
            return "❌ 请输入邮箱！", 400  # 前端必须填写邮箱

        # 📌 检查是否已提交过
        if os.path.exists(EMAILS_FILE):
            with open(EMAILS_FILE, "r") as f:
                emails = f.read().splitlines()
                if email in emails:
                    return "❌ 你已经提交过投票！", 400

        # 📌 记录邮箱，防止重复提交
        with open(EMAILS_FILE, "a") as f:
            f.write(email + "\n")

        # 📌 获取用户提交的数据
        data = request.form.to_dict(flat=False)

        # 📌 处理数据，转换为 CSV 格式
        with open(RESULTS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            for key, values in data.items():
                writer.writerow([email, key] + values)  # 存储邮箱 & 投票数据

        return redirect("/")

    return render_template("index.html", mnist_images=mnist_images, cifar_images=cifar_images)


if __name__ == "__main__":
    app.run(debug=True)
