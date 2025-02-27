from flask import Flask, abort, render_template, request, redirect, send_from_directory, send_file
import os
import csv
import random

app = Flask(__name__)

# 📌 设置图片路径
BASE_DIR = "vc"  # 存放所有图片
MNIST_DIR = os.path.join(BASE_DIR, "mnist")
CIFAR_DIR = os.path.join(BASE_DIR, "cifar")
RESULTS_FILE = os.path.join(os.getcwd(), "results.csv")  # 存储投票结果（完整路径）


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

# 确保至少有 20 组数据
while len(mnist_images) < 20:
    mnist_images.append({"original": "", "adversarial": []})

while len(cifar_images) < 20:
    cifar_images.append({"original": "", "adversarial": []})


# 📌 提供 `vc/mnist/` 和 `vc/cifar/` 里的图片
@app.route("/vc/<dataset>/<method>/<filename>")
def serve_image(dataset, method, filename):
    folder_path = os.path.join(BASE_DIR, dataset, method)
    return send_from_directory(folder_path, filename)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 📌 获取用户提交的数据
        data = request.form.to_dict(flat=False)

        print("Received Data:", data)  # ✅ 调试信息，查看表单数据是否正确

        try:
            # 📌 追加写入 CSV 文件
            with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for key, values in data.items():
                    writer.writerow([key] + values)  # 直接存储投票数据

                f.flush()  # ✅ 确保数据立即写入
                os.fsync(f.fileno())  # ✅ 确保写入磁盘

            print(f"Data successfully written to {RESULTS_FILE}")  # ✅ 确认写入成功
        except Exception as e:
            print("Error writing to CSV:", str(e))  # ✅ 调试信息，打印错误

        return redirect("/")

    return render_template("index.html", mnist_images=mnist_images, cifar_images=cifar_images)


@app.route("/download")
def download_results():
    if not os.path.exists(RESULTS_FILE):
        return abort(404, description="Results file not found.")

    return send_file(RESULTS_FILE, as_attachment=True, mimetype="text/csv", download_name="results.csv")


if __name__ == "__main__":
    app.run(debug=True)
